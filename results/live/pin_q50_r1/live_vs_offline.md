# Live vs offline on unseen windows (pin_q50_r1)

Model `decision_tree.pkl` · CPU quota 50 · replay speed x1.0
Macro-F1 offline **0.914** [0.726, 0.978] vs live **0.917** [0.731, 0.981] (145,295 / 145,327 flows)
Inference: batch p50 0.47 ms (p95 1.18 ms), median batch size 162, amortised 0.0035 ms/flow
NFStream counters (whole run): processed 866514, dropped by kernel 0, ignored 2021

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 13595.05 / 6.55 | 142,724 / 142,729 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.0857 | 46.2 | 15.6 | 0 | 48.1 / 55.0 | 1026.8 |
| DoS-HTTP_Flood | 668.43 / 3.91 | 2,398 / 2,425 | 1.0 | 1,871 / 1,898 | 0.954 / 0.962 | 0.0285 | 15.4 | 16.0 | 0 | 4.6 / 10.0 | 818.7 |
| Mirai-udpplain | 3851.07 / 16.97 | 173 / 173 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.1 | 31.3 | 0 | 3.9 / 8.0 | 816.7 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.92 / 0.966 / 0.942 (871) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.962 / 0.975 (1898) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
