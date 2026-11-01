# Live vs offline on unseen windows (edge50)

Model `decision_tree.pkl` · CPU quota 50 · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.918** [0.730, 0.982] (145,295 / 127,996 flows)
Inference: batch p50 0.74 ms (p95 24.16 ms), median batch size 108, amortised 0.0074 ms/flow
NFStream counters (whole run): processed 799195, dropped by kernel 0, ignored 1978

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 12236.1 / 5.9 | 142,724 / 125,380 | 0.9187 | 142,554 / 125,214 | 1.0 / 1.0 | 0.0723 | 70.1 | 23.3 | 0 | 49.9 / 55.0 | 986.1 |
| DoS-HTTP_Flood | 658.99 / 3.86 | 2,398 / 2,444 | 1.0001 | 1,871 / 1,914 | 0.954 / 0.964 | 0.0283 | 83.8 | 122.5 | 2 | 50.9 / 55.0 | 986.6 |
| Mirai-udpplain | 3262.14 / 14.37 | 173 / 172 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.2 | 33.6 | 4 | 20.0 / 56.0 | 927.3 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.923 / 0.969 / 0.945 (864) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 0.998 / 0.999 (125214) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.991 / 0.963 / 0.977 (1914) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |

ARP alerts:

- ip_rebound_to_new_mac ee:06:3b:b8:d1:df ['192.168.137.153', 'dc:a6:32:c9:e4:d5']
- mac_claims_multiple_ips 9c:8e:cd:1d:ab:9f ['192.168.137.235', '192.168.137.61']
- mac_claims_multiple_ips dc:a6:32:c9:e4:d5 ['192.168.137.128', '192.168.137.153']
- mac_claims_multiple_ips dc:a6:32:c9:e4:90 ['192.168.137.238', '192.168.137.99']
- mac_claims_multiple_ips e4:5f:01:55:90:c4 ['192.168.137.247', '192.168.137.36']
- mac_claims_multiple_ips dc:a6:32:dc:27:d5 ['192.168.137.147', '192.168.137.66']
