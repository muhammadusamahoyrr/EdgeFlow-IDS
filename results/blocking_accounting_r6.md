# Blocking details, review round 6 (extends results/blocking_accounting.md)

## (a) Definition of an eligible benign host-pair window

Computed as in src/analysis/blocking_accounting.py (denominators()). For each run and each of the ten replay windows: the flows are that run's own live flow records (results/live/<run>/flows.csv) whose first-seen time lies in the window's replay interval +-1 s (eval_live.in_window); a host pair is the unordered pair of IP addresses of a flow; a pair is an attacker pair if at least one of its flows in that window is labelled as attack (extract_flows.label_flows with data/attackers.json); every other pair seen in the window is an eligible benign pair, i.e. one that can only be blocked falsely. Counts are per window and summed over windows (a pair seen in two windows counts twice); blocks reset between windows.

Totals per run:

| run            |   flows |   host pairs |   attacker pairs |   eligible benign pairs |
|:---------------|--------:|-------------:|-----------------:|------------------------:|
| enforce_k1     |  193748 |         1700 |               26 |                    1674 |
| enforce_policy |  192773 |         1701 |               26 |                    1675 |
| run1           |  216708 |         1699 |               26 |                    1673 |

Per window:

| window               |   enforce_k1 |   enforce_policy |   run1 |   k1 - policy |
|:---------------------|-------------:|-----------------:|-------:|--------------:|
| Benign_Final         |          172 |              172 |    172 |             0 |
| CommandInjection     |          157 |              157 |    157 |             0 |
| DDoS-SYN_Flood       |          144 |              144 |    144 |             0 |
| DictionaryBruteForce |          162 |              163 |    162 |            -1 |
| DoS-HTTP_Flood       |          234 |              234 |    234 |             0 |
| MITM-ArpSpoofing     |          205 |              204 |    204 |             1 |
| Mirai-udpplain       |           66 |               67 |     66 |            -1 |
| Recon-PortScan       |          180 |              180 |    180 |             0 |
| SqlInjection         |          203 |              203 |    203 |             0 |
| XSS                  |          151 |              151 |    151 |             0 |

## (b) Why 1,674 (enforce_k1) and 1,675 (enforce_policy)

Each enforced run is a separate replay with its own live flow export, so the set of host pairs that appear in a window can differ by a pair or two between runs. Pairs present in a window of one run but not the other:

| window               | only in run    | pair                                | attacker pair   |   flows |   dst ports |   protocols |   packets | verdicts   |
|:---------------------|:---------------|:------------------------------------|:----------------|--------:|------------:|------------:|----------:|:-----------|
| Benign_Final         | enforce_k1     | fe80::6c9c:3ff:fe8b:ebd9 - ff02::2  | False           |       3 |           0 |          58 |         4 | Benign     |
| Benign_Final         | enforce_k1     | fe80::78f6:b2ff:fe31:7abe - ff02::2 | False           |       3 |           0 |          58 |         4 | Benign     |
| Benign_Final         | enforce_policy | fe80::1cfe:78ff:fe46:1a77 - ff02::2 | False           |       3 |           0 |          58 |         4 | Benign     |
| Benign_Final         | enforce_policy | fe80::402d:a6ff:fe65:e19f - ff02::2 | False           |       2 |           0 |          58 |         3 | Benign     |
| CommandInjection     | enforce_k1     | fe80::6c9c:3ff:fe8b:ebd9 - ff02::2  | False           |       1 |           0 |          58 |         1 | Benign     |
| CommandInjection     | enforce_k1     | fe80::78f6:b2ff:fe31:7abe - ff02::2 | False           |       1 |           0 |          58 |         1 | Benign     |
| CommandInjection     | enforce_policy | fe80::1cfe:78ff:fe46:1a77 - ff02::2 | False           |       1 |           0 |          58 |         1 | Benign     |
| CommandInjection     | enforce_policy | fe80::402d:a6ff:fe65:e19f - ff02::2 | False           |       1 |           0 |          58 |         1 | Benign     |
| DictionaryBruteForce | enforce_policy | fe80::402d:a6ff:fe65:e19f - ff02::2 | False           |       1 |           0 |          58 |         1 | Benign     |
| MITM-ArpSpoofing     | enforce_k1     | fe80::6c9c:3ff:fe8b:ebd9 - ff02::2  | False           |       1 |           0 |          58 |         1 | Benign     |
| Mirai-udpplain       | enforce_policy | fe80::402d:a6ff:fe65:e19f - ff02::2 | False           |       1 |           0 |          58 |         1 | Benign     |

All differing pairs are IPv6 link-local sources sending ICMPv6 (protocol 58) to ff02::2 (all-routers). Link-local sources to ff02::2 in each run's whole live flow log (results/live/<run>/flows.csv):

| run            |   link-local sources to ff02::2 |   in every run | run-specific                                         |
|:---------------|--------------------------------:|---------------:|:-----------------------------------------------------|
| run1           |                              12 |             10 | fe80::88a:81ff:fefa:fcb3, fe80::ace7:4bff:fe92:20f6  |
| run1_r2        |                              12 |             10 | fe80::b0f2:f3ff:fef6:663d, fe80::c047:37ff:fe52:6b3  |
| run1_r3        |                              12 |             10 | fe80::30:1cff:fec4:f2d8, fe80::c46e:f2ff:fe39:6b29   |
| edge100        |                              12 |             10 | fe80::5cbb:ffff:fe1d:51a, fe80::b8bf:40ff:fe05:5b12  |
| enforce_k1     |                              12 |             10 | fe80::6c9c:3ff:fe8b:ebd9, fe80::78f6:b2ff:fe31:7abe  |
| enforce_policy |                              12 |             10 | fe80::1cfe:78ff:fe46:1a77, fe80::402d:a6ff:fe65:e19f |

The run-specific addresses change from run to run, unlike the addresses from the replayed captures, so they are not in the pcaps; whether such a pair falls in a window (and in which) differs per run.

## (c) Window of each MITM-ARP-triggered false block (enforce_k1)

| window               |   MITM-ARP-triggered false blocks |
|:---------------------|----------------------------------:|
| Benign_Final         |                                 2 |
| CommandInjection     |                                 2 |
| DDoS-SYN_Flood       |                                 2 |
| DictionaryBruteForce |                                 1 |
| DoS-HTTP_Flood       |                                 3 |
| MITM-ArpSpoofing     |                                 7 |
| Recon-PortScan       |                                 1 |
| SqlInjection         |                                 1 |
| XSS                  |                                 2 |

Total: 21; in the MITM-ArpSpoofing window: 7; in other windows: 14. Roles: uninvolved benign hosts 20, attacker host, non-attack traffic 1.

| window               | pair                              | trigger verdict   |   trigger dst_port |   protocol | role                              |   pair flows in window |   pair flows with attack verdict |
|:---------------------|:----------------------------------|:------------------|-------------------:|-----------:|:----------------------------------|-----------------------:|---------------------------------:|
| Benign_Final         | 192.168.137.1 - 192.168.137.133   | MITM-ARP          |                 53 |         17 | uninvolved benign hosts           |                      8 |                                1 |
| Benign_Final         | 192.168.137.1 - 192.168.137.253   | MITM-ARP          |                 53 |         17 | uninvolved benign hosts           |                      4 |                                1 |
| CommandInjection     | 172.253.63.188 - 192.168.137.121  | MITM-ARP          |               5228 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| CommandInjection     | 192.168.137.55 - 34.213.103.51    | MITM-ARP          |              38926 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.209 - 54.218.246.107  | MITM-ARP          |              48256 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DDoS-SYN_Flood       | 192.168.137.172 - 44.231.239.23   | MITM-ARP          |              34858 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| DictionaryBruteForce | 172.253.115.188 - 192.168.137.41  | MITM-ARP          |                443 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| DoS-HTTP_Flood       | 17.57.147.5 - 192.168.137.153     | MITM-ARP          |               5223 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.254 - 192.168.137.66  | MITM-ARP          |              60000 |          6 | attacker host, non-attack traffic |                      1 |                                1 |
| DoS-HTTP_Flood       | 192.168.137.6 - 34.205.1.68       | MITM-ARP          |              47142 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| MITM-ArpSpoofing     | 173.198.192.117 - 192.168.137.145 | MITM-ARP          |               4431 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| MITM-ArpSpoofing     | 192.168.137.145 - 34.107.165.188  | MITM-ARP          |                443 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| MITM-ArpSpoofing     | 172.217.1.10 - 192.168.137.150    | MITM-ARP          |                443 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| MITM-ArpSpoofing     | 192.168.137.145 - 3.144.50.152    | MITM-ARP          |                 80 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| MITM-ArpSpoofing     | 142.251.33.164 - 192.168.137.13   | MITM-ARP          |                443 |         17 | uninvolved benign hosts           |                      2 |                                2 |
| MITM-ArpSpoofing     | 142.251.111.188 - 192.168.137.38  | MITM-ARP          |               5228 |          6 | uninvolved benign hosts           |                      4 |                                1 |
| MITM-ArpSpoofing     | 192.168.137.76 - 54.188.27.243    | MITM-ARP          |                443 |          6 | uninvolved benign hosts           |                      3 |                                1 |
| Recon-PortScan       | 142.251.32.67 - 192.168.137.59    | MITM-ARP          |                 80 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| SqlInjection         | 100.21.156.247 - 192.168.137.242  | MITM-ARP          |              50919 |          6 | uninvolved benign hosts           |                      2 |                                1 |
| XSS                  | 172.253.63.188 - 192.168.137.121  | MITM-ARP          |               5228 |          6 | uninvolved benign hosts           |                      1 |                                1 |
| XSS                  | 192.168.137.55 - 34.213.103.51    | MITM-ARP          |              38926 |          6 | uninvolved benign hosts           |                      2 |                                1 |

## (d) Per-class basis of the share of attack flows after block (run1 simulation)

Attack flows = live flows labelled as attack in the ten windows; after block = the flow starts (bidirectional_first_seen_ms) after its pair was blocked (block_curve.py). Contribution = class flows after block / all attack flows; contributions sum to the overall share.

|   k | MITM-ARP ignored   | class      |   attack flows |   share of attack flows |   flows after block |   class share after block |   contribution to overall share | attacker pairs blocked   |
|----:|:-------------------|:-----------|---------------:|------------------------:|--------------------:|--------------------------:|--------------------------------:|:-------------------------|
|   1 | False              | BruteForce |             28 |                  0.0001 |                  11 |                    0.3929 |                          0.0001 | 1/1                      |
|   1 | False              | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|   1 | False              | DoS-HTTP   |           2815 |                  0.0132 |                1789 |                    0.6355 |                          0.0084 | 1/1                      |
|   1 | False              | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|   1 | False              | Mirai      |             17 |                  0.0001 |                   3 |                    0.1765 |                          0      | 7/7                      |
|   1 | False              | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|   1 | False              | Web        |             15 |                  0.0001 |                   6 |                    0.4    |                          0      | 3/3                      |
|   1 | False              | ALL        |         212965 |                  1      |               23668 |                    0.1111 |                          0.1111 |                          |
|   2 | False              | BruteForce |             28 |                  0.0001 |                  11 |                    0.3929 |                          0.0001 | 1/1                      |
|   2 | False              | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|   2 | False              | DoS-HTTP   |           2815 |                  0.0132 |                1789 |                    0.6355 |                          0.0084 | 1/1                      |
|   2 | False              | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|   2 | False              | Mirai      |             17 |                  0.0001 |                   1 |                    0.0588 |                          0      | 6/7                      |
|   2 | False              | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|   2 | False              | Web        |             15 |                  0.0001 |                   3 |                    0.2    |                          0      | 3/3                      |
|   2 | False              | ALL        |         212965 |                  1      |               23663 |                    0.1111 |                          0.1111 |                          |
|   3 | False              | BruteForce |             28 |                  0.0001 |                   8 |                    0.2857 |                          0      | 1/1                      |
|   3 | False              | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|   3 | False              | DoS-HTTP   |           2815 |                  0.0132 |                1789 |                    0.6355 |                          0.0084 | 1/1                      |
|   3 | False              | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|   3 | False              | Mirai      |             17 |                  0.0001 |                   0 |                    0      |                          0      | 1/7                      |
|   3 | False              | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|   3 | False              | Web        |             15 |                  0.0001 |                   0 |                    0      |                          0      | 3/3                      |
|   3 | False              | ALL        |         212965 |                  1      |               23656 |                    0.1111 |                          0.1111 |                          |
|   5 | False              | BruteForce |             28 |                  0.0001 |                   8 |                    0.2857 |                          0      | 1/1                      |
|   5 | False              | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|   5 | False              | DoS-HTTP   |           2815 |                  0.0132 |                1789 |                    0.6355 |                          0.0084 | 1/1                      |
|   5 | False              | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|   5 | False              | Mirai      |             17 |                  0.0001 |                   0 |                    0      |                          0      | 0/7                      |
|   5 | False              | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|   5 | False              | Web        |             15 |                  0.0001 |                   0 |                    0      |                          0      | 1/3                      |
|   5 | False              | ALL        |         212965 |                  1      |               23656 |                    0.1111 |                          0.1111 |                          |
|  10 | False              | BruteForce |             28 |                  0.0001 |                   7 |                    0.25   |                          0      | 1/1                      |
|  10 | False              | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|  10 | False              | DoS-HTTP   |           2815 |                  0.0132 |                1789 |                    0.6355 |                          0.0084 | 1/1                      |
|  10 | False              | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|  10 | False              | Mirai      |             17 |                  0.0001 |                   0 |                    0      |                          0      | 0/7                      |
|  10 | False              | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|  10 | False              | Web        |             15 |                  0.0001 |                   0 |                    0      |                          0      | 0/3                      |
|  10 | False              | ALL        |         212965 |                  1      |               23655 |                    0.1111 |                          0.1111 |                          |
|  20 | False              | BruteForce |             28 |                  0.0001 |                   0 |                    0      |                          0      | 0/1                      |
|  20 | False              | DDoS-SYN   |         209001 |                  0.9814 |               21829 |                    0.1044 |                          0.1025 | 6/6                      |
|  20 | False              | DoS-HTTP   |           2815 |                  0.0132 |                1777 |                    0.6313 |                          0.0083 | 1/1                      |
|  20 | False              | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|  20 | False              | Mirai      |             17 |                  0.0001 |                   0 |                    0      |                          0      | 0/7                      |
|  20 | False              | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|  20 | False              | Web        |             15 |                  0.0001 |                   0 |                    0      |                          0      | 0/3                      |
|  20 | False              | ALL        |         212965 |                  1      |               23606 |                    0.1108 |                          0.1108 |                          |
|   1 | True               | BruteForce |             28 |                  0.0001 |                  11 |                    0.3929 |                          0.0001 | 1/1                      |
|   1 | True               | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|   1 | True               | DoS-HTTP   |           2815 |                  0.0132 |                1789 |                    0.6355 |                          0.0084 | 1/1                      |
|   1 | True               | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|   1 | True               | Mirai      |             17 |                  0.0001 |                   3 |                    0.1765 |                          0      | 7/7                      |
|   1 | True               | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|   1 | True               | Web        |             15 |                  0.0001 |                   6 |                    0.4    |                          0      | 3/3                      |
|   1 | True               | ALL        |         212965 |                  1      |               23668 |                    0.1111 |                          0.1111 |                          |
|   2 | True               | BruteForce |             28 |                  0.0001 |                  11 |                    0.3929 |                          0.0001 | 1/1                      |
|   2 | True               | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|   2 | True               | DoS-HTTP   |           2815 |                  0.0132 |                1789 |                    0.6355 |                          0.0084 | 1/1                      |
|   2 | True               | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|   2 | True               | Mirai      |             17 |                  0.0001 |                   1 |                    0.0588 |                          0      | 6/7                      |
|   2 | True               | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|   2 | True               | Web        |             15 |                  0.0001 |                   3 |                    0.2    |                          0      | 3/3                      |
|   2 | True               | ALL        |         212965 |                  1      |               23663 |                    0.1111 |                          0.1111 |                          |
|   3 | True               | BruteForce |             28 |                  0.0001 |                   8 |                    0.2857 |                          0      | 1/1                      |
|   3 | True               | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|   3 | True               | DoS-HTTP   |           2815 |                  0.0132 |                1789 |                    0.6355 |                          0.0084 | 1/1                      |
|   3 | True               | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|   3 | True               | Mirai      |             17 |                  0.0001 |                   0 |                    0      |                          0      | 1/7                      |
|   3 | True               | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|   3 | True               | Web        |             15 |                  0.0001 |                   0 |                    0      |                          0      | 3/3                      |
|   3 | True               | ALL        |         212965 |                  1      |               23656 |                    0.1111 |                          0.1111 |                          |
|   5 | True               | BruteForce |             28 |                  0.0001 |                   8 |                    0.2857 |                          0      | 1/1                      |
|   5 | True               | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|   5 | True               | DoS-HTTP   |           2815 |                  0.0132 |                1789 |                    0.6355 |                          0.0084 | 1/1                      |
|   5 | True               | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|   5 | True               | Mirai      |             17 |                  0.0001 |                   0 |                    0      |                          0      | 0/7                      |
|   5 | True               | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|   5 | True               | Web        |             15 |                  0.0001 |                   0 |                    0      |                          0      | 1/3                      |
|   5 | True               | ALL        |         212965 |                  1      |               23656 |                    0.1111 |                          0.1111 |                          |
|  10 | True               | BruteForce |             28 |                  0.0001 |                   7 |                    0.25   |                          0      | 1/1                      |
|  10 | True               | DDoS-SYN   |         209001 |                  0.9814 |               21859 |                    0.1046 |                          0.1026 | 6/6                      |
|  10 | True               | DoS-HTTP   |           2815 |                  0.0132 |                1777 |                    0.6313 |                          0.0083 | 1/1                      |
|  10 | True               | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|  10 | True               | Mirai      |             17 |                  0.0001 |                   0 |                    0      |                          0      | 0/7                      |
|  10 | True               | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|  10 | True               | Web        |             15 |                  0.0001 |                   0 |                    0      |                          0      | 0/3                      |
|  10 | True               | ALL        |         212965 |                  1      |               23643 |                    0.111  |                          0.111  |                          |
|  20 | True               | BruteForce |             28 |                  0.0001 |                   0 |                    0      |                          0      | 0/1                      |
|  20 | True               | DDoS-SYN   |         209001 |                  0.9814 |               21829 |                    0.1044 |                          0.1025 | 6/6                      |
|  20 | True               | DoS-HTTP   |           2815 |                  0.0132 |                1755 |                    0.6234 |                          0.0082 | 1/1                      |
|  20 | True               | MITM-ARP   |              8 |                  0      |                   0 |                    0      |                          0      | 0/7                      |
|  20 | True               | Mirai      |             17 |                  0.0001 |                   0 |                    0      |                          0      | 0/7                      |
|  20 | True               | Recon      |           1081 |                  0.0051 |                   0 |                    0      |                          0      | 1/1                      |
|  20 | True               | Web        |             15 |                  0.0001 |                   0 |                    0      |                          0      | 0/3                      |
|  20 | True               | ALL        |         212965 |                  1      |               23584 |                    0.1107 |                          0.1107 |                          |

Summary (k = 1, MITM-ARP counted): DDoS-SYN is 0.9814 of 212,965 attack flows; 0.1046 of its flows start after block, contributing 0.1026 of the overall 0.1111; DoS-HTTP contributes 0.0084. The six DDoS-SYN pairs are blocked at every k (column 'attacker pairs blocked'), so the overall share hardly changes with k.

