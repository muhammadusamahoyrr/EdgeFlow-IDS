# Live vs offline on unseen windows (bugcheck_unpatched)

Model `decision_tree.pkl` · CPU quota none · replay speed x1.0
Macro-F1 offline **0.999** [0.997, 1.000] vs live **0.999** [0.997, 1.000] (688 / 589 flows)
Inference: batch p50 0.56 ms (p95 0.93 ms), median batch size 2, amortised 0.3825 ms/flow
NFStream counters (whole run): processed 85181, dropped by kernel 0, ignored 402

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SqlInjection | 59.08 / 0.089 | 464 / 471 | 1.0033 | 4 / 4 | 1.0 / 1.0 | 0.0064 | 82.5 | 117.2 | 0 | 0.8 / 3.0 | 401.3 |
| XSS | 33.18 / 0.065 | 224 / 118 | 0.645 | 3 / 2 | 1.0 / 1.0 | 0.0 | 49.2 | 73.7 | 2 | 1.2 / 18.0 | 402.2 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 1.0 / 0.994 / 0.997 (681) | 1.0 / 0.995 / 0.997 (583) |
| Web | 1.0 / 1.0 / 1.0 (7) | 1.0 / 1.0 / 1.0 (6) |

ARP alerts:

- mac_claims_multiple_ips e8:1b:69:f8:d4:e3 ['192.168.137.171', '192.168.137.236']
- mac_claims_multiple_ips 9c:8e:cd:1d:ab:9f ['192.168.137.116', '192.168.137.242']
