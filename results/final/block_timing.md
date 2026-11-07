# Late blocks: window length vs export delay (round 17)

Script: src/analysis/block_timing.py, run run1, ten 60 s windows, counts reset per window. Validation (whole capture periods, flow-end stamps): 0.995 (results/final/blocking_rates.md).

|   k | MITM-ARP verdicts   | verdict time          |   attack flows after block (pooled) |   DDoS-SYN window |   DoS-HTTP window |   attack flows |
|----:|:--------------------|:----------------------|------------------------------------:|------------------:|------------------:|---------------:|
|   1 | counted             | (a) flow end          |                              0.9719 |             0.972 |             0.991 |         212965 |
|   1 | counted             | (b) flow end + 15 s   |                              0.1128 |             0.106 |             0.637 |         212965 |
|   1 | counted             | (c) live verdict time |                              0.1111 |             0.105 |             0.636 |         212965 |
|   3 | counted             | (a) flow end          |                              0.9715 |             0.972 |             0.977 |         212965 |
|   3 | counted             | (b) flow end + 15 s   |                              0.1128 |             0.106 |             0.637 |         212965 |
|   3 | counted             | (c) live verdict time |                              0.1111 |             0.105 |             0.636 |         212965 |
|  10 | counted             | (a) flow end          |                              0.971  |             0.971 |             0.953 |         212965 |
|  10 | counted             | (b) flow end + 15 s   |                              0.1127 |             0.106 |             0.636 |         212965 |
|  10 | counted             | (c) live verdict time |                              0.1111 |             0.105 |             0.636 |         212965 |
|   1 | ignored             | (a) flow end          |                              0.9715 |             0.972 |             0.958 |         212965 |
|   1 | ignored             | (b) flow end + 15 s   |                              0.1128 |             0.106 |             0.636 |         212965 |
|   1 | ignored             | (c) live verdict time |                              0.1111 |             0.105 |             0.636 |         212965 |
|   3 | ignored             | (a) flow end          |                              0.9711 |             0.972 |             0.949 |         212965 |
|   3 | ignored             | (b) flow end + 15 s   |                              0.1127 |             0.106 |             0.636 |         212965 |
|   3 | ignored             | (c) live verdict time |                              0.1111 |             0.105 |             0.636 |         212965 |
|  10 | ignored             | (a) flow end          |                              0.9706 |             0.971 |             0.93  |         212965 |
|  10 | ignored             | (b) flow end + 15 s   |                              0.1127 |             0.106 |             0.636 |         212965 |
|  10 | ignored             | (c) live verdict time |                              0.111  |             0.105 |             0.631 |         212965 |
