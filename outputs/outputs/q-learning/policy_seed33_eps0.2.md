# Greedy policy, training seed 33, epsilon 0.2

H = hit, S = stick, T = tie, . = never visited


## No usable ace

| sum \ dealer | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 4 | H | H | H | H | H | S | H | H | H | H |
| 5 | H | H | S | H | H | H | H | H | H | H |
| 6 | H | H | S | H | H | H | H | H | H | H |
| 7 | H | H | H | H | S | H | H | H | H | H |
| 8 | H | H | H | H | H | H | H | H | H | H |
| 9 | H | H | S | H | H | H | H | H | H | H |
| 10 | H | H | H | H | H | S | H | H | H | H |
| 11 | H | H | H | H | H | H | H | H | H | H |
| 12 | H | H | S | H | H | S | H | H | H | S |
| 13 | H | H | S | H | S | H | H | H | H | H |
| 14 | H | H | H | H | H | H | H | H | H | S |
| 15 | H | H | H | S | S | S | H | H | H | H |
| 16 | H | S | H | S | S | H | H | S | H | S |
| 17 | H | S | S | S | S | S | S | S | S | H |
| 18 | S | S | S | S | S | S | S | S | S | S |
| 19 | S | S | S | S | S | S | S | S | S | S |
| 20 | S | S | S | S | S | S | S | S | S | S |
| 21 | S | S | S | S | S | S | S | S | S | S |

## Usable ace

| sum \ dealer | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 12 | H | H | S | H | H | H | H | H | H | H |
| 13 | H | H | H | H | H | H | H | H | H | H |
| 14 | H | H | H | H | H | H | H | H | H | H |
| 15 | H | H | H | H | H | H | H | S | H | H |
| 16 | H | H | H | H | H | H | H | H | H | H |
| 17 | H | H | H | H | H | S | H | H | H | H |
| 18 | S | S | H | S | H | H | H | H | H | S |
| 19 | S | H | S | H | S | S | S | S | S | H |
| 20 | S | S | S | S | S | S | S | S | S | S |
| 21 | S | S | S | S | S | S | S | S | S | S |
