# Late blocks over the 5.9 h test periods (round 18)

Script: src/analysis/block_timing_long.py. Attack flows: 206,430 (audit-corrected labels); per-class columns give the share for that class's attack flows.

Test-period span per capture (s): Benign_Final 2808, CommandInjection 585, DDoS-SYN_Flood 23, DictionaryBruteForce 4727, DoS-HTTP_Flood 1310, MITM-ArpSpoofing 989, Mirai-udpplain 64, Recon-PortScan 9992, SqlInjection 271, XSS 518; attack flows per class: BruteForce 605, DDoS-SYN 153,402, DoS-HTTP 12,379, MITM-ARP 25, Mirai 10, Recon 39,819, Web 190

| MITM-ARP verdicts   | verdict time        | horizon    |   k |   attack flows after block |   BruteForce |   DDoS-SYN |   DoS-HTTP |   MITM-ARP |   Mirai |   Recon |   Web |
|:--------------------|:--------------------|:-----------|----:|---------------------------:|-------------:|-----------:|-----------:|-----------:|--------:|--------:|------:|
| counted             | (a) flow end        | reset 60 s |   1 |                     0.968  |        0.977 |      0.962 |      0.96  |       0.24 |     0.1 |   0.996 | 0.905 |
| counted             | (a) flow end        | reset 60 s |   3 |                     0.9654 |        0.241 |      0.961 |      0.958 |       0    |     0   |   0.995 | 0.816 |
| counted             | (a) flow end        | reset 60 s |  10 |                     0.964  |        0.129 |      0.961 |      0.958 |       0    |     0   |   0.992 | 0.626 |
| counted             | (a) flow end        | persistent |   1 |                     0.968  |        0.977 |      0.962 |      0.96  |       0.24 |     0.1 |   0.996 | 0.905 |
| counted             | (a) flow end        | persistent |   3 |                     0.9654 |        0.241 |      0.961 |      0.958 |       0    |     0   |   0.995 | 0.837 |
| counted             | (a) flow end        | persistent |  10 |                     0.9643 |        0.241 |      0.961 |      0.958 |       0    |     0   |   0.992 | 0.647 |
| counted             | (b) flow end + 15 s | reset 60 s |   1 |                     0.2034 |        0.188 |      0.072 |      0.869 |       0.24 |     0.1 |   0.5   | 0.884 |
| counted             | (b) flow end + 15 s | reset 60 s |   3 |                     0.2021 |        0.06  |      0.072 |      0.863 |       0    |     0   |   0.499 | 0.805 |
| counted             | (b) flow end + 15 s | reset 60 s |  10 |                     0.2018 |        0.058 |      0.072 |      0.863 |       0    |     0   |   0.499 | 0.468 |
| counted             | (b) flow end + 15 s | persistent |   1 |                     0.2034 |        0.188 |      0.072 |      0.869 |       0.24 |     0.1 |   0.5   | 0.884 |
| counted             | (b) flow end + 15 s | persistent |   3 |                     0.2022 |        0.06  |      0.072 |      0.863 |       0    |     0   |   0.499 | 0.816 |
| counted             | (b) flow end + 15 s | persistent |  10 |                     0.2018 |        0.058 |      0.072 |      0.863 |       0    |     0   |   0.499 | 0.468 |
| ignored             | (a) flow end        | reset 60 s |   1 |                     0.968  |        0.977 |      0.962 |      0.96  |       0    |     0.1 |   0.996 | 0.905 |
| ignored             | (a) flow end        | reset 60 s |   3 |                     0.9654 |        0.241 |      0.961 |      0.958 |       0    |     0   |   0.995 | 0.816 |
| ignored             | (a) flow end        | reset 60 s |  10 |                     0.964  |        0.129 |      0.961 |      0.958 |       0    |     0   |   0.992 | 0.626 |
| ignored             | (a) flow end        | persistent |   1 |                     0.968  |        0.977 |      0.962 |      0.96  |       0    |     0.1 |   0.996 | 0.905 |
| ignored             | (a) flow end        | persistent |   3 |                     0.9654 |        0.241 |      0.961 |      0.958 |       0    |     0   |   0.995 | 0.837 |
| ignored             | (a) flow end        | persistent |  10 |                     0.9643 |        0.241 |      0.961 |      0.958 |       0    |     0   |   0.992 | 0.647 |
| ignored             | (b) flow end + 15 s | reset 60 s |   1 |                     0.2033 |        0.188 |      0.072 |      0.869 |       0    |     0.1 |   0.5   | 0.884 |
| ignored             | (b) flow end + 15 s | reset 60 s |   3 |                     0.2021 |        0.06  |      0.072 |      0.863 |       0    |     0   |   0.499 | 0.805 |
| ignored             | (b) flow end + 15 s | reset 60 s |  10 |                     0.2018 |        0.058 |      0.072 |      0.863 |       0    |     0   |   0.499 | 0.468 |
| ignored             | (b) flow end + 15 s | persistent |   1 |                     0.2033 |        0.188 |      0.072 |      0.869 |       0    |     0.1 |   0.5   | 0.884 |
| ignored             | (b) flow end + 15 s | persistent |   3 |                     0.2022 |        0.06  |      0.072 |      0.863 |       0    |     0   |   0.499 | 0.816 |
| ignored             | (b) flow end + 15 s | persistent |  10 |                     0.2018 |        0.058 |      0.072 |      0.863 |       0    |     0   |   0.499 | 0.468 |
