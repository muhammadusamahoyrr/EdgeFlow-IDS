# Effect of the label errors found by the audit (final review M8)

Script: src/analysis/label_corrections.py (corrections C1, C2 in its docstring). attackers.json and flows.parquet are unchanged; corrections are applied in memory.

- C1 DoS-HTTP flood to unlisted victims: 2,269 flows relabelled Benign -> DoS-HTTP.
- C2 Web flows outside the evidence victims: 2 flows relabelled Web -> Benign.

C1 candidates (.66 -> unlisted LAN host :80, labelled Benign) by server and flood criterion:

| dst_ip          | flood   |   flows |
|:----------------|:--------|--------:|
| 192.168.137.174 | True    |    2269 |
| 192.168.137.186 | False   |      10 |

- temporal split: corrected labels in test 2,271, in train 0
- stratified split: corrected labels in test 667, in train 1,604

## Macro-F1 and per-class F1

| model                              | split      | labels    |   macro-F1 |   Benign |   BruteForce |   DDoS-SYN |   DoS-HTTP |   MITM-ARP |   Mirai |   Recon |   Web |
|:-----------------------------------|:-----------|:----------|-----------:|---------:|-------------:|-----------:|-----------:|-----------:|--------:|--------:|------:|
| deployed file (old-label training) | temporal   | old       |     0.7249 |    0.974 |        0.1   |          1 |      0.919 |      0.018 |     0.9 |       1 | 0.889 |
| deployed file (old-label training) | temporal   | corrected |     0.7294 |    0.978 |        0.1   |          1 |      0.946 |      0.018 |     0.9 |       1 | 0.893 |
| edge tree retrained                | temporal   | old       |     0.7249 |    0.974 |        0.1   |          1 |      0.919 |      0.018 |     0.9 |       1 | 0.889 |
| edge tree retrained                | stratified | old       |     0.8669 |    0.992 |        0.988 |          1 |      0.988 |      0.101 |     1   |       1 | 0.865 |
| edge tree retrained                | temporal   | corrected |     0.7294 |    0.978 |        0.1   |          1 |      0.946 |      0.018 |     0.9 |       1 | 0.893 |
| edge tree retrained                | stratified | corrected |     0.8744 |    0.992 |        0.975 |          1 |      0.991 |      0.134 |     1   |       1 | 0.903 |

## Random-minus-temporal gap, old labels

Macro-F1 random 0.8669, temporal 0.7249, gap +0.1420. Per class (share of summed difference):

| class      |   random |   temporal |   difference | share   |
|:-----------|---------:|-----------:|-------------:|:--------|
| Benign     |    0.992 |      0.974 |        0.018 | 2%      |
| BruteForce |    0.988 |      0.1   |        0.888 | 78%     |
| DDoS-SYN   |    1     |      1     |        0     | 0%      |
| DoS-HTTP   |    0.988 |      0.919 |        0.069 | 6%      |
| MITM-ARP   |    0.101 |      0.018 |        0.083 | 7%      |
| Mirai      |    1     |      0.9   |        0.1   | 9%      |
| Recon      |    1     |      1     |        0     | 0%      |
| Web        |    0.865 |      0.889 |       -0.024 | -2%     |

## Random-minus-temporal gap, corrected labels

Macro-F1 random 0.8744, temporal 0.7294, gap +0.1450. Per class (share of summed difference):

| class      |   random |   temporal |   difference | share   |
|:-----------|---------:|-----------:|-------------:|:--------|
| Benign     |    0.992 |      0.978 |        0.014 | 1%      |
| BruteForce |    0.975 |      0.1   |        0.875 | 75%     |
| DDoS-SYN   |    1     |      1     |        0     | 0%      |
| DoS-HTTP   |    0.991 |      0.946 |        0.045 | 4%      |
| MITM-ARP   |    0.134 |      0.018 |        0.116 | 10%     |
| Mirai      |    1     |      0.9   |        0.1   | 9%      |
| Recon      |    1     |      1     |        0     | 0%      |
| Web        |    0.903 |      0.893 |        0.01  | 1%      |

