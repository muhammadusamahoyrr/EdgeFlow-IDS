# Live vs offline on unseen windows (bugcheck_patched)

Model `decision_tree.pkl` · CPU quota none · replay speed x1.0
Macro-F1 offline **0.999** [0.997, 1.000] vs live **0.999** [0.997, 1.000] (688 / 686 flows)
Inference: batch p50 0.53 ms (p95 0.81 ms), median batch size 6, amortised 0.0930 ms/flow
NFStream counters (whole run): processed 84828, dropped by kernel 0, ignored 404

| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SqlInjection | 59.26 / 0.09 | 464 / 469 | 1.0029 | 4 / 4 | 1.0 / 1.0 | 0.0043 | 15.6 | 35.1 | 0 | 0.9 / 3.0 | 401.4 |
| XSS | 33.2 / 0.065 | 224 / 217 | 0.9941 | 3 / 3 | 1.0 / 1.0 | 0.0047 | 15.5 | 34.8 | 2 | 1.1 / 4.0 | 401.4 |

| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |
|---|---|---|
| Benign | 1.0 / 0.994 / 0.997 (681) | 1.0 / 0.996 / 0.998 (679) |
| Web | 1.0 / 1.0 / 1.0 (7) | 1.0 / 1.0 / 1.0 (7) |

ARP alerts:

- mac_claims_multiple_ips e8:1b:69:f8:d4:e3 ['192.168.137.171', '192.168.137.236']
- mac_claims_multiple_ips 9c:8e:cd:1d:ab:9f ['192.168.137.116', '192.168.137.242']
