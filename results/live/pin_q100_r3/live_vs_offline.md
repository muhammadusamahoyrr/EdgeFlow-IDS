# Live vs offline on unseen windows (pin_q100_r3)

Model `decision_tree.pkl` · CPU quota 100 · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.978] vs live **0.930** [0.840, 0.982] (145,295 / 145,342 flows)
Inference: batch p50 0.93 ms (p95 33.58 ms), median batch size 124, amortised 0.0089 ms/flow
NFStream counters (whole run): processed 877615, dropped by kernel 0, ignored 2033

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 12358.89 / 5.96 | 142,724 / 142,729 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.0857 | 37.5 | 15.5 | 0 | 83.5 / 106.0 | 985.5 |
| DoS-HTTP_Flood | 619.05 / 3.62 | 2,398 / 2,435 | 1.0 | 1,871 / 1,908 | 0.954 / 0.963 | 0.0285 | 15.4 | 16.0 | 0 | 5.0 / 18.0 | 806.5 |
| Mirai-udpplain | 2176.26 / 9.59 | 173 / 178 | 0.9999 | 4 / 5 | 0.75 / 0.8 | 0.0058 | 15.2 | 25.0 | 0 | 4.5 / 11.0 | 803.5 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.922 / 0.965 / 0.943 (875) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.989 / 0.962 / 0.976 (1908) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.8 / 0.8 / 0.8 (5) |
