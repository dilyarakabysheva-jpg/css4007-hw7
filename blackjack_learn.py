"""HW7 Part D: learn Blackjack from simulated games (Gymnasium Blackjack-v1).

Run:  python blackjack_learn.py
Writes everything into outputs/fixed-policy/ and outputs/q-learning/.

Learners only see observations (player sum, dealer card, usable ace),
actions, rewards and next observations. They never read hidden cards.
"""
import csv
import random
from collections import defaultdict
from pathlib import Path

import gymnasium as gym

ROOT = Path(__file__).parent
OUT_FP = ROOT / "outputs" / "fixed-policy"
OUT_Q = ROOT / "outputs" / "q-learning"
OUT_FP.mkdir(parents=True, exist_ok=True)
OUT_Q.mkdir(parents=True, exist_ok=True)

STICK, HIT = 0, 1
ACTIONS = (STICK, HIT)
END = "END"
GAMMA, ALPHA = 1.0, 0.1
MAX_ACTIONS = 100                      # safety limit per game
SEEDS = [11, 22, 33]
EVAL_SEEDS = {11: 1011, 22: 1022, 33: 1033}
FP_GAMES = 10_000
CHECKPOINTS = [100, 1_000, 10_000]
Q_GAMES = 50_000
EVAL_GAMES = 10_000
EPSILONS = [0.2, 0.0]
TOL, MAX_SWEEPS = 1e-6, 10_000


def make_env():
    return gym.make("Blackjack-v1", natural=False, sab=False)


def obs_key(obs):
    return (int(obs[0]), int(obs[1]), int(obs[2]))


def fixed_policy(state):
    """Baseline: hit below 20, stick at 20 or 21."""
    return HIT if state[0] < 20 else STICK


# ======================================================================
# Part D.1 - collect fixed-policy games once, feed the same games to all
# ======================================================================
def collect_fixed_games(seed):
    """Returns list of games; each game is a list of (s, a, r, s2, done)."""
    env = make_env()
    games, log, cutoffs = [], [], 0
    for g in range(FP_GAMES):
        obs, _ = env.reset(seed=seed) if g == 0 else env.reset()
        s = obs_key(obs)
        game = []
        for step in range(1, MAX_ACTIONS + 1):
            a = fixed_policy(s)
            obs2, r, term, trunc, _ = env.step(a)
            done = term or trunc
            s2 = END if done else obs_key(obs2)       # terminal -> END
            game.append((s, a, float(r), s2, done))
            log.append([seed, g + 1, step, s, a, r, s2 if s2 == END else obs_key(obs2), done])
            s = s2
            if done:
                break
        else:
            cutoffs += 1                              # never ended: not a complete game
            continue
        games.append(game)
    env.close()
    with open(OUT_FP / f"games_seed{seed}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seed", "game", "step", "player_sum", "dealer_showing", "usable_ace",
                    "action", "reward", "next_observation", "terminal"])
        for seed_, g, st, s, a, r, s2, d in log:
            w.writerow([seed_, g, st, s[0], s[1], s[2], a, r,
                        "END" if s2 == END else f"{s2[0]}-{s2[1]}-{s2[2]}", d])
    return games, cutoffs


class ModelBased:
    def __init__(self):
        self.n_sa = defaultdict(int)
        self.n_sas = defaultdict(int)
        self.r_sum = defaultdict(float)
        self.visits = defaultdict(int)

    def observe(self, game):
        for s, a, r, s2, _ in game:
            self.visits[s] += 1
            self.n_sa[(s, a)] += 1
            self.n_sas[(s, a, s2)] += 1
            self.r_sum[(s, a, s2)] += r

    def evaluate(self):
        """Policy evaluation of the fixed policy on the learned model.
        States whose policy action was never observed get no estimate (None).
        A successor without an estimate is a 'missing successor'."""
        model = defaultdict(list)
        for (s, a, s2), n in self.n_sas.items():
            model[(s, a)].append((n / self.n_sa[(s, a)], s2, self.r_sum[(s, a, s2)] / n))
        states = [s for s in self.visits if (s, fixed_policy(s)) in model]
        V = {s: 0.0 for s in states}
        missing_succ = set()
        for sweep in range(1, MAX_SWEEPS + 1):
            newV, delta = {}, 0.0
            for s in states:
                total = 0.0
                for p, s2, r in model[(s, fixed_policy(s))]:
                    if s2 == END:
                        nxt = 0.0
                    elif s2 in V:
                        nxt = V[s2]
                    else:
                        nxt = 0.0
                        missing_succ.add(s)
                    total += p * (r + GAMMA * nxt)
                newV[s] = total
                delta = max(delta, abs(total - V[s]))
            V = newV
            if delta < TOL:
                return V, sweep, delta, True, missing_succ
        return V, MAX_SWEEPS, delta, False, missing_succ


class MonteCarlo:
    def __init__(self):
        self.total = defaultdict(float)
        self.visits = defaultdict(int)

    def observe(self, game):
        G = 0.0
        for s, a, r, s2, _ in reversed(game):     # every-visit returns
            G = r + GAMMA * G
            self.total[s] += G
            self.visits[s] += 1

    def values(self):
        return {s: self.total[s] / n for s, n in self.visits.items()}


class TD0:
    def __init__(self):
        self.V = {}
        self.visits = defaultdict(int)

    def observe(self, game):
        for s, a, r, s2, done in game:
            nxt = 0.0 if (done or s2 == END) else self.V.get(s2, 0.0)
            old = self.V.get(s, 0.0)
            self.V[s] = old + ALPHA * (r + GAMMA * nxt - old)
            self.visits[s] += 1


def all_states():
    for ace in (0, 1):
        for p in range(4 if ace == 0 else 12, 22):
            for d in range(1, 11):
                yield (p, d, ace)


def value_table_md(title, values, visits, ace):
    lo = 4 if ace == 0 else 12
    rows = [f"**{title} — {'usable ace' if ace else 'no usable ace'}** "
            "(value / visits; `—` = no estimate)", "",
            "| sum \\ dealer | " + " | ".join(str(d) for d in range(1, 11)) + " |",
            "|---" * 11 + "|"]
    for p in range(lo, 22):
        cells = []
        for d in range(1, 11):
            s = (p, d, ace)
            v = values.get(s)
            cells.append("—" if v is None else f"{v:+.3f} / {visits.get(s, 0)}")
        rows.append(f"| {p} | " + " | ".join(cells) + " |")
    return "\n".join(rows) + "\n"


COMPARE_STATES = [(20, 10, 0), (13, 10, 0), (16, 10, 0), (19, 7, 0),   # frequent
                  (21, 1, 1), (12, 1, 1), (18, 2, 1), (4, 1, 0)]       # rare


def run_fixed_policy():
    est_rows, compare_rows, notes = [], [], []
    for seed in SEEDS:
        games, cutoffs = collect_fixed_games(seed)
        mb, mc, td = ModelBased(), MonteCarlo(), TD0()
        md = [f"# Fixed policy (hit below 20) — seed {seed}\n",
              f"Games: {FP_GAMES}, cut-offs: {cutoffs}\n"]
        for n, game in enumerate(games, 1):
            mb.observe(game)
            mc.observe(game)
            td.observe(game)
            if n in CHECKPOINTS:
                V_mb, sweeps, delta, conv, miss = mb.evaluate()
                V_mc, V_td = mc.values(), dict(td.V)
                notes.append(f"seed {seed}, {n} games: model-based sweeps={sweeps}, "
                             f"final change={delta:.2e}, converged={conv}, "
                             f"states with missing successor estimate={len(miss)}, "
                             f"states visited={len(mb.visits)}")
                for s in all_states():
                    est_rows.append([seed, n, *s, mb.visits.get(s, 0),
                                     "" if s not in V_mb else f"{V_mb[s]:.6f}",
                                     "" if s not in V_mc else f"{V_mc[s]:.6f}",
                                     "" if s not in V_td else f"{V_td[s]:.6f}",
                                     int(s in miss)])
                for s in COMPARE_STATES:
                    compare_rows.append([seed, n, s, mb.visits.get(s, 0),
                                         V_mb.get(s), V_mc.get(s), V_td.get(s)])
                if n == CHECKPOINTS[-1]:
                    for name, vals in [("Model-based", V_mb), ("Monte Carlo", V_mc), ("TD(0)", V_td)]:
                        md.append(f"\n## {name}, after {n} games\n")
                        for ace in (0, 1):
                            md.append(value_table_md(name, vals, mb.visits, ace))
        (OUT_FP / f"value_tables_seed{seed}.md").write_text("\n".join(md))

    with open(OUT_FP / "value_estimates.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seed", "games", "player_sum", "dealer_showing", "usable_ace", "visits",
                    "model_based", "monte_carlo", "td0", "missing_successor"])
        w.writerows(est_rows)

    fmt = lambda v: "—" if v is None else f"{v:+.3f}"
    lines = ["| Seed | Games | State (sum, dealer, ace) | Visits | Model-based | Monte Carlo | TD(0) |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for seed, n, s, vis, a, b, c in compare_rows:
        lines.append(f"| {seed} | {n} | {s} | {vis} | {fmt(a)} | {fmt(b)} | {fmt(c)} |")
    (OUT_FP / "compare_states.md").write_text("\n".join(lines) + "\n")
    (OUT_FP / "model_based_convergence.txt").write_text("\n".join(notes) + "\n")
    print("\n".join(notes))
    print("\n".join(lines))


# ======================================================================
# Part D.2 - Q-learning, frozen evaluation
# ======================================================================
def greedy(Q, s, rng):
    qs, qh = Q[(s, STICK)], Q[(s, HIT)]
    if qs == qh:
        return rng.choice(ACTIONS)        # random tie-break, seeded
    return STICK if qs > qh else HIT


def train_q(seed, eps):
    env = make_env()
    rng = random.Random(seed)             # seeded action generator (explore + ties)
    Q = defaultdict(float)
    N = defaultdict(int)
    game_rewards, cutoffs = [], 0
    for g in range(Q_GAMES):
        obs, _ = env.reset(seed=seed) if g == 0 else env.reset()
        s, total, finished = obs_key(obs), 0.0, False
        for _ in range(MAX_ACTIONS):
            if eps > 0 and rng.random() < eps:
                a = rng.choice(ACTIONS)
            else:
                a = greedy(Q, s, rng)
            obs2, r, term, trunc, _ = env.step(a)
            done = term or trunc
            s2 = END if done else obs_key(obs2)
            nxt = 0.0 if done else max(Q[(s2, STICK)], Q[(s2, HIT)])
            Q[(s, a)] += ALPHA * (r + GAMMA * nxt - Q[(s, a)])
            N[(s, a)] += 1
            total += r
            s = s2
            if done:
                finished = True
                break
        if finished:
            game_rewards.append(total)
        else:
            cutoffs += 1
    env.close()
    return Q, N, game_rewards, cutoffs


def evaluate(policy_fn, eval_seed):
    env = make_env()
    w = l = d = cut = 0
    total = 0.0
    for g in range(EVAL_GAMES):
        obs, _ = env.reset(seed=eval_seed) if g == 0 else env.reset()
        s = obs_key(obs)
        for _ in range(MAX_ACTIONS):
            obs2, r, term, trunc, _ = env.step(policy_fn(s))
            if term or trunc:
                total += r
                w += r > 0
                l += r < 0
                d += r == 0
                break
            s = obs_key(obs2)
        else:
            cut += 1
    env.close()
    done = EVAL_GAMES - cut
    return w, l, d, cut, total / done if done else float("nan")


def save_q(seed, eps, Q, N):
    tag = f"seed{seed}_eps{eps}"
    with open(OUT_Q / f"q_table_{tag}.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["player_sum", "dealer_showing", "usable_ace", "Q_stick", "Q_hit",
                     "N_stick", "N_hit", "greedy"])
        for s in all_states():
            ns, nh = N[(s, STICK)], N[(s, HIT)]
            if ns + nh == 0:
                g = "unvisited"
            elif Q[(s, STICK)] == Q[(s, HIT)]:
                g = "tie"
            else:
                g = "stick" if Q[(s, STICK)] > Q[(s, HIT)] else "hit"
            wr.writerow([*s, f"{Q[(s, STICK)]:.6f}", f"{Q[(s, HIT)]:.6f}", ns, nh, g])
    md = [f"# Greedy policy, training seed {seed}, epsilon {eps}\n",
          "H = hit, S = stick, T = tie, . = never visited\n"]
    for ace in (0, 1):
        lo = 4 if ace == 0 else 12
        md += [f"\n## {'Usable ace' if ace else 'No usable ace'}\n",
               "| sum \\ dealer | " + " | ".join(str(d) for d in range(1, 11)) + " |",
               "|---" * 11 + "|"]
        for p in range(lo, 22):
            cells = []
            for dlr in range(1, 11):
                s = (p, dlr, ace)
                if N[(s, STICK)] + N[(s, HIT)] == 0:
                    cells.append(".")
                elif Q[(s, STICK)] == Q[(s, HIT)]:
                    cells.append("T")
                else:
                    cells.append("S" if Q[(s, STICK)] > Q[(s, HIT)] else "H")
            md.append(f"| {p} | " + " | ".join(cells) + " |")
    (OUT_Q / f"policy_{tag}.md").write_text("\n".join(md) + "\n")


def plot_curves(curves, eval_means):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {11: "#2a78d6", 22: "#eb6834", 33: "#1baf7a"}   # fixed categorical order
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, eps in zip(axes, EPSILONS):
        for seed in SEEDS:
            ys = curves[(seed, eps)]
            xs = [(i + 1) for i in range(len(ys))]
            ax.plot(xs, ys, color=colors[seed], lw=2, label=f"training, seed {seed}")
            ax.plot([len(ys) + 3], [eval_means[(seed, eps)]], marker="o", ms=8,
                    color=colors[seed], markeredgecolor="white", markeredgewidth=2,
                    linestyle="none")
        base = sum(eval_means[(s, "baseline")] for s in SEEDS) / len(SEEDS)
        ax.axhline(base, color="#888888", lw=1.5, ls="--", label="baseline evaluation (mean of seeds)")
        ax.axvline(len(ys) + 1.5, color="#cccccc", lw=1)
        ax.set_title(f"Q-learning, epsilon = {eps}", fontsize=11)
        ax.set_xlabel("training block (1,000 games each)   |   dots = frozen greedy evaluation")
        ax.grid(axis="y", color="#e5e5e5", lw=0.8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[0].set_ylabel("mean reward per game")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=9, frameon=False, loc="lower center", ncol=4)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(OUT_Q / "training_curves.png", dpi=150)
    plt.close(fig)


def run_q_learning():
    results, curves, eval_means = [], {}, {}
    for seed in SEEDS:
        ev = EVAL_SEEDS[seed]
        w, l, d, c, m = evaluate(fixed_policy, ev)
        results.append([seed, "baseline (hit below 20)", ev, w, l, d, c, m])
        eval_means[(seed, "baseline")] = m
        for eps in EPSILONS:
            Q, N, rewards, cut = train_q(seed, eps)
            save_q(seed, eps, Q, N)
            blocks = [sum(rewards[i:i + 1000]) / len(rewards[i:i + 1000])
                      for i in range(0, len(rewards), 1000)]
            curves[(seed, eps)] = blocks
            with open(OUT_Q / f"training_blocks_seed{seed}_eps{eps}.csv", "w", newline="") as f:
                wr = csv.writer(f)
                wr.writerow(["block", "games", "mean_reward"])
                for i, b in enumerate(blocks, 1):
                    wr.writerow([i, f"{(i - 1) * 1000 + 1}-{i * 1000}", f"{b:.4f}"])
            frozen = dict(Q)
            tie_rng = random.Random(ev)
            pol = lambda s, Qf=frozen, r=tie_rng: greedy(defaultdict(float, Qf), s, r)
            w, l, d, c, m = evaluate(pol, ev)
            results.append([seed, f"Q-learning eps={eps} (training cut-offs {cut})", ev, w, l, d, c, m])
            eval_means[(seed, eps)] = m
            print(f"seed {seed} eps {eps}: train cut-offs {cut}, eval mean {m:+.4f}")

    lines = ["| Training seed | Policy / epsilon | Evaluation seed | Wins | Losses | Draws | Cut-offs | Mean reward |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in results:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]:+.4f} |")
    (OUT_Q / "evaluation.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    plot_curves(curves, eval_means)


if __name__ == "__main__":
    print("=== Fixed-policy evaluation ===")
    run_fixed_policy()
    print("\n=== Q-learning ===")
    run_q_learning()
    print("\nSaved outputs/fixed-policy/ and outputs/q-learning/")
