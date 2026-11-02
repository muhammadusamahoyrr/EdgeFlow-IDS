# Live vs offline on unseen windows (run1_r2)

Model `decision_tree.pkl` · CPU quota none · replay speed x1.0
Macro-F1 offline **0.804** [0.710, 0.845] vs live **0.804** [0.717, 0.843] (148,779 / 166,327 flows)
Inference: batch p50 0.67 ms (p95 1.15 ms), median batch size 194, amortised 0.0048 ms/flow
NFStream counters (whole run): processed 1158296, dropped by kernel 0, ignored 3543

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Benign_Final | 117.0 / 0.582 | 253 / 261 | 1.0046 | 0 / 0 | None / None | 0.023 | 15.5 | None | 0 | 1.9 / 43.0 | 400.6 |
| CommandInjection | 38.12 / 0.093 | 259 / 252 | 0.9919 | 5 / 5 | 1.0 / 1.0 | 0.0162 | 15.6 | 24.9 | 0 | 0.8 / 2.0 | 400.7 |
| DDoS-SYN_Flood | 11611.28 / 5.6 | 142,724 / 160,242 | 1.0 | 142,554 / 160,068 | 1.0 / 1.0 | 0.0862 | 30.9 | 15.2 | 0 | 128.6 / 216.0 | 1007.3 |
| DictionaryBruteForce | 51.06 / 0.056 | 300 / 300 | 1.0 | 25 / 25 | 0.64 / 0.64 | 0.0109 | 15.6 | 29.8 | 0 | 1.2 / 4.0 | 827.4 |
| DoS-HTTP_Flood | 667.43 / 3.91 | 2,398 / 2,429 | 1.0 | 1,871 / 1,902 | 0.954 / 0.958 | 0.0285 | 15.4 | 16.0 | 0 | 3.6 / 10.0 | 822.5 |
| MITM-ArpSpoofing | 277.25 / 2.45 | 412 / 421 | 0.9977 | 2 / 2 | 0.0 / 0.0 | 0.0286 | 15.5 | None | 3 | 1.8 / 8.0 | 822.5 |
| Mirai-udpplain | 3578.53 / 15.77 | 173 / 171 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.2 | 32.1 | 0 | 4.4 / 7.0 | 821.5 |
| Recon-PortScan | 94.98 / 0.098 | 1,572 / 1,572 | 1.0 | 1,081 / 1,081 | 1.0 / 1.0 | 0.0081 | 15.6 | 15.8 | 0 | 2.1 / 7.0 | 821.5 |
| SqlInjection | 59.0 / 0.089 | 464 / 464 | 1.0 | 4 / 4 | 1.0 / 1.0 | 0.0043 | 15.5 | 34.9 | 0 | 1.4 / 5.0 | 821.6 |
| XSS | 33.22 / 0.065 | 224 / 215 | 0.9924 | 3 / 3 | 1.0 / 1.0 | 0.0047 | 15.6 | 35.1 | 0 | 1.2 / 5.0 | 821.6 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.97 / 0.982 / 0.976 (3230) | 0.972 / 0.981 / 0.976 (3233) |
| BruteForce | 1.0 / 0.64 / 0.78 (25) | 1.0 / 0.64 / 0.78 (25) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (160068) |
| DoS-HTTP | 0.988 / 0.954 / 0.971 (1871) | 0.986 / 0.958 / 0.972 (1902) |
| MITM-ARP | 0.0 / 0.0 / 0.0 (2) | 0.0 / 0.0 / 0.0 (2) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
| Recon | 0.984 / 1.0 / 0.992 (1081) | 0.984 / 1.0 / 0.992 (1081) |
| Web | 0.923 / 1.0 / 0.96 (12) | 0.923 / 1.0 / 0.96 (12) |

ARP alerts:

- gateway_ip_spoof dc:a6:32:dc:27:d5 ['192.168.137.1', '3c:18:a0:41:c3:a0']
- ip_rebound_to_new_mac dc:a6:32:dc:27:d5 ['192.168.137.1', '3c:18:a0:41:c3:a0']
- ip_rebound_to_new_mac 3c:18:a0:41:c3:a0 ['192.168.137.1', 'dc:a6:32:dc:27:d5']
