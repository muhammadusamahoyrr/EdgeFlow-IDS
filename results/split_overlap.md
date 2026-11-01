# Connections spanning the temporal train/test boundary

Test flows whose 5-tuple also occurs in the same pcap's training split: 92,766 of 257,156 (36.1%).

| Test set | Macro-F1 [95% CI] (edge tree) |
|---|---|
| All test flows | 0.725 [0.702, 0.741] |
| Without spanning connections | 0.604 [0.598, 0.610] |

Macro-F1 over the 7 classes that still have test flows after removal (Benign, BruteForce, DDoS-SYN, DoS-HTTP, MITM-ARP, Recon, Web): all 0.700 vs without spanning 0.690.

| Class | F1, all test flows | F1, without spanning connections |
|---|---|---|
| Benign | 0.974 | 0.960 |
| BruteForce | 0.100 | 0.100 |
| DDoS-SYN | 1.000 | 1.000 |
| DoS-HTTP | 0.919 | 0.851 |
| MITM-ARP | 0.018 | 0.027 |
| Mirai | 0.900 | 0.000 (no test flows left) |
| Recon | 1.000 | 1.000 |
| Web | 0.889 | 0.893 |

Spanning flows per class:

| label      |   spanning |   test flows |   share |
|:-----------|-----------:|-------------:|--------:|
| Benign     |      20920 |        52993 |   0.395 |
| BruteForce |          0 |          605 |   0     |
| DDoS-SYN   |      66505 |       153402 |   0.434 |
| DoS-HTTP   |       5323 |        10110 |   0.527 |
| MITM-ARP   |          8 |           25 |   0.32  |
| Mirai      |         10 |           10 |   1     |
| Recon      |          0 |        39819 |   0     |
| Web        |          0 |          192 |   0     |
