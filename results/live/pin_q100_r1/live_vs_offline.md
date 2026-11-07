# Live vs offline on unseen windows (pin_q100_r1)

Model `decision_tree.pkl` · CPU quota 100 · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.917** [0.731, 0.981] (145,295 / 145,320 flows)
Inference: batch p50 0.47 ms (p95 0.85 ms), median batch size 233, amortised 0.0028 ms/flow
NFStream counters (whole run): processed 840534, dropped by kernel 0, ignored 2027

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 13964.95 / 6.73 | 142,724 / 142,727 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.0925 | 22.8 | 15.3 | 0 | 70.8 / 103.0 | 1032.8 |
| DoS-HTTP_Flood | 690.13 / 4.04 | 2,398 / 2,420 | 1.0001 | 1,871 / 1,891 | 0.954 / 0.962 | 0.0265 | 15.3 | 15.5 | 0 | 2.8 / 6.0 | 820.8 |
| Mirai-udpplain | 3887.92 / 17.13 | 173 / 173 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.2 | 30.9 | 0 | 3.0 / 5.0 | 817.8 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.921 / 0.966 / 0.943 (871) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.962 / 0.976 (1891) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
