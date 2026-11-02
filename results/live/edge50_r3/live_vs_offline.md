# Live vs offline on unseen windows (edge50_r3)

Model `decision_tree.pkl` · CPU quota 50 · replay speed x1.0
Macro-F1 offline **0.914** [0.727, 0.979] vs live **0.917** [0.732, 0.981] (145,295 / 145,347 flows)
Inference: batch p50 0.63 ms (p95 1.33 ms), median batch size 118, amortised 0.0058 ms/flow
NFStream counters (whole run): processed 881940, dropped by kernel 0, ignored 2039

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DDoS-SYN_Flood | 12400.83 / 5.98 | 142,724 / 142,729 | 1.0 | 142,554 / 142,554 | 1.0 / 1.0 | 0.0857 | 60.3 | 17.4 | 0 | 49.0 / 54.0 | 999.2 |
| DoS-HTTP_Flood | 655.93 / 3.84 | 2,398 / 2,446 | 1.0 | 1,871 / 1,918 | 0.954 / 0.964 | 0.0284 | 15.4 | 15.9 | 0 | 4.9 / 13.0 | 813.8 |
| Mirai-udpplain | 3167.13 / 13.95 | 173 / 172 | 0.9999 | 4 / 4 | 0.75 / 0.75 | 0.006 | 15.1 | 33.8 | 0 | 5.4 / 10.0 | 811.9 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 0.906 / 0.968 / 0.936 (866) | 0.923 / 0.964 / 0.943 (871) |
| DDoS-SYN | 1.0 / 1.0 / 1.0 (142554) | 1.0 / 1.0 / 1.0 (142554) |
| DoS-HTTP | 0.992 / 0.954 / 0.972 (1871) | 0.989 / 0.963 / 0.976 (1918) |
| Mirai | 0.75 / 0.75 / 0.75 (4) | 0.75 / 0.75 / 0.75 (4) |
