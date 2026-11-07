# Live vs offline on unseen windows (pin_none_r3)

Model `decision_tree.pkl` · CPU quota none · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.978] vs live **0.917** [0.730, 0.982] (145,295 / 145,373 flows)
Inference: batch p50 0.75 ms (p95 1.25 ms), median batch size 243, amortised 0.0038 ms/flow
NFStream counters (whole run): processed 838388, dropped by kernel 0, ignored 2029

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 12788.71 / 6.17 | 142,724 / 142,730 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.0966 | 18.6 | 15.2 | 0 | 118.1 / 207.0 | 1027.1 |
| DoS-HTTP_Flood | 633.52 / 3.71 | 2,398 / 2,472 | 1.0001 | 1,871 / 1,940 | 0.954 / 0.964 | 0.0282 | 15.4 | 15.6 | 0 | 5.9 / 25.0 | 812.7 |
| Mirai-udpplain | 3535.28 / 15.58 | 173 / 171 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.1 | 32.6 | 0 | 4.6 / 9.0 | 811.8 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.922 / 0.963 / 0.942 (875) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.963 / 0.976 (1940) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
