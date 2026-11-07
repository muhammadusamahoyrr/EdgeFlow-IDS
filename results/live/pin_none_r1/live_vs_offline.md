# Live vs offline on unseen windows (pin_none_r1)

Model `decision_tree.pkl` · CPU quota none · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.917** [0.730, 0.981] (145,295 / 145,331 flows)
Inference: batch p50 0.56 ms (p95 1.06 ms), median batch size 256, amortised 0.0029 ms/flow
NFStream counters (whole run): processed 839022, dropped by kernel 0, ignored 2015

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 12432.54 / 5.99 | 142,724 / 142,729 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.0857 | 18.6 | 15.3 | 0 | 115.1 / 195.0 | 994.3 |
| DoS-HTTP_Flood | 671.35 / 3.93 | 2,398 / 2,430 | 1.0001 | 1,871 / 1,901 | 0.954 / 0.963 | 0.0284 | 15.3 | 15.9 | 0 | 3.1 / 8.0 | 818.9 |
| Mirai-udpplain | 3569.3 / 15.73 | 173 / 172 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.1 | 32.6 | 0 | 3.1 / 6.0 | 816.9 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.921 / 0.966 / 0.943 (872) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.962 / 0.976 (1901) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
