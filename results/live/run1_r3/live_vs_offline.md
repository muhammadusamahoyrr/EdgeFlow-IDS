# Live vs offline on unseen windows (run1_r3)

Model `decision_tree.pkl` · CPU quota none · replay speed x1.0
Macro-F1 offline **0.804** [0.710, 0.845] vs live **0.804** [0.705, 0.844] (148,779 / 190,585 flows)
Inference: batch p50 0.72 ms (p95 1.21 ms), median batch size 198, amortised 0.0050 ms/flow
NFStream counters (whole run): processed 1157650, dropped by kernel 0, ignored 3545

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Benign_Final | 117.96 / 0.586 | 253 / 261 | 1.0074 | 0 / 0 | None / None | 0.0192 | 15.6 | None | 0 | 2.8 / 91.0 | 401.4 |
| CommandInjection | 38.11 / 0.093 | 259 / 252 | 0.9919 | 5 / 5 | 1.0 / 1.0 | 0.0162 | 15.6 | 24.7 | 0 | 0.8 / 3.0 | 401.4 |
| DDoS-SYN_Flood | 10935.62 / 5.27 | 142,724 / 184,483 | 1.0 | 142,554 / 184,308 | 1.0 / 1.0 | 0.0743 | 34.0 | 15.3 | 0 | 132.3 / 211.0 | 980.0 |
| DictionaryBruteForce | 51.06 / 0.056 | 300 / 300 | 1.0 | 25 / 25 | 0.64 / 0.64 | 0.0073 | 15.6 | 29.9 | 0 | 1.2 / 3.0 | 810.9 |
| DoS-HTTP_Flood | 654.94 / 3.83 | 2,398 / 2,451 | 1.0 | 1,871 / 1,924 | 0.954 / 0.963 | 0.0285 | 15.3 | 15.6 | 0 | 4.1 / 10.0 | 809.9 |
| MITM-ArpSpoofing | 362.15 / 3.2 | 412 / 415 | 0.9977 | 2 / 2 | 0.0 / 0.0 | 0.0266 | 15.4 | None | 3 | 1.8 / 5.0 | 809.9 |
| Mirai-udpplain | 3566.92 / 15.72 | 173 / 171 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.1 | 32.4 | 0 | 4.8 / 8.0 | 809.0 |
| Recon-PortScan | 92.66 / 0.095 | 1,572 / 1,573 | 1.0 | 1,081 / 1,081 | 1.0 / 1.0 | 0.0081 | 15.5 | 15.3 | 0 | 2.5 / 10.0 | 808.1 |
| SqlInjection | 58.92 / 0.089 | 464 / 464 | 1.0 | 4 / 4 | 1.0 / 1.0 | 0.0043 | 15.6 | 34.9 | 0 | 1.7 / 5.0 | 808.1 |
| XSS | 33.1 / 0.064 | 224 / 215 | 0.9924 | 3 / 3 | 1.0 / 1.0 | 0.0094 | 15.6 | 35.0 | 0 | 1.2 / 3.0 | 808.1 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.97 / 0.982 / 0.976 (3230) | 0.974 / 0.982 / 0.978 (3229) |
| BruteForce | 1.0 / 0.64 / 0.78 (25) | 1.0 / 0.64 / 0.78 (25) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (184308) |
| DoS-HTTP | 0.988 / 0.954 / 0.971 (1871) | 0.986 / 0.962 / 0.974 (1924) |
| MITM-ARP | 0.0 / 0.0 / 0.0 (2) | 0.0 / 0.0 / 0.0 (2) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
| Recon | 0.984 / 1.0 / 0.992 (1081) | 0.985 / 1.0 / 0.992 (1081) |
| Web | 0.923 / 1.0 / 0.96 (12) | 0.923 / 1.0 / 0.96 (12) |

ARP alerts:

- gateway_ip_spoof dc:a6:32:dc:27:d5 ['192.168.137.1', '3c:18:a0:41:c3:a0']
- ip_rebound_to_new_mac dc:a6:32:dc:27:d5 ['192.168.137.1', '3c:18:a0:41:c3:a0']
- ip_rebound_to_new_mac 3c:18:a0:41:c3:a0 ['192.168.137.1', 'dc:a6:32:dc:27:d5']
