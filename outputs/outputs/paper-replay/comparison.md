| Method | State / action | Sweep / pass / update | Paper result | Program result | Difference | Explanation |
| --- | --- | --- | --- | --- | --- | --- |
| Model-based | A | V1 | -0.33300 | -0.333333 | -0.000333 | rounding (-1/3 written as -0.333) |
| Model-based | B | V1 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Model-based | C | V1 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Model-based | D | V1 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Model-based | E | V1 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Model-based | A | V2 | -0.33300 | -0.333333 | -0.000333 | rounding (-1/3 written as -0.333) |
| Model-based | B | V2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Model-based | C | V2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Model-based | D | V2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Model-based | E | V2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Monte Carlo | A | final | -0.33300 | -0.333333 | -0.000333 | rounding (-1/3 written as -0.333) |
| Monte Carlo | B | final | 0.00000 | 0.000000 | +0.000000 | exact match |
| Monte Carlo | C | final | 0.00000 | 0.000000 | +0.000000 | exact match |
| Monte Carlo | D | final | 0.00000 | 0.000000 | +0.000000 | exact match |
| Monte Carlo | E | final | 0.00000 | 0.000000 | +0.000000 | exact match |
| TD(0) | A | after pass 1 | -0.08000 | -0.080000 | +0.000000 | exact match |
| TD(0) | B | after pass 1 | -0.01000 | -0.010000 | -0.000000 | exact match |
| TD(0) | C | after pass 1 | 0.00000 | 0.000000 | +0.000000 | exact match |
| TD(0) | D | after pass 1 | 0.00000 | 0.000000 | +0.000000 | exact match |
| TD(0) | E | after pass 1 | 0.00000 | 0.000000 | +0.000000 | exact match |
| TD(0) | A | after pass 2 | -0.14003 | -0.140030 | -0.000000 | exact match |
| TD(0) | B | after pass 2 | -0.01810 | -0.018100 | -0.000000 | exact match |
| TD(0) | C | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| TD(0) | D | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| TD(0) | E | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Q-learning | A,stick | after pass 1 | not written | 0.000000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | A,hit | after pass 1 | not written | -0.080000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | B,stick | after pass 1 | not written | -0.010000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | B,hit | after pass 1 | not written | 0.000000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | C,stick | after pass 1 | not written | 0.000000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | C,hit | after pass 1 | not written | 0.000000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | D,stick | after pass 1 | not written | 0.000000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | D,hit | after pass 1 | not written | 0.000000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | E,stick | after pass 1 | not written | 0.000000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | E,hit | after pass 1 | not written | 0.000000 | — | Target/New left blank on paper; program value fills the gap |
| Q-learning | A,stick | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Q-learning | A,hit | after pass 2 | -0.13922 | -0.139220 | +0.000000 | exact match |
| Q-learning | B,stick | after pass 2 | -0.01810 | -0.018100 | -0.000000 | exact match |
| Q-learning | B,hit | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Q-learning | C,stick | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Q-learning | C,hit | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Q-learning | D,stick | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Q-learning | D,hit | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Q-learning | E,stick | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
| Q-learning | E,hit | after pass 2 | 0.00000 | 0.000000 | +0.000000 | exact match |
