# False blocks per hour and distinct benign hosts (final review M5)

Script: src/analysis/final_blocking_rates.py. Definitions as in src/analysis/blocking_accounting.py. Per-hour rates extrapolate from about 10 minutes of traffic (ten 60 s windows) and inherit the per-window reset of block counters; they are exposure-normalised counts, not a measured hourly rate.

## Exposure

| run            |   windows |   capture time (min) |   wall-clock replay (min) |
|:---------------|----------:|---------------------:|--------------------------:|
| enforce_k1     |        10 |                   10 |                     10.38 |
| enforce_policy |        10 |                   10 |                     10.2  |
| run1           |        10 |                   10 |                     10.07 |

## False blocks

| run / policy                            |   false blocks |   eligible benign pair-windows |   per eligible pair |   per hour of capture time |   per hour of wall-clock replay | distinct hosts (sum over windows / unique IPs)   | distinct hosts excl. window's attackers+victims (sum / unique)   |   windows with >= 1 false block |
|:----------------------------------------|---------------:|-------------------------------:|--------------------:|---------------------------:|--------------------------------:|:-------------------------------------------------|:-----------------------------------------------------------------|--------------------------------:|
| enforce_k1 (enforced)                   |             60 |                           1674 |              0.0358 |                        360 |                           346.8 | 101 / 90                                         | 99 / 88                                                          |                               9 |
| enforce_policy (enforced)               |              0 |                           1675 |              0      |                          0 |                             0   | 0 / 0                                            | 0 / 0                                                            |                               0 |
| run1 simulation, k=1                    |             64 |                           1673 |              0.0383 |                        384 |                           381.4 | 106 / 93                                         | 104 / 91                                                         |                               9 |
| run1 simulation, k=2                    |             14 |                           1673 |              0.0084 |                         84 |                            83.4 | 25 / 24                                          | 23 / 22                                                          |                               7 |
| run1 simulation, k=3                    |              2 |                           1673 |              0.0012 |                         12 |                            11.9 | 4 / 4                                            | 4 / 4                                                            |                               2 |
| run1 simulation, k=5                    |              0 |                           1673 |              0      |                          0 |                             0   | 0 / 0                                            | 0 / 0                                                            |                               0 |
| run1 simulation, k=10                   |              0 |                           1673 |              0      |                          0 |                             0   | 0 / 0                                            | 0 / 0                                                            |                               0 |
| run1 simulation, k=20                   |              0 |                           1673 |              0      |                          0 |                             0   | 0 / 0                                            | 0 / 0                                                            |                               0 |
| run1 simulation, k=1, MITM-ARP ignored  |             37 |                           1673 |              0.0221 |                        222 |                           220.5 | 64 / 58                                          | 62 / 56                                                          |                               6 |
| run1 simulation, k=2, MITM-ARP ignored  |              5 |                           1673 |              0.003  |                         30 |                            29.8 | 10 / 10                                          | 8 / 8                                                            |                               3 |
| run1 simulation, k=3, MITM-ARP ignored  |              1 |                           1673 |              0.0006 |                          6 |                             6   | 2 / 2                                            | 2 / 2                                                            |                               1 |
| run1 simulation, k=5, MITM-ARP ignored  |              0 |                           1673 |              0      |                          0 |                             0   | 0 / 0                                            | 0 / 0                                                            |                               0 |
| run1 simulation, k=10, MITM-ARP ignored |              0 |                           1673 |              0      |                          0 |                             0   | 0 / 0                                            | 0 / 0                                                            |                               0 |
| run1 simulation, k=20, MITM-ARP ignored |              0 |                           1673 |              0      |                          0 |                             0   | 0 / 0                                            | 0 / 0                                                            |                               0 |

Distinct hosts: IPs at either end of a falsely blocked pair. 'Sum over windows' counts an IP once per window (each window is a separate capture); 'unique' counts each IP once over the run (the captures share one lab subnet, so the same IP may be a different device in different captures).

## Blocking-policy selection rule on validation (tune_block_policy.py), unrounded

|   k | ignore MITM-ARP   |   attack flows after block (unrounded) |   false blocks | attack pairs blocked   | attack pairs blocked by class                                                              |   gap to best | within 0.005   |
|----:|:------------------|---------------------------------------:|---------------:|:-----------------------|:-------------------------------------------------------------------------------------------|--------------:|:---------------|
|   1 | False             |                               0.995832 |            128 | 29/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 1/14, Mirai 4/4, Recon 10/10, Web 6/6 |      0        | True           |
|   2 | False             |                               0.995533 |             46 | 26/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/14, Mirai 2/4, Recon 10/10, Web 6/6 |      0.000298 | True           |
|   3 | False             |                               0.995461 |             27 | 21/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/14, Mirai 0/4, Recon 10/10, Web 3/6 |      0.000371 | True           |
|   5 | False             |                               0.995008 |             13 | 21/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/14, Mirai 0/4, Recon 10/10, Web 3/6 |      0.000823 | True           |
|  10 | False             |                               0.994648 |              6 | 20/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/14, Mirai 0/4, Recon 10/10, Web 2/6 |      0.001184 | True           |
|   1 | True              |                               0.995832 |             59 | 28/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/14, Mirai 4/4, Recon 10/10, Web 6/6 |      0        | True           |
|   2 | True              |                               0.995533 |             15 | 26/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/14, Mirai 2/4, Recon 10/10, Web 6/6 |      0.000298 | True           |
|   3 | True              |                               0.995461 |              6 | 21/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/14, Mirai 0/4, Recon 10/10, Web 3/6 |      0.000371 | True           |
|   5 | True              |                               0.995008 |              3 | 21/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/14, Mirai 0/4, Recon 10/10, Web 3/6 |      0.000823 | True           |
|  10 | True              |                               0.994648 |              1 | 20/42                  | BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/14, Mirai 0/4, Recon 10/10, Web 2/6 |      0.001184 | True           |

Every policy within 0.005 of the best coverage: **yes**. The rule therefore picks the fewest false blocks: k=10, ignore MITM-ARP=True (the largest k in the grid [1, 2, 3, 5, 10]).
