# Live vs offline on unseen windows (edge50_r2)

Model `decision_tree.pkl` · CPU quota 50 · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.917** [0.730, 0.983] (145,295 / 163,066 flows)
Inference: batch p50 0.62 ms (p95 1.22 ms), median batch size 114, amortised 0.0060 ms/flow
NFStream counters (whole run): processed 899107, dropped by kernel 0, ignored 2041

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 11830.85 / 5.7 | 142,724 / 160,475 | 1.0 | 142,554 / 160,297 | 1.0 / 1.0 | 0.0899 | 97.0 | 21.9 | 0 | 50.4 / 55.0 | 991.6 |
| DoS-HTTP_Flood | 678.96 / 3.97 | 2,398 / 2,420 | 1.0001 | 1,871 / 1,891 | 0.954 / 0.962 | 0.0265 | 15.4 | 15.5 | 0 | 2.7 / 6.0 | 812.4 |
| Mirai-udpplain | 3685.05 / 16.24 | 173 / 171 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.0 | 15.2 | 31.6 | 0 | 3.8 / 9.0 | 812.4 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.921 / 0.966 / 0.943 (874) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (160297) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.99 / 0.962 / 0.976 (1891) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
