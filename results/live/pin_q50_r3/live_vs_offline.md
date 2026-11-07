# Live vs offline on unseen windows (pin_q50_r3)

Model `decision_tree.pkl` · CPU quota 50 · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.917** [0.731, 0.982] (145,295 / 157,955 flows)
Inference: batch p50 0.69 ms (p95 1.59 ms), median batch size 104, amortised 0.0073 ms/flow
NFStream counters (whole run): processed 907671, dropped by kernel 0, ignored 2047

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 11847.47 / 5.71 | 142,724 / 155,350 | 1.0 | 142,554 / 155,175 | 1.0 / 1.0 | 0.0857 | 89.1 | 26.0 | 0 | 49.7 / 55.0 | 963.9 |
| DoS-HTTP_Flood | 666.65 / 3.9 | 2,398 / 2,433 | 1.0 | 1,871 / 1,905 | 0.954 / 0.963 | 0.0284 | 15.4 | 16.1 | 0 | 5.1 / 12.0 | 809.8 |
| Mirai-udpplain | 3292.83 / 14.51 | 173 / 172 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.2 | 33.2 | 0 | 5.9 / 10.0 | 808.8 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.922 / 0.966 / 0.943 (871) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (155175) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.962 / 0.976 (1905) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
