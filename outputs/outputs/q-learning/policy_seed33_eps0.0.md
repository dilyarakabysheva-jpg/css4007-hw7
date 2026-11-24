# Greedy policy, training seed 33, epsilon 0.0

H = hit, S = stick, T = tie, . = never visited


## No usable ace

| sum \ dealer | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 4 | H | H | H | H | H | H | H | S | H | H |
| 5 | H | H | H | H | H | H | H | H | H | H |
| 6 | H | S | H | H | H | H | S | H | H | H |
| 7 | H | H | H | H | H | H | H | H | H | H |
| 8 | H | H | H | H | H | H | H | H | H | H |
| 9 | H | H | H | H | H | H | H | H | H | H |
| 10 | H | H | H | H | H | H | H | H | H | H |
| 11 | H | H | H | H | H | H | H | H | H | H |
| 12 | H | H | H | H | H | S | H | H | H | H |
| 13 | H | H | H | S | H | H | H | H | H | H |
| 14 | H | S | H | S | H | S | H | H | H | H |
| 15 | H | H | S | H | S | H | H | H | H | H |
| 16 | H | H | S | H | H | S | S | H | S | H |
| 17 | S | S | S | S | S | S | S | S | S | S |
| 18 | S | S | S | S | S | S | S | S | S | S |
| 19 | S | S | S | S | S | S | S | S | S | S |
| 20 | S | S | S | S | S | S | S | S | S | S |
| 21 | S | S | S | S | S | S | S | S | S | S |

## Usable ace

| sum \ dealer | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 12 | H | H | H | H | H | H | H | H | H | H |
| 13 | H | H | H | H | H | H | H | H | H | H |
| 14 | H | H | H | H | H | H | H | S | H | H |
| 15 | H | H | H | H | H | H | H | H | S | H |
| 16 | H | H | H | H | H | H | H | H | H | H |
| 17 | S | H | H | H | H | H | H | S | H | H |
| 18 | S | H | H | S | S | H | H | S | H | H |
| 19 | H | H | S | H | H | S | S | S | S | S |
| 20 | S | H | H | S | S | S | S | S | S | S |
| 21 | S | S | S | S | S | S | S | S | S | S |
