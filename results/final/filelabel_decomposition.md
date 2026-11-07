# File-label FPR decomposition and leave-one-capture-out (final review M1)

Deployed edge tree {'max_depth': 32, 'min_samples_leaf': 1, 'class_weight': 'balanced', 'random_state': 0}, seed 0. Script: src/analysis/final_filelabel.py. FPR = share of Benign test flows (evidence labels on CIC-IoT2023, Zeek labels on IoT-23) predicted as any attack class. Format: rate (FP/n).

(i) = Benign flows inside attack/malware captures (the file-label model is trained on this background under the capture's attack name); (ii) = flows of benign captures (CIC: Benign_Final; IoT-23: the three benign-device captures), the only Benign class the file-label model ever sees.

## CIC-IoT2023

Benign captures: Benign_Final. Captures: 10.

### A. Temporal and stratified splits: decomposition

| split      | model                | pooled Benign FPR      | (i) background in attack captures   | (ii) benign capture(s)   |   share of FPs from (i) |
|:-----------|:---------------------|:-----------------------|:------------------------------------|:-------------------------|------------------------:|
| temporal   | file-label model     | 0.7177 (38,034/52,993) | 0.8610 (33,685/39,124)              | 0.3136 (4,349/13,869)    |                  0.8857 |
| temporal   | evidence-label model | 0.0383 (2,030/52,993)  | 0.0485 (1,897/39,124)               | 0.0096 (133/13,869)      |                  0.9345 |
| stratified | file-label model     | 0.7023 (33,939/48,323) | 0.8590 (29,610/34,471)              | 0.3125 (4,329/13,852)    |                  0.8724 |
| stratified | evidence-label model | 0.0115 (555/48,323)    | 0.0122 (421/34,471)                 | 0.0097 (134/13,852)      |                  0.7586 |

### A. Per capture

| split      | model                | capture              | group               |   Benign test flows |    FP |    FPR | top FP classes                           |
|:-----------|:---------------------|:---------------------|:--------------------|--------------------:|------:|-------:|:-----------------------------------------|
| temporal   | file-label model     | Benign_Final         | (ii) benign capture |               13869 |  4349 | 0.3136 | MITM-ARP 1236, Web 758, BruteForce 730   |
| temporal   | file-label model     | CommandInjection     | (i) attack capture  |                1660 |  1463 | 0.8813 | BruteForce 555, Web 553, Recon 114       |
| temporal   | file-label model     | DDoS-SYN_Flood       | (i) attack capture  |                 178 |   154 | 0.8652 | DDoS-SYN 34, Web 32, Recon 24            |
| temporal   | file-label model     | DictionaryBruteForce | (i) attack capture  |                2942 |  2546 | 0.8654 | BruteForce 1201, Web 710, Recon 214      |
| temporal   | file-label model     | DoS-HTTP_Flood       | (i) attack capture  |                5272 |  4990 | 0.9465 | DoS-HTTP 4075, MITM-ARP 270, Recon 213   |
| temporal   | file-label model     | MITM-ArpSpoofing     | (i) attack capture  |                3637 |  3034 | 0.8342 | MITM-ARP 1188, BruteForce 709, Web 603   |
| temporal   | file-label model     | Mirai-udpplain       | (i) attack capture  |                 185 |   170 | 0.9189 | Mirai 74, MITM-ARP 33, Recon 20          |
| temporal   | file-label model     | Recon-PortScan       | (i) attack capture  |               21700 | 18270 | 0.8419 | Recon 9197, Web 3571, MITM-ARP 2737      |
| temporal   | file-label model     | SqlInjection         | (i) attack capture  |                2078 |  1782 | 0.8576 | DoS-HTTP 1009, Web 372, BruteForce 113   |
| temporal   | file-label model     | XSS                  | (i) attack capture  |                1472 |  1276 | 0.8668 | Web 705, BruteForce 284, Mirai 105       |
| temporal   | evidence-label model | Benign_Final         | (ii) benign capture |               13869 |   133 | 0.0096 | MITM-ARP 84, DoS-HTTP 49                 |
| temporal   | evidence-label model | CommandInjection     | (i) attack capture  |                1660 |    11 | 0.0066 | MITM-ARP 10, DoS-HTTP 1                  |
| temporal   | evidence-label model | DDoS-SYN_Flood       | (i) attack capture  |                 178 |    14 | 0.0787 | DoS-HTTP 6, DDoS-SYN 3, MITM-ARP 2       |
| temporal   | evidence-label model | DictionaryBruteForce | (i) attack capture  |                2942 |    30 | 0.0102 | MITM-ARP 27, DoS-HTTP 3                  |
| temporal   | evidence-label model | DoS-HTTP_Flood       | (i) attack capture  |                5272 |  1413 | 0.268  | DoS-HTTP 1405, MITM-ARP 5, Web 2         |
| temporal   | evidence-label model | MITM-ArpSpoofing     | (i) attack capture  |                3637 |   122 | 0.0335 | MITM-ARP 103, Web 9, DoS-HTTP 6          |
| temporal   | evidence-label model | Mirai-udpplain       | (i) attack capture  |                 185 |     2 | 0.0108 | MITM-ARP 1, DoS-HTTP 1                   |
| temporal   | evidence-label model | Recon-PortScan       | (i) attack capture  |               21700 |   277 | 0.0128 | MITM-ARP 160, DoS-HTTP 101, Web 16       |
| temporal   | evidence-label model | SqlInjection         | (i) attack capture  |                2078 |    13 | 0.0063 | MITM-ARP 11, DoS-HTTP 2                  |
| temporal   | evidence-label model | XSS                  | (i) attack capture  |                1472 |    15 | 0.0102 | MITM-ARP 12, DoS-HTTP 3                  |
| stratified | file-label model     | Benign_Final         | (ii) benign capture |               13852 |  4329 | 0.3125 | MITM-ARP 1178, BruteForce 822, Web 799   |
| stratified | file-label model     | CommandInjection     | (i) attack capture  |                1726 |  1546 | 0.8957 | Web 758, BruteForce 456, MITM-ARP 123    |
| stratified | file-label model     | DDoS-SYN_Flood       | (i) attack capture  |                 133 |   121 | 0.9098 | MITM-ARP 29, DDoS-SYN 27, DoS-HTTP 17    |
| stratified | file-label model     | DictionaryBruteForce | (i) attack capture  |                3135 |  2766 | 0.8823 | BruteForce 1681, Web 380, MITM-ARP 283   |
| stratified | file-label model     | DoS-HTTP_Flood       | (i) attack capture  |                3664 |  3355 | 0.9157 | DoS-HTTP 2686, Web 218, MITM-ARP 152     |
| stratified | file-label model     | MITM-ArpSpoofing     | (i) attack capture  |                3608 |  3089 | 0.8562 | MITM-ARP 1831, Recon 371, BruteForce 345 |
| stratified | file-label model     | Mirai-udpplain       | (i) attack capture  |                 194 |   173 | 0.8918 | Mirai 105, MITM-ARP 20, Web 19           |
| stratified | file-label model     | Recon-PortScan       | (i) attack capture  |               18433 | 15444 | 0.8378 | Recon 9573, Web 1993, MITM-ARP 1819      |
| stratified | file-label model     | SqlInjection         | (i) attack capture  |                2061 |  1784 | 0.8656 | Web 1109, Recon 232, MITM-ARP 168        |
| stratified | file-label model     | XSS                  | (i) attack capture  |                1517 |  1332 | 0.878  | Web 710, BruteForce 285, MITM-ARP 128    |
| stratified | evidence-label model | Benign_Final         | (ii) benign capture |               13852 |   134 | 0.0097 | MITM-ARP 117, DoS-HTTP 11, Web 5         |
| stratified | evidence-label model | CommandInjection     | (i) attack capture  |                1726 |    15 | 0.0087 | MITM-ARP 10, DoS-HTTP 3, DDoS-SYN 1      |
| stratified | evidence-label model | DDoS-SYN_Flood       | (i) attack capture  |                 133 |     4 | 0.0301 | DoS-HTTP 2, Recon 1, MITM-ARP 1          |
| stratified | evidence-label model | DictionaryBruteForce | (i) attack capture  |                3135 |    29 | 0.0093 | MITM-ARP 23, DoS-HTTP 3, BruteForce 2    |
| stratified | evidence-label model | DoS-HTTP_Flood       | (i) attack capture  |                3664 |   120 | 0.0328 | DoS-HTTP 103, MITM-ARP 12, Web 3         |
| stratified | evidence-label model | MITM-ArpSpoofing     | (i) attack capture  |                3608 |    74 | 0.0205 | MITM-ARP 66, DoS-HTTP 5, Web 2           |
| stratified | evidence-label model | Mirai-udpplain       | (i) attack capture  |                 194 |     3 | 0.0155 | DoS-HTTP 2, MITM-ARP 1                   |
| stratified | evidence-label model | Recon-PortScan       | (i) attack capture  |               18433 |   135 | 0.0073 | MITM-ARP 88, DoS-HTTP 34, Web 12         |
| stratified | evidence-label model | SqlInjection         | (i) attack capture  |                2061 |    22 | 0.0107 | MITM-ARP 17, DoS-HTTP 4, Web 1           |
| stratified | evidence-label model | XSS                  | (i) attack capture  |                1517 |    19 | 0.0125 | MITM-ARP 16, DoS-HTTP 2, Web 1           |

### B. Leave-one-capture-out (train on all flows of the other captures)

| held-out capture     | group               | file label   |   Benign flows in held-out capture | FPR file-label model                 | top FP classes (file-label)   |   FPR evidence-label model | top FP classes (evidence-label)   |
|:---------------------|:--------------------|:-------------|-----------------------------------:|:-------------------------------------|:------------------------------|---------------------------:|:----------------------------------|
| Benign_Final         | (ii) benign capture | Benign       |                              46231 | 1.0000 (no Benign class in training) | Recon 15908, Web 10242        |                     0.0152 | MITM-ARP 597, DoS-HTTP 83         |
| CommandInjection     | (i) attack capture  | Web          |                               5541 | 0.8775                               | BruteForce 1889, Web 1350     |                     0.0105 | MITM-ARP 46, DoS-HTTP 9           |
| DDoS-SYN_Flood       | (i) attack capture  | DDoS-SYN     |                                409 | 0.8704                               | MITM-ARP 73, Web 71           |                     0.0538 | DoS-HTTP 13, MITM-ARP 4           |
| DictionaryBruteForce | (i) attack capture  | BruteForce   |                              10744 | 0.8417                               | Web 3978, MITM-ARP 1845       |                     0.0127 | MITM-ARP 113, DoS-HTTP 21         |
| DoS-HTTP_Flood       | (i) attack capture  | DoS-HTTP     |                              11791 | 0.7929                               | Web 4365, Recon 2962          |                     0.0123 | MITM-ARP 70, BruteForce 47        |
| MITM-ArpSpoofing     | (i) attack capture  | MITM-ARP     |                              11910 | 0.7141                               | Recon 2999, Web 2283          |                     0.0051 | Web 31, DoS-HTTP 25               |
| Mirai-udpplain       | (i) attack capture  | Mirai        |                                612 | 0.8023                               | Web 170, MITM-ARP 137         |                     0.0114 | MITM-ARP 5, DoS-HTTP 2            |
| Recon-PortScan       | (i) attack capture  | Recon        |                              61921 | 0.7300                               | Web 23328, MITM-ARP 8678      |                     0.0145 | MITM-ARP 606, DoS-HTTP 244        |
| SqlInjection         | (i) attack capture  | Web          |                               7002 | 0.8599                               | Recon 2458, DoS-HTTP 1361     |                     0.0111 | MITM-ARP 66, DoS-HTTP 8           |
| XSS                  | (i) attack capture  | Web          |                               4915 | 0.8163                               | BruteForce 1382, Web 1335     |                     0.0124 | MITM-ARP 50, DoS-HTTP 10          |

CIC-IoT2023 has one Benign capture. Holding it out removes every file-label Benign training flow, so the file-label model cannot predict Benign at all (FPR 1 by construction); the evidence-label model still learns Benign from the background of the attack captures.

## IoT-23

Benign captures: CTU-Honeypot-Capture-4-1, CTU-Honeypot-Capture-5-1, CTU-Honeypot-Capture-7-1-Somfy-01. Captures: 10.

### A. Temporal and stratified splits: decomposition

| split      | model            | pooled Benign FPR        | (i) background in attack captures   | (ii) benign capture(s)   |   share of FPs from (i) |
|:-----------|:-----------------|:-------------------------|:------------------------------------|:-------------------------|------------------------:|
| temporal   | file-label model | 0.9847 (141,590/143,796) | 0.9997 (141,483/141,525)            | 0.0471 (107/2,271)       |                  0.9992 |
| temporal   | Zeek-label model | 0.0340 (4,884/143,796)   | 0.0345 (4,880/141,525)              | 0.0018 (4/2,271)         |                  0.9992 |
| stratified | file-label model | 0.9840 (138,323/140,573) | 0.9995 (138,261/138,330)            | 0.0276 (62/2,243)        |                  0.9996 |
| stratified | Zeek-label model | 0.0368 (5,170/140,573)   | 0.0372 (5,152/138,330)              | 0.0080 (18/2,243)        |                  0.9965 |

### A. Per capture

| split      | model            | capture                           | group               |   Benign test flows |     FP |    FPR | top FP classes                      |
|:-----------|:-----------------|:----------------------------------|:--------------------|--------------------:|-------:|-------:|:------------------------------------|
| temporal   | file-label model | CTU-Honeypot-Capture-4-1          | (ii) benign capture |                1373 |      9 | 0.0066 | C&C 5, DDoS 2, PortScan 2           |
| temporal   | file-label model | CTU-Honeypot-Capture-5-1          | (ii) benign capture |                 802 |     97 | 0.1209 | PortScan 58, C&C 38, DDoS 1         |
| temporal   | file-label model | CTU-Honeypot-Capture-7-1-Somfy-01 | (ii) benign capture |                  96 |      1 | 0.0104 | PortScan 1                          |
| temporal   | file-label model | CTU-IoT-Malware-Capture-1-1       | (i) attack capture  |              136828 | 136827 | 1      | PortScan 135491, C&C 1334, DDoS 2   |
| temporal   | file-label model | CTU-IoT-Malware-Capture-20-1      | (i) attack capture  |                 938 |    930 | 0.9915 | C&C 842, DDoS 80, PortScan 8        |
| temporal   | file-label model | CTU-IoT-Malware-Capture-21-1      | (i) attack capture  |                 829 |    824 | 0.994  | C&C 801, DDoS 19, PortScan 4        |
| temporal   | file-label model | CTU-IoT-Malware-Capture-3-1       | (i) attack capture  |                 832 |    809 | 0.9724 | PortScan 687, DDoS 72, C&C 50       |
| temporal   | file-label model | CTU-IoT-Malware-Capture-34-1      | (i) attack capture  |                 172 |    172 | 1      | C&C 160, DDoS 11, FileDownload 1    |
| temporal   | file-label model | CTU-IoT-Malware-Capture-42-1      | (i) attack capture  |                1279 |   1274 | 0.9961 | C&C 723, FileDownload 305, DDoS 237 |
| temporal   | file-label model | CTU-IoT-Malware-Capture-8-1       | (i) attack capture  |                 647 |    647 | 1      | C&C 505, DDoS 142                   |
| temporal   | Zeek-label model | CTU-Honeypot-Capture-4-1          | (ii) benign capture |                1373 |      1 | 0.0007 | C&C 1                               |
| temporal   | Zeek-label model | CTU-Honeypot-Capture-5-1          | (ii) benign capture |                 802 |      3 | 0.0037 | C&C 3                               |
| temporal   | Zeek-label model | CTU-Honeypot-Capture-7-1-Somfy-01 | (ii) benign capture |                  96 |      0 | 0      |                                     |
| temporal   | Zeek-label model | CTU-IoT-Malware-Capture-1-1       | (i) attack capture  |              136828 |   4410 | 0.0322 | PortScan 4410                       |
| temporal   | Zeek-label model | CTU-IoT-Malware-Capture-20-1      | (i) attack capture  |                 938 |      0 | 0      |                                     |
| temporal   | Zeek-label model | CTU-IoT-Malware-Capture-21-1      | (i) attack capture  |                 829 |      0 | 0      |                                     |
| temporal   | Zeek-label model | CTU-IoT-Malware-Capture-3-1       | (i) attack capture  |                 832 |    210 | 0.2524 | PortScan 203, Attack 4, C&C 3       |
| temporal   | Zeek-label model | CTU-IoT-Malware-Capture-34-1      | (i) attack capture  |                 172 |      0 | 0      |                                     |
| temporal   | Zeek-label model | CTU-IoT-Malware-Capture-42-1      | (i) attack capture  |                1279 |    260 | 0.2033 | C&C 259, Attack 1                   |
| temporal   | Zeek-label model | CTU-IoT-Malware-Capture-8-1       | (i) attack capture  |                 647 |      0 | 0      |                                     |
| stratified | file-label model | CTU-Honeypot-Capture-4-1          | (ii) benign capture |                1338 |      2 | 0.0015 | C&C 1, FileDownload 1               |
| stratified | file-label model | CTU-Honeypot-Capture-5-1          | (ii) benign capture |                 826 |     56 | 0.0678 | C&C 36, PortScan 11, DDoS 8         |
| stratified | file-label model | CTU-Honeypot-Capture-7-1-Somfy-01 | (ii) benign capture |                  79 |      4 | 0.0506 | C&C 2, PortScan 2                   |
| stratified | file-label model | CTU-IoT-Malware-Capture-1-1       | (i) attack capture  |              132379 | 132369 | 0.9999 | PortScan 130185, C&C 2080, DDoS 100 |
| stratified | file-label model | CTU-IoT-Malware-Capture-20-1      | (i) attack capture  |                 942 |    929 | 0.9862 | C&C 829, DDoS 71, FileDownload 18   |
| stratified | file-label model | CTU-IoT-Malware-Capture-21-1      | (i) attack capture  |                 987 |    986 | 0.999  | C&C 949, DDoS 21, FileDownload 12   |
| stratified | file-label model | CTU-IoT-Malware-Capture-3-1       | (i) attack capture  |                1489 |   1453 | 0.9758 | PortScan 1269, C&C 110, DDoS 66     |
| stratified | file-label model | CTU-IoT-Malware-Capture-34-1      | (i) attack capture  |                 556 |    552 | 0.9928 | C&C 446, DDoS 87, FileDownload 13   |
| stratified | file-label model | CTU-IoT-Malware-Capture-42-1      | (i) attack capture  |                1298 |   1293 | 0.9961 | FileDownload 853, C&C 273, DDoS 163 |
| stratified | file-label model | CTU-IoT-Malware-Capture-8-1       | (i) attack capture  |                 679 |    679 | 1      | C&C 678, DDoS 1                     |
| stratified | Zeek-label model | CTU-Honeypot-Capture-4-1          | (ii) benign capture |                1338 |      0 | 0      |                                     |
| stratified | Zeek-label model | CTU-Honeypot-Capture-5-1          | (ii) benign capture |                 826 |     18 | 0.0218 | PortScan 16, C&C 1, FileDownload 1  |
| stratified | Zeek-label model | CTU-Honeypot-Capture-7-1-Somfy-01 | (ii) benign capture |                  79 |      0 | 0      |                                     |
| stratified | Zeek-label model | CTU-IoT-Malware-Capture-1-1       | (i) attack capture  |              132379 |   4461 | 0.0337 | PortScan 4417, C&C 44               |
| stratified | Zeek-label model | CTU-IoT-Malware-Capture-20-1      | (i) attack capture  |                 942 |      0 | 0      |                                     |
| stratified | Zeek-label model | CTU-IoT-Malware-Capture-21-1      | (i) attack capture  |                 987 |      0 | 0      |                                     |
| stratified | Zeek-label model | CTU-IoT-Malware-Capture-3-1       | (i) attack capture  |                1489 |    466 | 0.313  | PortScan 437, C&C 27, Attack 2      |
| stratified | Zeek-label model | CTU-IoT-Malware-Capture-34-1      | (i) attack capture  |                 556 |     16 | 0.0288 | DDoS 7, C&C 7, FileDownload 1       |
| stratified | Zeek-label model | CTU-IoT-Malware-Capture-42-1      | (i) attack capture  |                1298 |    209 | 0.161  | C&C 209                             |
| stratified | Zeek-label model | CTU-IoT-Malware-Capture-8-1       | (i) attack capture  |                 679 |      0 | 0      |                                     |

### B. Leave-one-capture-out (train on all flows of the other captures)

| held-out capture                  | group               | file label   |   Benign flows in held-out capture |   FPR file-label model | top FP classes (file-label)   |   FPR Zeek-label model | top FP classes (Zeek-label)   |
|:----------------------------------|:--------------------|:-------------|-----------------------------------:|-----------------------:|:------------------------------|-----------------------:|:------------------------------|
| CTU-Honeypot-Capture-4-1          | (ii) benign capture | Benign       |                               4577 |                 0.2342 | FileDownload 773, C&C 133     |                 0.1584 | C&C 629, PortScan 88          |
| CTU-Honeypot-Capture-5-1          | (ii) benign capture | Benign       |                               2676 |                 0.4387 | PortScan 620, C&C 356         |                 0.1749 | C&C 193, PortScan 158         |
| CTU-Honeypot-Capture-7-1-Somfy-01 | (ii) benign capture | Benign       |                                321 |                 0.4673 | PortScan 111, C&C 38          |                 0      |                               |
| CTU-IoT-Malware-Capture-1-1       | (i) attack capture  | PortScan     |                             441292 |                 0.0941 | C&C 22002, PortScan 9334      |                 0.0331 | C&C 14357, PortScan 236       |
| CTU-IoT-Malware-Capture-20-1      | (i) attack capture  | C&C          |                               3209 |                 0.9891 | C&C 1724, FileDownload 884    |                 0      |                               |
| CTU-IoT-Malware-Capture-21-1      | (i) attack capture  | C&C          |                               3293 |                 0.9936 | FileDownload 1609, C&C 1585   |                 0.0003 | Attack 1                      |
| CTU-IoT-Malware-Capture-3-1       | (i) attack capture  | PortScan     |                               4865 |                 0.8898 | PortScan 3590, DDoS 374       |                 0.4913 | PortScan 2367, C&C 23         |
| CTU-IoT-Malware-Capture-34-1      | (i) attack capture  | DDoS         |                               1901 |                 0.9811 | C&C 1757, FileDownload 64     |                 0.0147 | C&C 28                        |
| CTU-IoT-Malware-Capture-42-1      | (i) attack capture  | FileDownload |                               4260 |                 0.6448 | DDoS 1829, C&C 878            |                 0.42   | C&C 1473, PortScan 314        |
| CTU-IoT-Malware-Capture-8-1       | (i) attack capture  | C&C          |                               2181 |                 0.9995 | C&C 1366, FileDownload 470    |                 0      |                               |

