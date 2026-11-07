# Blocking evaluation: full accounting

Definitions as in src/analysis/round2_checks.py and block_curve.py: a block is false if the blocked host pair has no attack flow in that window (labels: extract_flows.label_flows + data/attackers.json; window flows: eval_live.in_window). Enforced runs: the trigger flow is the one with blocked_now = 1.

## Enforced run enforce_k1

### (b) Per-window denominators

| window               |   host pairs |   attacker pairs |   benign pairs (eligible) |   benign pairs with >=1 attack verdict |   same, MITM-ARP verdicts ignored |   pairs blocked |   false blocks |   false-block rate (per eligible pair) |   benign flows |   benign flows with attack verdict |
|:---------------------|-------------:|-----------------:|--------------------------:|---------------------------------------:|----------------------------------:|----------------:|---------------:|---------------------------------------:|---------------:|-----------------------------------:|
| Benign_Final         |          172 |                0 |                       172 |                                      4 |                                 2 |               4 |              4 |                                 0.0233 |            303 |                                  4 |
| CommandInjection     |          158 |                1 |                       157 |                                      3 |                                 1 |               4 |              3 |                                 0.0191 |            291 |                                  3 |
| DDoS-SYN_Flood       |          150 |                6 |                       144 |                                     18 |                                16 |              24 |             18 |                                 0.125  |            273 |                                 20 |
| DictionaryBruteForce |          163 |                1 |                       162 |                                      1 |                                 0 |               2 |              1 |                                 0.0062 |            319 |                                  1 |
| DoS-HTTP_Flood       |          235 |                1 |                       234 |                                     16 |                                13 |              17 |             16 |                                 0.0684 |            600 |                                 18 |
| MITM-ArpSpoofing     |          212 |                7 |                       205 |                                      9 |                                 2 |               9 |              9 |                                 0.0439 |            462 |                                 10 |
| Mirai-udpplain       |           73 |                7 |                        66 |                                      0 |                                 0 |               7 |              0 |                                 0      |            186 |                                  0 |
| Recon-PortScan       |          181 |                1 |                       180 |                                      4 |                                 3 |               5 |              4 |                                 0.0222 |            534 |                                  4 |
| SqlInjection         |          204 |                1 |                       203 |                                      3 |                                 2 |               4 |              3 |                                 0.0148 |            508 |                                  3 |
| XSS                  |          152 |                1 |                       151 |                                      2 |                                 0 |               3 |              2 |                                 0.0132 |            259 |                                  2 |

Totals: 1,700 host-pair-windows, 26 attacker pairs, 1,674 benign pairs eligible to be falsely blocked, 60 of them with >= 1 attack verdict, 60 false blocks (0.0358 per eligible pair; 0.0174 of 3,735 benign flows got an attack verdict).

Attacker pairs blocked by class: BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/7, Mirai 7/7, Recon 1/1, Web 3/3 (total 19/26).

### (a) False blocks by trigger verdict and host role

| trigger verdict   |   attacker host, non-attack traffic |   uninvolved benign hosts |   victim host, non-attack traffic |   total |
|:------------------|------------------------------------:|--------------------------:|----------------------------------:|--------:|
| DDoS-SYN          |                                   0 |                         5 |                                 0 |       5 |
| DoS-HTTP          |                                   1 |                        29 |                                 2 |      32 |
| MITM-ARP          |                                   1 |                        20 |                                 0 |      21 |
| Mirai             |                                   0 |                         1 |                                 0 |       1 |
| Recon             |                                   0 |                         1 |                                 0 |       1 |
| total             |                                   2 |                        56 |                                 2 |      60 |

By window and trigger verdict:

| window               |   DDoS-SYN |   DoS-HTTP |   MITM-ARP |   Mirai |   Recon |   total |
|:---------------------|-----------:|-----------:|-----------:|--------:|--------:|--------:|
| Benign_Final         |          0 |          2 |          2 |       0 |       0 |       4 |
| CommandInjection     |          0 |          1 |          2 |       0 |       0 |       3 |
| DDoS-SYN_Flood       |          4 |         10 |          2 |       1 |       1 |      18 |
| DictionaryBruteForce |          0 |          0 |          1 |       0 |       0 |       1 |
| DoS-HTTP_Flood       |          1 |         12 |          3 |       0 |       0 |      16 |
| MITM-ArpSpoofing     |          0 |          2 |          7 |       0 |       0 |       9 |
| Recon-PortScan       |          0 |          3 |          1 |       0 |       0 |       4 |
| SqlInjection         |          0 |          2 |          1 |       0 |       0 |       3 |
| XSS                  |          0 |          0 |          2 |       0 |       0 |       2 |
| total                |          5 |         32 |         21 |       1 |       1 |      60 |

All false blocks:

| window               | pair                              | trigger verdict   |   trigger dst_port |   protocol | role                              |   pair flows in window |   pair flows with attack verdict |
|:---------------------|:----------------------------------|:------------------|-------------------:|-----------:|:----------------------------------|-----------------------:|---------------------------------:|
| Benign_Final         | 192.168.137.1 - 192.168.137.133   | MITM-ARP          |                 53 |         17 | uninvolved benign hosts           |                      8 |                                1 |
| Benign_Final         | 173.198.192.103 - 192.168.137.253 | DoS-HTTP          |               4431 |          6 | uninvolved benign hosts           |                      8 |                                1 |
| Benign_Final         | 192.168.137.1 - 192.168.137.253   | MITM-ARP          |                 53 |         17 | uninvolved benign hosts           |                      4 |                                1 |
| Benign_Final         | 192.168.137.1 - 192.168.137.16    | DoS-HTTP          |                 53 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| CommandInjection     | 172.253.63.188 - 192.168.137.121  | MITM-ARP          |               5228 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| CommandInjection     | 192.168.137.55 - 34.213.103.51    | MITM-ARP          |              38926 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| CommandInjection     | 108.138.125.14 - 192.168.137.12   | DoS-HTTP          |              32964 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.245 - 34.158.253.218  | DoS-HTTP          |                 80 |          6 | victim host, non-attack traffic   |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.253 - 34.158.253.218  | DoS-HTTP          |               4070 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.29 - 35.170.219.163   | DoS-HTTP          |              50525 |          6 | uninvolved benign hosts           |                      5 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.158 - 192.168.137.7   | DoS-HTTP          |               8009 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.209 - 54.218.246.107  | MITM-ARP          |              48256 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.245 - 99.83.183.187   | DoS-HTTP          |                443 |          6 | victim host, non-attack traffic   |                      2 |                                2 |
| DDoS-SYN_Flood       | 192.168.137.106 - 75.2.39.155     | DoS-HTTP          |              49154 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.159 - 75.2.39.155     | DoS-HTTP          |              35502 |          6 | uninvolved benign hosts           |                      4 |                                2 |
| DDoS-SYN_Flood       | 192.168.137.159 - 35.169.134.177  | DoS-HTTP          |              46316 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.54 - 3.223.181.245    | Mirai             |              40232 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.140 - 35.161.249.48   | DDoS-SYN          |              20443 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.172 - 44.231.239.23   | MITM-ARP          |              34858 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.11 - 54.192.51.75     | DoS-HTTP          |                443 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.94 - 54.148.153.241   | DDoS-SYN          |               8886 |          6 | uninvolved benign hosts           |                      3 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.43 - 35.161.158.54    | Recon             |               8886 |          6 | uninvolved benign hosts           |                      3 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.225 - 35.168.43.144   | DDoS-SYN          |               1883 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.21 - 54.188.99.4      | DDoS-SYN          |               8886 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.11 - 75.2.39.155      | DoS-HTTP          |              43240 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DictionaryBruteForce | 172.253.115.188 - 192.168.137.41  | MITM-ARP          |                443 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| DoS-HTTP_Flood       | 17.57.147.5 - 192.168.137.153     | MITM-ARP          |               5223 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.244 - 192.168.137.66  | DoS-HTTP          |               8009 |          6 | attacker host, non-attack traffic |                      2 |                                2 |
| DoS-HTTP_Flood       | 192.168.137.222 - 54.197.127.199  | DoS-HTTP          |              47084 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 17.248.175.137 - 192.168.137.153  | DoS-HTTP          |              54237 |          6 | uninvolved benign hosts           |                      2 |                                2 |
| DoS-HTTP_Flood       | 192.168.137.191 - 52.87.75.92     | DoS-HTTP          |              44410 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.254 - 192.168.137.66  | MITM-ARP          |              60000 |          6 | attacker host, non-attack traffic |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.254 - 54.210.31.159   | DoS-HTTP          |              56256 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.1 - 192.168.137.64    | DoS-HTTP          |                  7 |          6 | uninvolved benign hosts           |                      6 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.123 - 192.168.137.191 | DoS-HTTP          |              55443 |          6 | uninvolved benign hosts           |                      4 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.222 - 44.197.43.221   | DoS-HTTP          |              52634 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.163 - 47.254.72.224   | DoS-HTTP          |              47856 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.254 - 52.6.61.231     | DoS-HTTP          |              58285 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.163 - 39.108.218.123  | DoS-HTTP          |              13502 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.224 - 54.212.163.173  | DoS-HTTP          |              53585 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 18.211.132.11 - 192.168.137.3     | DDoS-SYN          |              57009 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.6 - 34.205.1.68       | MITM-ARP          |              47142 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| MITM-ArpSpoofing     | 173.198.192.117 - 192.168.137.145 | MITM-ARP          |               4431 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| MITM-ArpSpoofing     | 192.168.137.145 - 34.107.165.188  | MITM-ARP          |                443 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| MITM-ArpSpoofing     | 192.168.137.145 - 54.186.53.219   | DoS-HTTP          |              40594 |          6 | uninvolved benign hosts           |                      4 |                                1 |
| MITM-ArpSpoofing     | 172.217.1.10 - 192.168.137.150    | MITM-ARP          |                443 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| MITM-ArpSpoofing     | 192.168.137.145 - 3.144.50.152    | MITM-ARP          |                 80 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| MITM-ArpSpoofing     | 142.251.33.164 - 192.168.137.13   | MITM-ARP          |                443 |         17 | uninvolved benign hosts           |                      2 |                                2 |
| MITM-ArpSpoofing     | 142.251.111.188 - 192.168.137.38  | MITM-ARP          |               5228 |          6 | uninvolved benign hosts           |                      4 |                                1 |
| MITM-ArpSpoofing     | 192.168.137.1 - 192.168.137.23    | DoS-HTTP          |                 53 |          6 | uninvolved benign hosts           |                     83 |                                1 |
| MITM-ArpSpoofing     | 192.168.137.76 - 54.188.27.243    | MITM-ARP          |                443 |          6 | uninvolved benign hosts           |                      3 |                                1 |
| Recon-PortScan       | 120.76.210.199 - 192.168.137.163  | DoS-HTTP          |                 80 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| Recon-PortScan       | 192.168.137.238 - 52.11.155.34    | DoS-HTTP          |                 21 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| Recon-PortScan       | 142.251.32.67 - 192.168.137.59    | MITM-ARP          |                 80 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| Recon-PortScan       | 109.95.152.166 - 192.168.137.41   | DoS-HTTP          |                443 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| SqlInjection         | 120.76.210.199 - 192.168.137.163  | DoS-HTTP          |                 80 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| SqlInjection         | 13.225.189.40 - 192.168.137.234   | DoS-HTTP          |              45442 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| SqlInjection         | 100.21.156.247 - 192.168.137.242  | MITM-ARP          |              50919 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| XSS                  | 172.253.63.188 - 192.168.137.121  | MITM-ARP          |               5228 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| XSS                  | 192.168.137.55 - 34.213.103.51    | MITM-ARP          |              38926 |          6 | uninvolved benign hosts           |                      2 |                                1 |

## Enforced run enforce_policy

### (b) Per-window denominators

| window               |   host pairs |   attacker pairs |   benign pairs (eligible) |   benign pairs with >=1 attack verdict |   same, MITM-ARP verdicts ignored |   pairs blocked |   false blocks |   false-block rate (per eligible pair) |   benign flows |   benign flows with attack verdict |
|:---------------------|-------------:|-----------------:|--------------------------:|---------------------------------------:|----------------------------------:|----------------:|---------------:|---------------------------------------:|---------------:|-----------------------------------:|
| Benign_Final         |          172 |                0 |                       172 |                                      4 |                                 2 |               0 |              0 |                                      0 |            307 |                                  6 |
| CommandInjection     |          158 |                1 |                       157 |                                      2 |                                 0 |               0 |              0 |                                      0 |            295 |                                  3 |
| DDoS-SYN_Flood       |          150 |                6 |                       144 |                                     19 |                                17 |               6 |              0 |                                      0 |            256 |                                 24 |
| DictionaryBruteForce |          164 |                1 |                       163 |                                      1 |                                 0 |               1 |              0 |                                      0 |            322 |                                  3 |
| DoS-HTTP_Flood       |          235 |                1 |                       234 |                                     16 |                                13 |               1 |              0 |                                      0 |            602 |                                 18 |
| MITM-ArpSpoofing     |          211 |                7 |                       204 |                                      8 |                                 1 |               0 |              0 |                                      0 |            469 |                                 11 |
| Mirai-udpplain       |           74 |                7 |                        67 |                                      0 |                                 0 |               0 |              0 |                                      0 |            187 |                                  0 |
| Recon-PortScan       |          181 |                1 |                       180 |                                      5 |                                 3 |               1 |              0 |                                      0 |            538 |                                  6 |
| SqlInjection         |          204 |                1 |                       203 |                                      3 |                                 2 |               0 |              0 |                                      0 |            511 |                                  3 |
| XSS                  |          152 |                1 |                       151 |                                      2 |                                 0 |               0 |              0 |                                      0 |            262 |                                  2 |

Totals: 1,701 host-pair-windows, 26 attacker pairs, 1,675 benign pairs eligible to be falsely blocked, 60 of them with >= 1 attack verdict, 0 false blocks (0.0000 per eligible pair; 0.0203 of 3,749 benign flows got an attack verdict).

Attacker pairs blocked by class: BruteForce 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM-ARP 0/7, Mirai 0/7, Recon 1/1, Web 0/3 (total 9/26).

## (c) Run-1 k-curve (simulated per window), all attack classes

Columns per class: attacker pairs blocked / attacker pairs in the windows. The class columns sum to the Attackers column.

|   k | MITM-ARP ignored   |   blocked |   false | attackers   | BruteForce   | DDoS-SYN   | DoS-HTTP   | MITM-ARP   | Mirai   | Recon   | Web   | false blocks by trigger verdict                        |
|----:|:-------------------|----------:|--------:|:------------|:-------------|:-----------|:-----------|:-----------|:--------|:--------|:------|:-------------------------------------------------------|
|   1 | False              |        83 |      64 | 19/26       | 1/1          | 6/6        | 1/1        | 0/7        | 7/7     | 1/1     | 3/3   | DDoS-SYN 4, DoS-HTTP 30, MITM-ARP 27, Mirai 1, Recon 2 |
|   2 | False              |        32 |      14 | 18/26       | 1/1          | 6/6        | 1/1        | 0/7        | 6/7     | 1/1     | 3/3   | DoS-HTTP 5, MITM-ARP 9                                 |
|   3 | False              |        15 |       2 | 13/26       | 1/1          | 6/6        | 1/1        | 0/7        | 1/7     | 1/1     | 3/3   | DoS-HTTP 1, MITM-ARP 1                                 |
|   5 | False              |        10 |       0 | 10/26       | 1/1          | 6/6        | 1/1        | 0/7        | 0/7     | 1/1     | 1/3   |                                                        |
|  10 | False              |         9 |       0 | 9/26        | 1/1          | 6/6        | 1/1        | 0/7        | 0/7     | 1/1     | 0/3   |                                                        |
|  20 | False              |         8 |       0 | 8/26        | 0/1          | 6/6        | 1/1        | 0/7        | 0/7     | 1/1     | 0/3   |                                                        |
|   1 | True               |        56 |      37 | 19/26       | 1/1          | 6/6        | 1/1        | 0/7        | 7/7     | 1/1     | 3/3   | DDoS-SYN 4, DoS-HTTP 30, Mirai 1, Recon 2              |
|   2 | True               |        23 |       5 | 18/26       | 1/1          | 6/6        | 1/1        | 0/7        | 6/7     | 1/1     | 3/3   | DoS-HTTP 5                                             |
|   3 | True               |        14 |       1 | 13/26       | 1/1          | 6/6        | 1/1        | 0/7        | 1/7     | 1/1     | 3/3   | DoS-HTTP 1                                             |
|   5 | True               |        10 |       0 | 10/26       | 1/1          | 6/6        | 1/1        | 0/7        | 0/7     | 1/1     | 1/3   |                                                        |
|  10 | True               |         9 |       0 | 9/26        | 1/1          | 6/6        | 1/1        | 0/7        | 0/7     | 1/1     | 0/3   |                                                        |
|  20 | True               |         8 |       0 | 8/26        | 0/1          | 6/6        | 1/1        | 0/7        | 0/7     | 1/1     | 0/3   |                                                        |

### (b) Run-1 per-window denominators at k = 1

| ignore MITM-ARP   | window               |   host pairs |   attacker pairs |   benign pairs (eligible) |   benign pairs with >=1 attack verdict |   same, MITM-ARP verdicts ignored |   pairs blocked |   false blocks |   false-block rate (per eligible pair) |   benign flows |   benign flows with attack verdict |
|:------------------|:---------------------|-------------:|-----------------:|--------------------------:|---------------------------------------:|----------------------------------:|----------------:|---------------:|---------------------------------------:|---------------:|-----------------------------------:|
| False             | Benign_Final         |          172 |                0 |                       172 |                                      4 |                                 2 |               4 |              4 |                                 0.0233 |            304 |                                  6 |
| False             | CommandInjection     |          158 |                1 |                       157 |                                      2 |                                 0 |               3 |              2 |                                 0.0127 |            295 |                                  4 |
| False             | DDoS-SYN_Flood       |          150 |                6 |                       144 |                                     20 |                                17 |              26 |             20 |                                 0.1389 |            255 |                                 25 |
| False             | DictionaryBruteForce |          163 |                1 |                       162 |                                      1 |                                 0 |               2 |              1 |                                 0.0062 |            320 |                                  2 |
| False             | DoS-HTTP_Flood       |          235 |                1 |                       234 |                                     16 |                                12 |              17 |             16 |                                 0.0684 |            604 |                                 18 |
| False             | MITM-ArpSpoofing     |          211 |                7 |                       204 |                                     12 |                                 1 |              12 |             12 |                                 0.0588 |            467 |                                 17 |
| False             | Mirai-udpplain       |           73 |                7 |                        66 |                                      0 |                                 0 |               7 |              0 |                                 0      |            186 |                                  0 |
| False             | Recon-PortScan       |          181 |                1 |                       180 |                                      4 |                                 3 |               5 |              4 |                                 0.0222 |            538 |                                  5 |
| False             | SqlInjection         |          204 |                1 |                       203 |                                      3 |                                 2 |               4 |              3 |                                 0.0148 |            512 |                                  3 |
| False             | XSS                  |          152 |                1 |                       151 |                                      2 |                                 0 |               3 |              2 |                                 0.0132 |            262 |                                  2 |
| True              | Benign_Final         |          172 |                0 |                       172 |                                      4 |                                 2 |               2 |              2 |                                 0.0116 |            304 |                                  6 |
| True              | CommandInjection     |          158 |                1 |                       157 |                                      2 |                                 0 |               1 |              0 |                                 0      |            295 |                                  4 |
| True              | DDoS-SYN_Flood       |          150 |                6 |                       144 |                                     20 |                                17 |              23 |             17 |                                 0.1181 |            255 |                                 25 |
| True              | DictionaryBruteForce |          163 |                1 |                       162 |                                      1 |                                 0 |               1 |              0 |                                 0      |            320 |                                  2 |
| True              | DoS-HTTP_Flood       |          235 |                1 |                       234 |                                     16 |                                12 |              13 |             12 |                                 0.0513 |            604 |                                 18 |
| True              | MITM-ArpSpoofing     |          211 |                7 |                       204 |                                     12 |                                 1 |               1 |              1 |                                 0.0049 |            467 |                                 17 |
| True              | Mirai-udpplain       |           73 |                7 |                        66 |                                      0 |                                 0 |               7 |              0 |                                 0      |            186 |                                  0 |
| True              | Recon-PortScan       |          181 |                1 |                       180 |                                      4 |                                 3 |               4 |              3 |                                 0.0167 |            538 |                                  5 |
| True              | SqlInjection         |          204 |                1 |                       203 |                                      3 |                                 2 |               3 |              2 |                                 0.0099 |            512 |                                  3 |
| True              | XSS                  |          152 |                1 |                       151 |                                      2 |                                 0 |               1 |              0 |                                 0      |            262 |                                  2 |

## (d) One-core run (edge100) macro-F1 0.810 vs 0.804

Live per-class F1 (support) of every detection run (from results/live/<run>/live_vs_offline.json):

| run       |   CPU quota |   windows |   offline macro-F1 |   live macro-F1 | Benign F1 (n)   | BruteForce F1 (n)   | DDoS-SYN F1 (n)   | DoS-HTTP F1 (n)   | MITM-ARP F1 (n)   | Mirai F1 (n)   | Recon F1 (n)   | Web F1 (n)   |
|:----------|------------:|----------:|-------------------:|----------------:|:----------------|:--------------------|:------------------|:------------------|:------------------|:---------------|:---------------|:-------------|
| run1      |         nan |        10 |             0.8036 |          0.8042 | 0.977 (3225)    | 0.78 (25)           | 1.0 (142580)      | 0.975 (1955)      | 0.0 (2)           | 0.75 (4)       | 0.992 (1081)   | 0.96 (12)    |
| run1_r2   |         nan |        10 |             0.8036 |          0.8038 | 0.976 (3233)    | 0.78 (25)           | 1.0 (160068)      | 0.972 (1902)      | 0.0 (2)           | 0.75 (4)       | 0.992 (1081)   | 0.96 (12)    |
| run1_r3   |         nan |        10 |             0.8036 |          0.8043 | 0.978 (3229)    | 0.78 (25)           | 1.0 (184308)      | 0.974 (1924)      | 0.0 (2)           | 0.75 (4)       | 0.992 (1081)   | 0.96 (12)    |
| edge100   |         100 |        10 |             0.8036 |          0.8102 | 0.977 (3228)    | 0.78 (25)           | 1.0 (142554)      | 0.972 (1891)      | 0.0 (2)           | 0.8 (5)        | 0.992 (1081)   | 0.96 (12)    |
| edge50    |          50 |         3 |             0.9145 |          0.9175 | 0.944 (871)     | nan                 | 1.0 (142554)      | 0.976 (1917)      | nan               | 0.75 (4)       | nan            | nan          |
| edge50_r2 |          50 |         3 |             0.9145 |          0.9172 | 0.943 (874)     | nan                 | 1.0 (160297)      | 0.976 (1891)      | nan               | 0.75 (4)       | nan            | nan          |
| edge50_r3 |          50 |         3 |             0.9145 |          0.9173 | 0.943 (871)     | nan                 | 1.0 (142554)      | 0.976 (1918)      | nan               | 0.75 (4)       | nan            | nan          |

Decomposition of edge100 minus run1 (live, same ten windows):

| class      | run1 live F1 (n)   | edge100 live F1 (n)   |   contribution to macro-F1 difference |
|:-----------|:-------------------|:----------------------|--------------------------------------:|
| Benign     | 0.977 (3225)       | 0.977 (3228)          |                                0      |
| BruteForce | 0.78 (25)          | 0.78 (25)             |                                0      |
| DDoS-SYN   | 1.0 (142580)       | 1.0 (142554)          |                                0      |
| DoS-HTTP   | 0.975 (1955)       | 0.972 (1891)          |                               -0.0004 |
| MITM-ARP   | 0.0 (2)            | 0.0 (2)               |                                0      |
| Mirai      | 0.75 (4)           | 0.8 (5)               |                                0.0063 |
| Recon      | 0.992 (1081)       | 0.992 (1081)          |                                0      |
| Web        | 0.96 (12)          | 0.96 (12)             |                                0      |

Sum of contributions: +0.0059 (per-class F1 rounded to 3 decimals in the json).
