# Coarse-cluster sign and permutation tests, random minus temporal (final review M3)

Script: src/analysis/final_sign_test.py. Per cluster: macro-F1 over the classes present in the cluster's test flows in both splits; difference = random (stratified 70/30, seed 0) minus temporal. Exact two-sided sign test (ties dropped) and exact sign-flip permutation test of the mean difference.

## Summary

| cluster unit    | tree                           |   clusters tested | positive / non-zero   |   mean diff |   median diff |   sign test p (two-sided) |   permutation p (two-sided) |
|:----------------|:-------------------------------|------------------:|:----------------------|------------:|--------------:|--------------------------:|----------------------------:|
| capture         | decision tree (Table perclass) |                10 | 7 / 10                |      0.0661 |        0.0054 |                    0.3438 |                      0.1895 |
| capture         | deployed edge tree             |                10 | 6 / 9                 |      0.0659 |        0.0071 |                    0.5078 |                      0.1758 |
| attacker host   | decision tree (Table perclass) |                19 | 4 / 8                 |      0.0972 |        0      |                    1      |                      0.3125 |
| attacker host   | deployed edge tree             |                19 | 4 / 8                 |      0.0967 |        0      |                    1      |                      0.3281 |
| attacker device | decision tree (Table perclass) |                15 | 4 / 5                 |      0.1118 |        0      |                    0.375  |                      0.1875 |
| attacker device | deployed edge tree             |                15 | 4 / 5                 |      0.1113 |        0      |                    0.375  |                      0.1875 |

With n non-zero clusters the smallest attainable two-sided sign-test p is 2 * 0.5^n (n = 10: 0.002; n = 5: 0.0625).

## capture, decision tree (Table perclass)

| cluster                                        |   temporal flows |   random flows | classes (both splits)   |   temporal macro-F1 |   random macro-F1 |   random - temporal |
|:-----------------------------------------------|-----------------:|---------------:|:------------------------|--------------------:|------------------:|--------------------:|
| Benign_Final/BenignTraffic3.pcap               |            13869 |          13852 | Benign                  |              0.9952 |            0.9953 |              0.0001 |
| CommandInjection/CommandInjection.pcap         |             1691 |           1753 | Benign, Web             |              0.9634 |            0.9258 |             -0.0376 |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap           |           153580 |         153591 | Benign, DDoS-SYN        |              0.981  |            0.9904 |              0.0094 |
| DictionaryBruteForce/DictionaryBruteForce.pcap |             3547 |           3459 | Benign, BruteForce      |              0.5059 |            0.9963 |              0.4904 |
| DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap            |            15382 |          15509 | Benign, DoS-HTTP        |              0.8791 |            0.9819 |              0.1028 |
| MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap        |             3662 |           3698 | Benign, MITM-ARP        |              0.5208 |            0.6302 |              0.1094 |
| Mirai-udpplain/Mirai-udpplain24.pcap           |              195 |            206 | Benign, Mirai           |              0.971  |            0.9961 |              0.0251 |
| Recon-PortScan/Recon-PortScan.pcap             |            61519 |          61376 | Benign, Recon           |              0.9968 |            0.9982 |              0.0014 |
| SqlInjection/SqlInjection.pcap                 |             2214 |           2177 | Benign, Web             |              0.9783 |            0.9718 |             -0.0065 |
| XSS/XSS.pcap                                   |             1497 |           1541 | Benign, Web             |              0.9871 |            0.953  |             -0.034  |

## capture, deployed edge tree

| cluster                                        |   temporal flows |   random flows | classes (both splits)   |   temporal macro-F1 |   random macro-F1 |   random - temporal |
|:-----------------------------------------------|-----------------:|---------------:|:------------------------|--------------------:|------------------:|--------------------:|
| Benign_Final/BenignTraffic3.pcap               |            13869 |          13852 | Benign                  |              0.9952 |            0.9951 |             -0      |
| CommandInjection/CommandInjection.pcap         |             1691 |           1753 | Benign, Web             |              0.9634 |            0.9258 |             -0.0376 |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap           |           153580 |         153591 | Benign, DDoS-SYN        |              0.9795 |            0.9924 |              0.0128 |
| DictionaryBruteForce/DictionaryBruteForce.pcap |             3547 |           3459 | Benign, BruteForce      |              0.5059 |            0.9961 |              0.4903 |
| DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap            |            15382 |          15509 | Benign, DoS-HTTP        |              0.8799 |            0.9809 |              0.1011 |
| MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap        |             3662 |           3698 | Benign, MITM-ARP        |              0.5203 |            0.6237 |              0.1034 |
| Mirai-udpplain/Mirai-udpplain24.pcap           |              195 |            206 | Benign, Mirai           |              0.9696 |            0.9961 |              0.0265 |
| Recon-PortScan/Recon-PortScan.pcap             |            61519 |          61376 | Benign, Recon           |              0.9968 |            0.9981 |              0.0013 |
| SqlInjection/SqlInjection.pcap                 |             2214 |           2177 | Benign, Web             |              0.9763 |            0.9718 |             -0.0045 |
| XSS/XSS.pcap                                   |             1497 |           1541 | Benign, Web             |              0.9871 |            0.953  |             -0.034  |

## attacker host, decision tree (Table perclass)

| cluster                                                       |   temporal flows |   random flows | classes (both splits)   |   temporal macro-F1 |   random macro-F1 |   random - temporal |
|:--------------------------------------------------------------|-----------------:|---------------:|:------------------------|--------------------:|------------------:|--------------------:|
| CommandInjection/CommandInjection.pcap|192.168.137.147        |               42 |             46 | Benign, Web             |              0.9055 |            0.8676 |             -0.0379 |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.153          |             7931 |          22890 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.201          |              206 |          19792 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.34           |            18307 |          26529 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.36           |            65525 |          19818 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.87           |            27585 |          21257 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.99           |            33848 |          43172 | DDoS-SYN                |              1      |            1      |              0      |
| DictionaryBruteForce/DictionaryBruteForce.pcap|192.168.137.65 |              630 |            342 | Benign, BruteForce      |              0.0928 |            1      |              0.9072 |
| DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap|192.168.137.66            |            12400 |          12564 | Benign, DoS-HTTP        |              0.735  |            0.9408 |              0.2058 |
| MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap|192.168.137.65        |               60 |            123 | Benign, MITM-ARP        |              0.4665 |            0.4323 |             -0.0342 |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.106          |                1 |              3 | Mirai                   |              1      |            1      |              0      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.128          |                1 |              2 | Mirai                   |              0      |            1      |              1      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.147          |                2 |              1 | Mirai                   |              1      |            1      |              0      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.162          |                2 |              5 | Mirai                   |              1      |            1      |              0      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.207          |                0 |              2 |                         |            nan      |          nan      |            nan      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.238          |                3 |              2 | Mirai                   |              1      |            1      |              0      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.247          |                1 |              1 | Mirai                   |              1      |            1      |              0      |
| Recon-PortScan/Recon-PortScan.pcap|192.168.137.178            |            39820 |          42944 | Benign, Recon           |              1      |            0.8333 |             -0.1667 |
| SqlInjection/SqlInjection.pcap|192.168.137.178                |              146 |            126 | Benign, Web             |              0.8257 |            0.8478 |              0.0221 |
| XSS/XSS.pcap|192.168.137.147                                  |               37 |             34 | Benign, Web             |              0.9698 |            0.9212 |             -0.0486 |

## attacker host, deployed edge tree

| cluster                                                       |   temporal flows |   random flows | classes (both splits)   |   temporal macro-F1 |   random macro-F1 |   random - temporal |
|:--------------------------------------------------------------|-----------------:|---------------:|:------------------------|--------------------:|------------------:|--------------------:|
| CommandInjection/CommandInjection.pcap|192.168.137.147        |               42 |             46 | Benign, Web             |              0.9055 |            0.8676 |             -0.0379 |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.153          |             7931 |          22890 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.201          |              206 |          19792 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.34           |            18307 |          26529 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.36           |            65525 |          19818 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.87           |            27585 |          21257 | DDoS-SYN                |              1      |            1      |              0      |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap|192.168.137.99           |            33848 |          43172 | DDoS-SYN                |              1      |            1      |              0      |
| DictionaryBruteForce/DictionaryBruteForce.pcap|192.168.137.65 |              630 |            342 | Benign, BruteForce      |              0.0928 |            1      |              0.9072 |
| DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap|192.168.137.66            |            12400 |          12564 | Benign, DoS-HTTP        |              0.7373 |            0.9392 |              0.2019 |
| MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap|192.168.137.65        |               60 |            123 | Benign, MITM-ARP        |              0.4665 |            0.4239 |             -0.0426 |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.106          |                1 |              3 | Mirai                   |              1      |            1      |              0      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.128          |                1 |              2 | Mirai                   |              0      |            1      |              1      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.147          |                2 |              1 | Mirai                   |              1      |            1      |              0      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.162          |                2 |              5 | Mirai                   |              1      |            1      |              0      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.207          |                0 |              2 |                         |            nan      |          nan      |            nan      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.238          |                3 |              2 | Mirai                   |              1      |            1      |              0      |
| Mirai-udpplain/Mirai-udpplain24.pcap|192.168.137.247          |                1 |              1 | Mirai                   |              1      |            1      |              0      |
| Recon-PortScan/Recon-PortScan.pcap|192.168.137.178            |            39820 |          42944 | Benign, Recon           |              1      |            0.8333 |             -0.1667 |
| SqlInjection/SqlInjection.pcap|192.168.137.178                |              146 |            126 | Benign, Web             |              0.8238 |            0.8478 |              0.0241 |
| XSS/XSS.pcap|192.168.137.147                                  |               37 |             34 | Benign, Web             |              0.9698 |            0.9212 |             -0.0486 |

## attacker device, decision tree (Table perclass)

| cluster         |   temporal flows |   random flows | classes (both splits)        |   temporal macro-F1 |   random macro-F1 |   random - temporal |
|:----------------|-----------------:|---------------:|:-----------------------------|--------------------:|------------------:|--------------------:|
| 192.168.137.106 |                1 |              3 | Mirai                        |              1      |            1      |              0      |
| 192.168.137.128 |                1 |              2 | Mirai                        |              0      |            1      |              1      |
| 192.168.137.147 |               81 |             81 | Benign, Mirai, Web           |              0.9578 |            0.9275 |             -0.0303 |
| 192.168.137.153 |             7931 |          22890 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.162 |                2 |              5 | Mirai                        |              1      |            1      |              0      |
| 192.168.137.178 |            39966 |          43070 | Benign, Recon, Web           |              0.8905 |            0.8961 |              0.0056 |
| 192.168.137.201 |              206 |          19792 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.207 |                0 |              2 |                              |            nan      |          nan      |            nan      |
| 192.168.137.238 |                3 |              2 | Mirai                        |              1      |            1      |              0      |
| 192.168.137.247 |                1 |              1 | Mirai                        |              1      |            1      |              0      |
| 192.168.137.34  |            18307 |          26529 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.36  |            65525 |          19818 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.65  |              690 |            465 | Benign, BruteForce, MITM-ARP |              0.1664 |            0.6627 |              0.4963 |
| 192.168.137.66  |            12400 |          12564 | Benign, DoS-HTTP             |              0.735  |            0.9408 |              0.2058 |
| 192.168.137.87  |            27585 |          21257 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.99  |            33848 |          43172 | DDoS-SYN                     |              1      |            1      |              0      |

## attacker device, deployed edge tree

| cluster         |   temporal flows |   random flows | classes (both splits)        |   temporal macro-F1 |   random macro-F1 |   random - temporal |
|:----------------|-----------------:|---------------:|:-----------------------------|--------------------:|------------------:|--------------------:|
| 192.168.137.106 |                1 |              3 | Mirai                        |              1      |            1      |              0      |
| 192.168.137.128 |                1 |              2 | Mirai                        |              0      |            1      |              1      |
| 192.168.137.147 |               81 |             81 | Benign, Mirai, Web           |              0.9578 |            0.9275 |             -0.0303 |
| 192.168.137.153 |             7931 |          22890 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.162 |                2 |              5 | Mirai                        |              1      |            1      |              0      |
| 192.168.137.178 |            39966 |          43070 | Benign, Recon, Web           |              0.8892 |            0.8961 |              0.0069 |
| 192.168.137.201 |              206 |          19792 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.207 |                0 |              2 |                              |            nan      |          nan      |            nan      |
| 192.168.137.238 |                3 |              2 | Mirai                        |              1      |            1      |              0      |
| 192.168.137.247 |                1 |              1 | Mirai                        |              1      |            1      |              0      |
| 192.168.137.34  |            18307 |          26529 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.36  |            65525 |          19818 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.65  |              690 |            465 | Benign, BruteForce, MITM-ARP |              0.1664 |            0.6571 |              0.4907 |
| 192.168.137.66  |            12400 |          12564 | Benign, DoS-HTTP             |              0.7373 |            0.9392 |              0.2019 |
| 192.168.137.87  |            27585 |          21257 | DDoS-SYN                     |              1      |            1      |              0      |
| 192.168.137.99  |            33848 |          43172 | DDoS-SYN                     |              1      |            1      |              0      |

