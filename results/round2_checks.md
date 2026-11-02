# Second-round review checks

## Per-class recall with host-pair bootstrap (edge tree)

| split      | class      |   recall | host-pair 95% CI   |   host pairs |   test flows |
|:-----------|:-----------|---------:|:-------------------|-------------:|-------------:|
| temporal   | Benign     |    0.962 | [0.901, 0.990]     |         3424 |        52993 |
| temporal   | BruteForce |    0.053 | [0.000, 0.842]     |            3 |          605 |
| temporal   | DDoS-SYN   |    1     | [1.000, 1.000]     |            6 |       153402 |
| temporal   | DoS-HTTP   |    0.985 | [0.985, 0.985]     |            1 |        10110 |
| temporal   | MITM-ARP   |    0.16  | [0.000, 0.375]     |           13 |           25 |
| temporal   | Mirai      |    0.9   | [0.571, 1.000]     |            6 |           10 |
| temporal   | Recon      |    1     | [1.000, 1.000]     |           18 |        39819 |
| temporal   | Web        |    0.917 | [0.804, 0.941]     |            8 |          192 |
| stratified | Benign     |    0.989 | [0.984, 0.992]     |         3750 |        48323 |
| stratified | BruteForce |    1     | [1.000, 1.000]     |            3 |          324 |
| stratified | DDoS-SYN   |    1     | [1.000, 1.000]     |            6 |       153458 |
| stratified | DoS-HTTP   |    0.991 | [0.991, 0.991]     |            2 |        11845 |
| stratified | MITM-ARP   |    0.267 | [0.176, 0.390]     |           43 |           90 |
| stratified | Mirai      |    1     | [1.000, 1.000]     |            7 |           12 |
| stratified | Recon      |    1     | [1.000, 1.000]     |           57 |        42943 |
| stratified | Web        |    0.886 | [0.824, 0.919]     |           10 |          167 |

## False blocks under two definitions (enforced live runs)

| run            |   pairs blocked |   false (trigger flow benign) |   false (pair has no attack flow in window) |
|:---------------|----------------:|------------------------------:|--------------------------------------------:|
| enforce_k1     |              79 |                            60 |                                          60 |
| enforce_policy |               9 |                             0 |                                           0 |
