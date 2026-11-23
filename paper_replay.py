"""HW7 Part C: reproduce the paper calculations on the fixed histories.

Run:  python paper_replay.py
Reads data/paper-games.csv and data/states.csv (no Gymnasium needed).
Writes outputs/paper-replay/replay.txt and outputs/paper-replay/comparison.md
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "outputs" / "paper-replay"
OUT.mkdir(parents=True, exist_ok=True)

GAMMA, ALPHA = 1.0, 0.1
STICK, HIT = 0, 1
NAME = {STICK: "stick", HIT: "hit"}
END = "END"

# ---------------------------------------------------------------- data
states = {}
with open(ROOT / "data" / "states.csv") as f:
    for r in csv.DictReader(f):
        states[r["label"]] = (int(r["player_sum"]), int(r["dealer_showing"]), int(r["usable_ace"]))
LABELS = list(states)

games = defaultdict(list)
with open(ROOT / "data" / "paper-games.csv") as f:
    for r in csv.DictReader(f):
        games[int(r["game"])].append(
            (r["state"], int(r["action"]), r["next_state"], float(r["reward"]),
             r["terminated"].strip().lower() == "true"))
GAME_ORDER = sorted(games)


def policy(label):
    """Fixed policy: hit below 20, stick at 20 or 21."""
    return HIT if states[label][0] < 20 else STICK


lines = []
def say(text=""):
    print(text)
    lines.append(text)


# results[(method, item, step)] = value, used for the comparison table
results = {}

# ---------------------------------------------------------------- 1. model-based
say("=" * 70)
say("1. MODEL-BASED LEARNING")
say("=" * 70)
count_sa = defaultdict(int)
count_sas = defaultdict(int)
reward_sum = defaultdict(float)
for g in GAME_ORDER:
    for s, a, s2, r, _ in games[g]:
        count_sa[(s, a)] += 1
        count_sas[(s, a, s2)] += 1
        reward_sum[(s, a, s2)] += r

model = defaultdict(list)   # (s,a) -> [(p, s2, mean r)]
say("Counts, estimated probabilities and mean rewards:")
for (s, a, s2), n in sorted(count_sas.items()):
    p = n / count_sa[(s, a)]
    mr = reward_sum[(s, a, s2)] / n
    model[(s, a)].append((p, s2, mr))
    say(f"  ({s},{NAME[a]}) -> {s2}: N={n}/{count_sa[(s, a)]}, T={p:.6f}, R={mr:.6f}")
for s in LABELS:
    for a in (STICK, HIT):
        if (s, a) not in model:
            say(f"  ({s},{NAME[a]}): UNOBSERVED")

V = {s: 0.0 for s in LABELS}
V[END] = 0.0
for sweep in (1, 2):
    newV = {END: 0.0}
    say(f"\nSweep {sweep} (uses only sweep {sweep - 1} values, fixed policy):")
    for s in LABELS:
        a = policy(s)
        if (s, a) not in model:
            newV[s] = V[s]
            say(f"  V{sweep}({s}) policy action {NAME[a]} unobserved -> no estimate")
            continue
        parts = [f"{p:.4f}*({r:+.4f} + {V[s2]:.4f})" for p, s2, r in model[(s, a)]]
        newV[s] = sum(p * (r + GAMMA * V[s2]) for p, s2, r in model[(s, a)])
        say(f"  V{sweep}({s}) [{NAME[a]}] = {' + '.join(parts)} = {newV[s]:.6f}")
        results[("Model-based", s, f"V{sweep}")] = newV[s]
    V = newV

# ---------------------------------------------------------------- 2. Monte Carlo
say("\n" + "=" * 70)
say("2. DIRECT EVALUATION (every-visit Monte Carlo)")
say("=" * 70)
returns = defaultdict(list)
for g in GAME_ORDER:
    G = 0.0
    for s, a, s2, r, _ in reversed(games[g]):
        G = r + GAMMA * G
        returns[s].append((g, G))
for s in LABELS:
    rs = sorted(returns[s])
    vals = [G for _, G in rs]
    avg = sum(vals) / len(vals)
    say(f"  {s}: returns {[(f'game {g}', G) for g, G in rs]}, N={len(vals)}, V={avg:.6f}")
    results[("Monte Carlo", s, "final")] = avg

# ---------------------------------------------------------------- 3. TD(0)
say("\n" + "=" * 70)
say("3. TD(0), alpha=0.1, gamma=1.0, two passes")
say("=" * 70)
V = {s: 0.0 for s in LABELS}
for p in (1, 2):
    say(f"\nPass {p}:")
    for g in GAME_ORDER:
        for s, a, s2, r, term in games[g]:
            nxt = 0.0 if (term or s2 == END) else V[s2]
            target = r + GAMMA * nxt
            old = V[s]
            V[s] = old + ALPHA * (target - old)
            say(f"  game {g}: V({s}) old={old:.6f} r={r:+.0f} V(next={s2})={nxt:.6f} "
                f"target={target:.6f} new={V[s]:.6f}")
    for s in LABELS:
        results[("TD(0)", s, f"after pass {p}")] = V[s]
say("Final TD values: " + ", ".join(f"{s}={V[s]:.6f}" for s in LABELS))

# ---------------------------------------------------------------- 4. Q-learning
say("\n" + "=" * 70)
say("4. Q-LEARNING, alpha=0.1, gamma=1.0, two passes, fresh zero table")
say("=" * 70)
Q = {(s, a): 0.0 for s in LABELS for a in (STICK, HIT)}
for p in (1, 2):
    say(f"\nPass {p}:")
    for g in GAME_ORDER:
        for s, a, s2, r, term in games[g]:
            nxt = 0.0 if (term or s2 == END) else max(Q[(s2, STICK)], Q[(s2, HIT)])
            target = r + GAMMA * nxt
            old = Q[(s, a)]
            Q[(s, a)] = old + ALPHA * (target - old)
            say(f"  game {g}: Q({s},{NAME[a]}) old={old:.6f} r={r:+.0f} "
                f"maxQ(next={s2})={nxt:.6f} target={target:.6f} new={Q[(s, a)]:.6f}")
    for s in LABELS:
        for a in (STICK, HIT):
            results[("Q-learning", f"{s},{NAME[a]}", f"after pass {p}")] = Q[(s, a)]
say("\nFinal Q-table and greedy actions:")
for s in LABELS:
    qs, qh = Q[(s, STICK)], Q[(s, HIT)]
    greedy = "tie" if abs(qs - qh) < 1e-12 else ("stick" if qs > qh else "hit")
    say(f"  {s}: Q(stick)={qs:.6f}  Q(hit)={qh:.6f}  greedy={greedy}")

(OUT / "replay.txt").write_text("\n".join(lines) + "\n")

# ---------------------------------------------------------------- comparison
# Paper results copied from my handwritten pages (part_b_1/2/3.jpg).
# None = not written on paper (Q-learning pass 1 Target/New columns were left blank).
PAPER = {}
for st in "ABCDE":
    for k in ("V1", "V2"):
        PAPER[("Model-based", st, k)] = -0.333 if st == "A" else 0.0
    PAPER[("Monte Carlo", st, "final")] = -0.333 if st == "A" else 0.0
    PAPER[("TD(0)", st, "after pass 1")] = {"A": -0.08, "B": -0.01}.get(st, 0.0)
    PAPER[("TD(0)", st, "after pass 2")] = {"A": -0.14003, "B": -0.0181}.get(st, 0.0)
    for a in ("stick", "hit"):
        PAPER[("Q-learning", f"{st},{a}", "after pass 1")] = None
        PAPER[("Q-learning", f"{st},{a}", "after pass 2")] = {
            "A,hit": -0.13922, "B,stick": -0.0181}.get(f"{st},{a}", 0.0)

rows = ["| Method | State / action | Sweep / pass / update | Paper result | Program result | Difference | Explanation |",
        "| --- | --- | --- | --- | --- | --- | --- |"]
for key, prog in results.items():
    paper = PAPER.get(key)
    if paper is None:
        rows.append(f"| {key[0]} | {key[1]} | {key[2]} | not written | {prog:.6f} | — | "
                    "Target/New left blank on paper; program value fills the gap |")
        continue
    diff = prog - paper
    if abs(diff) < 1e-9:
        why = "exact match"
    elif abs(diff) < 1e-3:
        why = "rounding (-1/3 written as -0.333)"
    else:
        why = "CHECK: real discrepancy"
    rows.append(f"| {key[0]} | {key[1]} | {key[2]} | {paper:.5f} | {prog:.6f} | {diff:+.6f} | {why} |")
(OUT / "comparison.md").write_text("\n".join(rows) + "\n")
print("\n" + "\n".join(rows))
print("\nSaved outputs/paper-replay/replay.txt and comparison.md")
