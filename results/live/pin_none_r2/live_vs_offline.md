# Live vs offline on unseen windows (pin_none_r2)

Model `decision_tree.pkl` · CPU quota none · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.917** [0.730, 0.982] (145,295 / 145,320 flows)
Inference: batch p50 0.58 ms (p95 1.06 ms), median batch size 256, amortised 0.0030 ms/flow
NFStream counters (whole run): processed 833366, dropped by kernel 0, ignored 2013

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 13743.43 / 6.63 | 142,724 / 142,729 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.0914 | 17.5 | 15.2 | 0 | 104.4 / 192.0 | 1033.9 |
| DoS-HTTP_Flood | 682.34 / 3.99 | 2,398 / 2,420 | 1.0001 | 1,871 / 1,891 | 0.954 / 0.962 | 0.0284 | 15.3 | 16.0 | 0 | 4.0 / 19.0 | 821.5 |
| Mirai-udpplain | 3807.54 / 16.78 | 173 / 171 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.1 | 32.0 | 0 | 3.9 / 9.0 | 803.8 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.921 / 0.964 / 0.942 (871) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.962 / 0.976 (1891) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
