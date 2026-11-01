# Live vs offline on unseen windows (edge50)

Model `decision_tree.pkl` · CPU quota 50 · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.918** [0.731, 0.982] (145,295 / 145,346 flows)
Inference: batch p50 0.72 ms (p95 23.84 ms), median batch size 105, amortised 0.0074 ms/flow
NFStream counters (whole run): processed 894563, dropped by kernel 0, ignored 2035

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 12087.66 / 5.83 | 142,724 / 142,730 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.0852 | 75.9 | 20.2 | 0 | 50.2 / 55.0 | 981.2 |
| DoS-HTTP_Flood | 657.69 / 3.85 | 2,398 / 2,445 | 1.0 | 1,871 / 1,917 | 0.954 / 0.964 | 0.0284 | 15.4 | 16.1 | 0 | 4.2 / 9.0 | 800.6 |
| Mirai-udpplain | 3206.32 / 14.13 | 173 / 171 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.1 | 34.1 | 0 | 5.4 / 9.0 | 798.6 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.923 / 0.966 / 0.944 (871) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.963 / 0.976 (1917) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
