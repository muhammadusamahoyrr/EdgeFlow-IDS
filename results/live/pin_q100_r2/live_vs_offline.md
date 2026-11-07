# Live vs offline on unseen windows (pin_q100_r2)

Model `decision_tree.pkl` · CPU quota 100 · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.917** [0.730, 0.980] (145,295 / 145,326 flows)
Inference: batch p50 0.48 ms (p95 0.89 ms), median batch size 230, amortised 0.0028 ms/flow
NFStream counters (whole run): processed 841242, dropped by kernel 0, ignored 2023

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 14052.02 / 6.78 | 142,724 / 142,727 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.0983 | 22.3 | 15.2 | 0 | 66.3 / 104.0 | 1036.3 |
| DoS-HTTP_Flood | 678.19 / 3.97 | 2,398 / 2,426 | 1.0001 | 1,871 / 1,897 | 0.954 / 0.962 | 0.0265 | 15.4 | 15.5 | 0 | 3.6 / 14.0 | 819.9 |
| Mirai-udpplain | 3512.33 / 15.48 | 173 / 173 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0059 | 15.2 | 33.6 | 0 | 4.5 / 8.0 | 816.9 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.92 / 0.963 / 0.941 (871) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.962 / 0.975 (1897) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
