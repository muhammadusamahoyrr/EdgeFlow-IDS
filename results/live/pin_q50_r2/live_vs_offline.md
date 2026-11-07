# Live vs offline on unseen windows (pin_q50_r2)

Model `decision_tree.pkl` · CPU quota 50 · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.917** [0.728, 0.983] (145,295 / 145,323 flows)
Inference: batch p50 0.41 ms (p95 1.07 ms), median batch size 199, amortised 0.0026 ms/flow
NFStream counters (whole run): processed 853886, dropped by kernel 0, ignored 2027

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 14189.34 / 6.84 | 142,724 / 142,728 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.092 | 38.8 | 15.5 | 0 | 45.8 / 53.0 | 1038.6 |
| DoS-HTTP_Flood | 681.38 / 3.99 | 2,398 / 2,422 | 1.0001 | 1,871 / 1,893 | 0.954 / 0.962 | 0.0284 | 15.4 | 15.6 | 0 | 3.5 / 10.0 | 824.3 |
| Mirai-udpplain | 3738.62 / 16.47 | 173 / 173 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.2 | 31.4 | 0 | 4.1 / 8.0 | 821.3 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.921 / 0.964 / 0.942 (872) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.962 / 0.976 (1893) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
