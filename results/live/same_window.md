# Same-window baseline: live macro-F1 on the three half-core windows (review round 7)

Windows: DDoS-SYN_Flood, DoS-HTTP_Flood, Mirai-udpplain (the only windows replayed in the half-core runs). Method: src/eval_live.py restricted to these windows (gateway verdicts from flows.csv; offline = NFStream on the window pcap). Macro-F1 over the classes present on either side.

## Check: recomputation over each run's own windows reproduces live_vs_offline.json

| run       |   live macro-F1 (json) |   live recomputed |   offline (json) |   offline recomputed | match   |
|:----------|-----------------------:|------------------:|-----------------:|---------------------:|:--------|
| run1      |                 0.8042 |            0.8042 |           0.8036 |               0.8036 | True    |
| run1_r2   |                 0.8038 |            0.8038 |           0.8036 |               0.8036 | True    |
| run1_r3   |                 0.8043 |            0.8043 |           0.8036 |               0.8036 | True    |
| edge100   |                 0.8102 |            0.8102 |           0.8036 |               0.8036 | True    |
| edge50    |                 0.9175 |            0.9175 |           0.9145 |               0.9145 | True    |
| edge50_r2 |                 0.9172 |            0.9172 |           0.9145 |               0.9145 | True    |
| edge50_r3 |                 0.9173 |            0.9173 |           0.9145 |               0.9145 | True    |

## Macro-F1 on the same three windows

| run       | CPU       |   windows replayed |   live macro-F1, own windows |   live macro-F1, 3 half-core windows |   offline macro-F1, 3 windows |   live flows, 3 windows | classes (3 windows)               |
|:----------|:----------|-------------------:|-----------------------------:|-------------------------------------:|------------------------------:|------------------------:|:----------------------------------|
| run1      | no limit  |                 10 |                       0.8042 |                               0.9171 |                        0.9145 |                 145,406 | Benign, DDoS-SYN, DoS-HTTP, Mirai |
| run1_r2   | no limit  |                 10 |                       0.8038 |                               0.9155 |                        0.9145 |                 162,842 | Benign, DDoS-SYN, DoS-HTTP, Mirai |
| run1_r3   | no limit  |                 10 |                       0.8043 |                               0.9175 |                        0.9145 |                 187,105 | Benign, DDoS-SYN, DoS-HTTP, Mirai |
| edge100   | one core  |                 10 |                       0.8102 |                               0.9284 |                        0.9145 |                 145,317 | Benign, DDoS-SYN, DoS-HTTP, Mirai |
| edge50    | half core |                  3 |                       0.9175 |                               0.9175 |                        0.9145 |                 145,346 | Benign, DDoS-SYN, DoS-HTTP, Mirai |
| edge50_r2 | half core |                  3 |                       0.9172 |                               0.9172 |                        0.9145 |                 163,066 | Benign, DDoS-SYN, DoS-HTTP, Mirai |
| edge50_r3 | half core |                  3 |                       0.9173 |                               0.9173 |                        0.9145 |                 145,347 | Benign, DDoS-SYN, DoS-HTTP, Mirai |

## Per-class F1 on the three windows

| run       | class    |   live F1 |   live support |   offline F1 |   offline support |
|:----------|:---------|----------:|---------------:|-------------:|------------------:|
| run1      | Benign   |     0.942 |            867 |        0.936 |               866 |
| run1      | DDoS-SYN |     1     |         142580 |        1     |            142554 |
| run1      | DoS-HTTP |     0.976 |           1955 |        0.972 |              1871 |
| run1      | Mirai    |     0.75  |              4 |        0.75  |                 4 |
| run1_r2   | Benign   |     0.938 |            868 |        0.936 |               866 |
| run1_r2   | DDoS-SYN |     1     |         160068 |        1     |            142554 |
| run1_r2   | DoS-HTTP |     0.974 |           1902 |        0.972 |              1871 |
| run1_r2   | Mirai    |     0.75  |              4 |        0.75  |                 4 |
| run1_r3   | Benign   |     0.944 |            869 |        0.936 |               866 |
| run1_r3   | DDoS-SYN |     1     |         184308 |        1     |            142554 |
| run1_r3   | DoS-HTTP |     0.976 |           1924 |        0.972 |              1871 |
| run1_r3   | Mirai    |     0.75  |              4 |        0.75  |                 4 |
| edge100   | Benign   |     0.939 |            867 |        0.936 |               866 |
| edge100   | DDoS-SYN |     1     |         142554 |        1     |            142554 |
| edge100   | DoS-HTTP |     0.975 |           1891 |        0.972 |              1871 |
| edge100   | Mirai    |     0.8   |              5 |        0.75  |                 4 |
| edge50    | Benign   |     0.944 |            871 |        0.936 |               866 |
| edge50    | DDoS-SYN |     1     |         142554 |        1     |            142554 |
| edge50    | DoS-HTTP |     0.976 |           1917 |        0.972 |              1871 |
| edge50    | Mirai    |     0.75  |              4 |        0.75  |                 4 |
| edge50_r2 | Benign   |     0.943 |            874 |        0.936 |               866 |
| edge50_r2 | DDoS-SYN |     1     |         160297 |        1     |            142554 |
| edge50_r2 | DoS-HTTP |     0.976 |           1891 |        0.972 |              1871 |
| edge50_r2 | Mirai    |     0.75  |              4 |        0.75  |                 4 |
| edge50_r3 | Benign   |     0.943 |            871 |        0.936 |               866 |
| edge50_r3 | DDoS-SYN |     1     |         142554 |        1     |            142554 |
| edge50_r3 | DoS-HTTP |     0.976 |           1918 |        0.972 |              1871 |
| edge50_r3 | Mirai    |     0.75  |              4 |        0.75  |                 4 |
