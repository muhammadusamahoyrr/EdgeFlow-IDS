# CIC-IoT2023: decomposition of the random-minus-temporal gap (final review M2)

Script: src/analysis/final_gap.py. Splits of src/train_baseline.py; paired host-pair bootstrap of src/analysis/paired_diff.py (1000 resamples, seed 0, union clusters 4,641). Classes: Benign, BruteForce, DDoS-SYN, DoS-HTTP, MITM-ARP, Mirai, Recon, Web.

## decision tree (Table perclass)

| class      |   temporal test flows |   host pairs temporal |   host pairs random |   F1 random |   F1 temporal |   random - temporal |   share of summed difference |
|:-----------|----------------------:|----------------------:|--------------------:|------------:|--------------:|--------------------:|-----------------------------:|
| Benign     |                 52993 |                  3424 |                3750 |       0.993 |         0.974 |               0.019 |                        0.017 |
| BruteForce |                   605 |                     3 |                   3 |       0.991 |         0.1   |               0.891 |                        0.811 |
| DDoS-SYN   |                153402 |                     6 |                   6 |       1     |         1     |               0     |                        0     |
| DoS-HTTP   |                 10110 |                     1 |                   2 |       0.989 |         0.918 |               0.07  |                        0.064 |
| MITM-ARP   |                    25 |                    13 |                  43 |       0.11  |         0.018 |               0.092 |                        0.083 |
| Mirai      |                    10 |                     6 |                   7 |       1     |         0.947 |               0.053 |                        0.048 |
| Recon      |                 39819 |                    18 |                  57 |       1     |         1     |               0     |                        0     |
| Web        |                   192 |                     8 |                  10 |       0.868 |         0.894 |              -0.026 |                       -0.024 |

Summed per-class difference 1.099 (= 0.1373 macro-F1 points); BruteForce contributes 0.891 (81.1%).

Paired host-pair bootstrap of random minus temporal:

| classes                                                                              |   temporal |   random |   random - temporal | paired 95% CI   |   share of resamples <= 0 |
|:-------------------------------------------------------------------------------------|-----------:|---------:|--------------------:|:----------------|--------------------------:|
| all 8 classes                                                                        |      0.731 |    0.869 |               0.137 | [0.024, 0.278]  |                     0.001 |
| without BruteForce (7)                                                               |      0.822 |    0.851 |               0.03  | [0.004, 0.187]  |                     0.009 |
| >= 5 host pairs in both test sets (6: Benign, DDoS-SYN, MITM-ARP, Mirai, Recon, Web) |      0.806 |    0.828 |               0.023 | [0.001, 0.081]  |                     0.021 |

## deployed edge tree

| class      |   temporal test flows |   host pairs temporal |   host pairs random |   F1 random |   F1 temporal |   random - temporal |   share of summed difference |
|:-----------|----------------------:|----------------------:|--------------------:|------------:|--------------:|--------------------:|-----------------------------:|
| Benign     |                 52993 |                  3424 |                3750 |       0.992 |         0.974 |               0.019 |                        0.016 |
| BruteForce |                   605 |                     3 |                   3 |       0.988 |         0.1   |               0.887 |                        0.781 |
| DDoS-SYN   |                153402 |                     6 |                   6 |       1     |         1     |               0     |                        0     |
| DoS-HTTP   |                 10110 |                     1 |                   2 |       0.988 |         0.919 |               0.07  |                        0.061 |
| MITM-ARP   |                    25 |                    13 |                  43 |       0.101 |         0.018 |               0.084 |                        0.074 |
| Mirai      |                    10 |                     6 |                   7 |       1     |         0.9   |               0.1   |                        0.088 |
| Recon      |                 39819 |                    18 |                  57 |       1     |         1     |               0     |                        0     |
| Web        |                   192 |                     8 |                  10 |       0.865 |         0.889 |              -0.023 |                       -0.021 |

Summed per-class difference 1.136 (= 0.1420 macro-F1 points); BruteForce contributes 0.887 (78.1%).

Paired host-pair bootstrap of random minus temporal:

| classes                                                                              |   temporal |   random |   random - temporal | paired 95% CI   |   share of resamples <= 0 |
|:-------------------------------------------------------------------------------------|-----------:|---------:|--------------------:|:----------------|--------------------------:|
| all 8 classes                                                                        |      0.725 |    0.867 |               0.142 | [0.025, 0.287]  |                     0.001 |
| without BruteForce (7)                                                               |      0.814 |    0.85  |               0.036 | [0.007, 0.199]  |                     0.006 |
| >= 5 host pairs in both test sets (6: Benign, DDoS-SYN, MITM-ARP, Mirai, Recon, Web) |      0.797 |    0.827 |               0.03  | [0.004, 0.098]  |                     0.011 |

## BruteForce per target, temporal split

Attacker .65 (data/attackers.json). Training-set BruteForce targets: .67:22 475.

| target   |   test flows |   test host pairs |   train flows | test period     | decision_tree.pkl (54 features): predicted BruteForce / any attack   | dt_nsga.pkl (14 features): predicted BruteForce / any attack   | decision tree (Table perclass), retrained: predicted BruteForce / any attack   | deployed edge tree, retrained: predicted BruteForce / any attack   |
|:---------|-------------:|------------------:|--------------:|:----------------|:---------------------------------------------------------------------|:---------------------------------------------------------------|:-------------------------------------------------------------------------------|:-------------------------------------------------------------------|
| .11:554  |          356 |                 1 |             0 | 15:01-15:01 UTC | 0 / 2                                                                | 16 / 18                                                        | 0 / 2                                                                          | 0 / 2                                                              |
| .140:554 |          211 |                 1 |             0 | 14:56-14:56 UTC | 0 / 34                                                               | 0 / 34                                                         | 0 / 34                                                                         | 0 / 34                                                             |
| .67:22   |           38 |                 1 |           475 | 13:43-13:44 UTC | 32 / 32                                                              | 32 / 32                                                        | 32 / 32                                                                        | 32 / 32                                                            |

Deployed tree: src/gateway.py loads results/models/decision_tree.pkl by default and every live run's windows.json names it; dt_nsga.pkl is the NSGA-II 14-feature variant, not used live. decision_tree.pkl predictions equal the retrained deployed edge tree on 100.0000% of temporal test flows.
