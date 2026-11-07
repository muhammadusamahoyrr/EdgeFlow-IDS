# Headline numbers under corrected labels (round 11, P1)

Script: src/analysis/corrected_headline.py. Corrections C1 (2,269 flows) and C2 (2 flows) of label_corrections.py, applied in memory.

## 1. Background share (Table II)

| capture              |   flows |   background old |   background corrected |
|:---------------------|--------:|-----------------:|-----------------------:|
| CommandInjection     |    5639 |           0.9826 |                 0.9826 |
| DDoS-SYN_Flood       |  511936 |           0.0008 |                 0.0008 |
| DictionaryBruteForce |   11824 |           0.9087 |                 0.9087 |
| DoS-HTTP_Flood       |   51275 |           0.23   |                 0.1857 |
| MITM-ArpSpoofing     |   12208 |           0.9756 |                 0.9756 |
| Mirai-udpplain       |     653 |           0.9372 |                 0.9372 |
| Recon-PortScan       |  205065 |           0.302  |                 0.302  |
| SqlInjection         |    7383 |           0.9484 |                 0.9487 |
| XSS                  |    4992 |           0.9846 |                 0.9846 |

- file-name vs old evidence labels differ: 0.1340 (114,845/857,206)
- file-name vs corrected evidence labels differ: 0.1313 (112,578/857,206)

## 2. Deployed tree, temporal test set (setup, Table IV)

| labels    |   macro-F1 | host-pair CI   |   macro-F1 w/o MITM-ARP | pooled Benign FPR     | background FPR        | Benign-capture FPR   | DoS-HTTP capture background FPR   |
|:----------|-----------:|:---------------|------------------------:|:----------------------|:----------------------|:---------------------|:----------------------------------|
| old       |     0.7249 | [0.568, 0.822] |                  0.8259 | 0.0383 (2,030/52,993) | 0.0485 (1,897/39,124) | 0.0096 (133/13,869)  | 0.2680 (1,413/5,272)              |
| corrected |     0.7294 | [0.585, 0.827] |                  0.8311 | 0.0129 (656/50,726)   | 0.0142 (523/36,857)   | 0.0096 (133/13,869)  | 0.0130 (39/3,003)                 |

| labels    | class      |      n |   pairs |    F1 |   recall |
|:----------|:-----------|-------:|--------:|------:|---------:|
| old       | Benign     |  52993 |    3424 | 0.974 |    0.962 |
| old       | BruteForce |    605 |       3 | 0.1   |    0.053 |
| old       | DDoS-SYN   | 153402 |       6 | 1     |    1     |
| old       | DoS-HTTP   |  10110 |       1 | 0.919 |    0.985 |
| old       | MITM-ARP   |     25 |      13 | 0.018 |    0.16  |
| old       | Mirai      |     10 |       6 | 0.9   |    0.9   |
| old       | Recon      |  39819 |      18 | 1     |    1     |
| old       | Web        |    192 |       8 | 0.889 |    0.917 |
| corrected | Benign     |  50726 |    3423 | 0.978 |    0.987 |
| corrected | BruteForce |    605 |       3 | 0.1   |    0.053 |
| corrected | DDoS-SYN   | 153402 |       6 | 1     |    1     |
| corrected | DoS-HTTP   |  12379 |       2 | 0.946 |    0.915 |
| corrected | MITM-ARP   |     25 |      13 | 0.018 |    0.16  |
| corrected | Mirai      |     10 |       6 | 0.9   |    0.9   |
| corrected | Recon      |  39819 |      18 | 1     |    1     |
| corrected | Web        |    190 |       7 | 0.893 |    0.926 |

## 3. File-label tree, temporal split, scored against evidence labels (Table III)

| labels    |   macro-F1 vs evidence | pooled FPR             | background FPR         | Benign-capture FPR    |
|:----------|-----------------------:|:-----------------------|:-----------------------|:----------------------|
| old       |                 0.3963 | 0.7177 (38,034/52,993) | 0.8610 (33,685/39,124) | 0.3136 (4,349/13,869) |
| corrected |                 0.4086 | 0.7057 (35,795/50,726) | 0.8532 (31,446/36,857) | 0.3136 (4,349/13,869) |

## 4. Leave-one-capture-out Benign FPR (Table III); paired diff = file-label minus evidence tree

| held-out capture     |   Benign flows (old) |   FPR file-label tree (old) |   FPR evidence tree (old) |   paired diff (old) |   Benign flows (corrected) |   FPR file-label tree (corrected) |   FPR evidence tree (corrected) |   paired diff (corrected) |
|:---------------------|---------------------:|----------------------------:|--------------------------:|--------------------:|---------------------------:|----------------------------------:|--------------------------------:|--------------------------:|
| Benign_Final         |                46231 |                      1      |                    0.0152 |              0.9848 |                      46231 |                            1      |                          0.0154 |                    0.9846 |
| CommandInjection     |                 5541 |                      0.8775 |                    0.0105 |              0.867  |                       5541 |                            0.8775 |                          0.0099 |                    0.8676 |
| DDoS-SYN_Flood       |                  409 |                      0.8704 |                    0.0538 |              0.8166 |                        409 |                            0.8704 |                          0.044  |                    0.8264 |
| DictionaryBruteForce |                10744 |                      0.8417 |                    0.0127 |              0.829  |                      10744 |                            0.8417 |                          0.0133 |                    0.8284 |
| DoS-HTTP_Flood       |                11791 |                      0.7929 |                    0.0123 |              0.7806 |                       9522 |                            0.7948 |                          0.015  |                    0.7798 |
| MITM-ArpSpoofing     |                11910 |                      0.7141 |                    0.0051 |              0.709  |                      11910 |                            0.7141 |                          0.0068 |                    0.7073 |
| Mirai-udpplain       |                  612 |                      0.8023 |                    0.0114 |              0.7909 |                        612 |                            0.8023 |                          0.0114 |                    0.7909 |
| Recon-PortScan       |                61921 |                      0.73   |                    0.0145 |              0.7155 |                      61921 |                            0.73   |                          0.0163 |                    0.7137 |
| SqlInjection         |                 7002 |                      0.8599 |                    0.0111 |              0.8488 |                       7004 |                            0.8599 |                          0.0117 |                    0.8482 |
| XSS                  |                 4915 |                      0.8163 |                    0.0124 |              0.8039 |                       4915 |                            0.8163 |                          0.0128 |                    0.8035 |

## 5. Blocking replay, MITM-ARP verdicts ignored (exposure 5.91 h)

| labels    | horizon    |   k | attacker pairs blocked   |   false blocks |   per hour |   benign-only pairs |
|:----------|:-----------|----:|:-------------------------|---------------:|-----------:|--------------------:|
| old       | reset 60 s |   1 | 40/55                    |            124 |       21   |                3410 |
| old       | reset 60 s |   2 | 36/55                    |             15 |        2.5 |                3410 |
| old       | reset 60 s |   3 | 34/55                    |              3 |        0.5 |                3410 |
| old       | reset 60 s |   5 | 30/55                    |              1 |        0.2 |                3410 |
| old       | reset 60 s |  10 | 28/55                    |              1 |        0.2 |                3410 |
| old       | reset 60 s |  20 | 27/55                    |              1 |        0.2 |                3410 |
| old       | persistent |   1 | 40/55                    |            124 |       21   |                3410 |
| old       | persistent |   2 | 38/55                    |             43 |        7.3 |                3410 |
| old       | persistent |   3 | 35/55                    |             22 |        3.7 |                3410 |
| old       | persistent |   5 | 34/55                    |              7 |        1.2 |                3410 |
| old       | persistent |  10 | 29/55                    |              3 |        0.5 |                3410 |
| old       | persistent |  20 | 28/55                    |              2 |        0.3 |                3410 |
| corrected | reset 60 s |   1 | 41/55                    |            123 |       20.8 |                3410 |
| corrected | reset 60 s |   2 | 37/55                    |             14 |        2.4 |                3410 |
| corrected | reset 60 s |   3 | 35/55                    |              2 |        0.3 |                3410 |
| corrected | reset 60 s |   5 | 31/55                    |              0 |        0   |                3410 |
| corrected | reset 60 s |  10 | 29/55                    |              0 |        0   |                3410 |
| corrected | reset 60 s |  20 | 28/55                    |              0 |        0   |                3410 |
| corrected | persistent |   1 | 41/55                    |            123 |       20.8 |                3410 |
| corrected | persistent |   2 | 39/55                    |             42 |        7.1 |                3410 |
| corrected | persistent |   3 | 36/55                    |             21 |        3.6 |                3410 |
| corrected | persistent |   5 | 35/55                    |              6 |        1   |                3410 |
| corrected | persistent |  10 | 30/55                    |              2 |        0.3 |                3410 |
| corrected | persistent |  20 | 29/55                    |              1 |        0.2 |                3410 |

Falsely blocked pairs:

- old, reset 60 s, k=5: DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap|192.168.137.174|192.168.137.66
- old, reset 60 s, k=10: DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap|192.168.137.174|192.168.137.66
- old, reset 60 s, k=20: DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap|192.168.137.174|192.168.137.66
- old, persistent, k=5: Benign_Final/BenignTraffic3.pcap|173.198.192.103|192.168.137.253; Benign_Final/BenignTraffic3.pcap|192.168.137.131|52.11.155.34; DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap|192.168.137.174|192.168.137.66; Recon-PortScan/Recon-PortScan.pcap|120.76.210.199|192.168.137.163; Recon-PortScan/Recon-PortScan.pcap|192.168.137.191|192.168.137.199; Recon-PortScan/Recon-PortScan.pcap|192.168.137.208|34.208.202.84; Recon-PortScan/Recon-PortScan.pcap|192.168.137.238|52.11.155.34
- old, persistent, k=10: Benign_Final/BenignTraffic3.pcap|173.198.192.103|192.168.137.253; DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap|192.168.137.174|192.168.137.66; Recon-PortScan/Recon-PortScan.pcap|192.168.137.238|52.11.155.34
- old, persistent, k=20: DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap|192.168.137.174|192.168.137.66; Recon-PortScan/Recon-PortScan.pcap|192.168.137.238|52.11.155.34
- corrected, reset 60 s, k=5: 
- corrected, reset 60 s, k=10: 
- corrected, reset 60 s, k=20: 
- corrected, persistent, k=5: Benign_Final/BenignTraffic3.pcap|173.198.192.103|192.168.137.253; Benign_Final/BenignTraffic3.pcap|192.168.137.131|52.11.155.34; Recon-PortScan/Recon-PortScan.pcap|120.76.210.199|192.168.137.163; Recon-PortScan/Recon-PortScan.pcap|192.168.137.191|192.168.137.199; Recon-PortScan/Recon-PortScan.pcap|192.168.137.208|34.208.202.84; Recon-PortScan/Recon-PortScan.pcap|192.168.137.238|52.11.155.34
- corrected, persistent, k=10: Benign_Final/BenignTraffic3.pcap|173.198.192.103|192.168.137.253; Recon-PortScan/Recon-PortScan.pcap|192.168.137.238|52.11.155.34
- corrected, persistent, k=20: Recon-PortScan/Recon-PortScan.pcap|192.168.137.238|52.11.155.34

