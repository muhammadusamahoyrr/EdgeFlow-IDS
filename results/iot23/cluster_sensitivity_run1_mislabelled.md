# IoT-23: sensitivity of the bootstrap intervals to the cluster definition (review round 7)

Edge tree {'max_depth': 32, 'min_samples_leaf': 1, 'class_weight': 'balanced', 'random_state': 0}, Zeek labels, splits of src/train_baseline.py; 1000 resamples, seed 0, percentile intervals. Point estimates do not depend on the clustering.

Cluster definitions (all within one capture):

- **host pair**: (capture, unordered {src_ip, dst_ip}); the scheme used for the paper's intervals (results/iot23/common_class_ci.md, splits.md).
- **capture**: the capture file; only 10 clusters, so this bootstrap is coarse: a resample of 10 captures with replacement omits each capture with probability 0.9^10 = 0.35, and Attack (scenario 3-1 only), DDoS (34-1 only) and FileDownload (42-1 only) each sit in a single capture. Treat these intervals as a stress test, not as calibrated 95% intervals.
- **originator**: (capture, src_ip), src_ip = NFStream flow source = sender of the flow's first packet. In the malware captures nearly all attack flows originate from the infected device (the attacker host); inbound flows (e.g. from a C&C server) form the remote host's cluster.
- **local host**: (capture, local endpoint) with local endpoint = src_ip if private/link-local/unspecified, else dst_ip if that is, else src_ip. Folds inbound flows into the local (infected or benign IoT) device; for the benign captures it is the device or another LAN host.

Host-pair rows reproduce results/iot23/common_class_ci.md: **yes**.

## Number of clusters

| clusters   |   temporal test |   stratified test |   union |
|:-----------|----------------:|------------------:|--------:|
| host pair  |         207,778 |           202,938 | 348,350 |
| capture    |              10 |                10 |      10 |
| originator |             350 |             4,997 |   5,212 |
| local host |              42 |                37 |      45 |

## Marginal intervals (each split resamples its own clusters)

| clusters   | split      |   n clusters |   common-class macro-F1 | common 95% CI   |   all-class macro-F1 | all-class 95% CI   |   C&C F1 | C&C 95% CI     |   resamples missing a common class |
|:-----------|:-----------|-------------:|------------------------:|:----------------|---------------------:|:-------------------|---------:|:---------------|-----------------------------------:|
| host pair  | temporal   |      207,778 |                   0.973 | [0.919, 0.983]  |                0.649 | [0.613, 0.655]     |    0.945 | [0.731, 0.983] |                              0     |
| host pair  | stratified |      202,938 |                   0.956 | [0.904, 0.969]  |                0.863 | [0.638, 0.939]     |    0.885 | [0.679, 0.940] |                              0     |
| capture    | temporal   |           10 |                   0.973 | [0.469, 0.984]  |                0.649 | [0.312, 0.656]     |    0.945 | [0.819, 0.997] |                              0.35  |
| capture    | stratified |           10 |                   0.956 | [0.474, 0.976]  |                0.863 | [0.446, 0.906]     |    0.885 | [0.573, 0.978] |                              0.347 |
| originator | temporal   |          350 |                   0.973 | [0.576, 0.983]  |                0.649 | [0.384, 0.655]     |    0.945 | [0.780, 0.995] |                              0.131 |
| originator | stratified |        4,997 |                   0.956 | [0.643, 0.979]  |                0.863 | [0.489, 0.908]     |    0.885 | [0.585, 0.989] |                              0.057 |
| local host | temporal   |           42 |                   0.973 | [0.460, 0.982]  |                0.649 | [0.307, 0.655]     |    0.945 | [0.782, 0.998] |                              0.377 |
| local host | stratified |           37 |                   0.956 | [0.479, 0.978]  |                0.863 | [0.416, 0.904]     |    0.885 | [0.489, 0.991] |                              0.353 |

'resamples missing a common class' = share of resamples in which at least one of Attack, Benign, C&C, PortScan has no test flow (its F1 is then 0).

## Paired bootstrap of stratified minus temporal (union clusters, same draw for both splits)

| clusters   | metric          |   union clusters |   temporal |   stratified |   stratified - temporal | paired 95% CI    |   share diff <= 0 |
|:-----------|:----------------|-----------------:|-----------:|-------------:|------------------------:|:-----------------|------------------:|
| host pair  | common classes  |          348,350 |      0.973 |        0.956 |                  -0.017 | [-0.039, -0.009] |             0.991 |
| host pair  | all six classes |          348,350 |      0.649 |        0.863 |                   0.214 | [-0.014, 0.293]  |             0.047 |
| host pair  | C&C F1          |          348,350 |      0.945 |        0.885 |                  -0.06  | [-0.150, -0.028] |             0.99  |
| capture    | common classes  |               10 |      0.973 |        0.956 |                  -0.017 | [-0.078, 0.005]  |             0.886 |
| capture    | all six classes |               10 |      0.649 |        0.863 |                   0.214 | [-0.032, 0.272]  |             0.107 |
| capture    | C&C F1          |               10 |      0.945 |        0.885 |                  -0.06  | [-0.308, 0.014]  |             0.813 |
| originator | common classes  |            5,212 |      0.973 |        0.956 |                  -0.017 | [-0.130, 0.114]  |             0.738 |
| originator | all six classes |            5,212 |      0.649 |        0.863 |                   0.214 | [-0.037, 0.283]  |             0.105 |
| originator | C&C F1          |            5,212 |      0.945 |        0.885 |                  -0.06  | [-0.267, 0.032]  |             0.813 |
| local host | common classes  |               45 |      0.973 |        0.956 |                  -0.017 | [-0.081, 0.005]  |             0.888 |
| local host | all six classes |               45 |      0.649 |        0.863 |                   0.214 | [-0.034, 0.273]  |             0.126 |
| local host | C&C F1          |               45 |      0.945 |        0.885 |                  -0.06  | [-0.319, 0.014]  |             0.817 |

## Cluster-size distribution per class (IoT-23 test sets)

Per class: clusters containing at least one flow of the class; singleton = cluster with exactly one test flow in total; flows/cluster = flows of that class per such cluster.

|   clusters | split      | class        |   flows |   singleton clusters |   share of class flows in singletons |   flows/cluster median |     p90 |    max |   share in largest cluster |
|-----------:|:-----------|:-------------|--------:|---------------------:|-------------------------------------:|-----------------------:|--------:|-------:|---------------------------:|
|         65 | temporal   | Attack       |   1,964 |                   33 |                                0.017 |                    1   |    76   |     76 |                      0.039 |
|    135,629 | temporal   | Benign       | 143,796 |               135396 |                                0.942 |                    1   |     1   |    781 |                      0.005 |
|          7 | temporal   | C&C          |   5,152 |                    1 |                                0     |                  620   |  1583.6 |   1985 |                      0.385 |
|          3 | temporal   | DDoS         |     211 |                    1 |                                0.005 |                   95   |   111   |    115 |                      0.545 |
|          0 | temporal   | FileDownload |       0 |                  nan |                              nan     |                  nan   |   nan   |    nan |                    nan     |
|     72,105 | temporal   | PortScan     |  75,752 |                72078 |                                0.951 |                    1   |     1   |   3647 |                      0.048 |
|    207,778 | temporal   | all classes  | 226,875 |               207509 |                                0.915 |                    1   |     1   |   3647 |                      0.016 |
|        144 | stratified | Attack       |   1,798 |                   40 |                                0.022 |                   14   |    26.7 |     31 |                      0.017 |
|    129,514 | stratified | Benign       | 140,573 |               128327 |                                0.913 |                    1   |     1   |   1318 |                      0.009 |
|         10 | stratified | C&C          |   4,600 |                    2 |                                0     |                  225.5 |  1049.3 |   1664 |                      0.362 |
|          2 | stratified | DDoS         |      63 |                    0 |                                0     |                   31.5 |    33.5 |     34 |                      0.54  |
|          1 | stratified | FileDownload |       2 |                    0 |                                0     |                    2   |     2   |      2 |                      1     |
|     73,393 | stratified | PortScan     |  79,845 |                73188 |                                0.917 |                    1   |     1   |   3509 |                      0.044 |
|    202,938 | stratified | all classes  | 226,881 |               201557 |                                0.888 |                    1   |     1   |   3509 |                      0.015 |
|          1 | temporal   | Attack       |   1,964 |                    0 |                                0     |                 1964   |  1964   |   1964 |                      1     |
|         10 | temporal   | Benign       | 143,796 |                    0 |                                0     |                  830.5 | 14918.5 | 136828 |                      0.952 |
|          6 | temporal   | C&C          |   5,152 |                    0 |                                0     |                  806   |  1650.5 |   1985 |                      0.385 |
|          1 | temporal   | DDoS         |     211 |                    0 |                                0     |                  211   |   211   |    211 |                      1     |
|          0 | temporal   | FileDownload |       0 |                  nan |                              nan     |                  nan   |   nan   |    nan |                    nan     |
|          2 | temporal   | PortScan     |  75,752 |                    0 |                                0     |                37876   | 50255.2 |  53350 |                      0.704 |
|         10 | temporal   | all classes  | 226,875 |                    0 |                                0     |                 1326   | 42880.5 | 190179 |                      0.838 |
|          1 | stratified | Attack       |   1,798 |                    0 |                                0     |                 1798   |  1798   |   1798 |                      1     |
|         10 | stratified | Benign       | 140,573 |                    0 |                                0     |                  964.5 | 14578   | 132379 |                      0.942 |
|          6 | stratified | C&C          |   4,600 |                    0 |                                0     |                  725   |  1471   |   1664 |                      0.362 |
|          1 | stratified | DDoS         |      63 |                    0 |                                0     |                   63   |    63   |     63 |                      1     |
|          1 | stratified | FileDownload |       2 |                    0 |                                0     |                    2   |     2   |      2 |                      1     |
|          3 | stratified | PortScan     |  79,845 |                    0 |                                0     |                22128   | 50576.8 |  57689 |                      0.723 |
|         10 | stratified | all classes  | 226,881 |                    0 |                                0     |                 1319   | 43030.7 | 190070 |                      0.838 |
|          5 | temporal   | Attack       |   1,964 |                    1 |                                0.001 |                    1   |  1176.2 |   1959 |                      0.997 |
|        344 | temporal   | Benign       | 143,796 |                  278 |                                0.002 |                    1   |     4   | 136134 |                      0.947 |
|          8 | temporal   | C&C          |   5,152 |                    0 |                                0     |                  532   |  1298.5 |   1316 |                      0.255 |
|          1 | temporal   | DDoS         |     211 |                    0 |                                0     |                  211   |   211   |    211 |                      1     |
|          0 | temporal   | FileDownload |       0 |                  nan |                              nan     |                  nan   |   nan   |    nan |                    nan     |
|          2 | temporal   | PortScan     |  75,752 |                    0 |                                0     |                37876   | 50255.2 |  53350 |                      0.704 |
|        350 | temporal   | all classes  | 226,875 |                  279 |                                0.001 |                    1   |     4.1 | 189485 |                      0.835 |
|          7 | stratified | Attack       |   1,798 |                    1 |                                0.001 |                    1   |   717.6 |   1791 |                      0.996 |
|      4,989 | stratified | Benign       | 140,573 |                 4812 |                                0.034 |                    1   |     1   | 126988 |                      0.903 |
|         12 | stratified | C&C          |   4,600 |                    0 |                                0     |                  211   |  1202.3 |   1230 |                      0.267 |
|          1 | stratified | DDoS         |      63 |                    0 |                                0     |                   63   |    63   |     63 |                      1     |
|          1 | stratified | FileDownload |       2 |                    0 |                                0     |                    2   |     2   |      2 |                      1     |
|          3 | stratified | PortScan     |  79,845 |                    0 |                                0     |                22128   | 50576.8 |  57689 |                      0.723 |
|      4,997 | stratified | all classes  | 226,881 |                 4813 |                                0.021 |                    1   |     1   | 184679 |                      0.814 |
|          1 | temporal   | Attack       |   1,964 |                    0 |                                0     |                 1964   |  1964   |   1964 |                      1     |
|         42 | temporal   | Benign       | 143,796 |                    5 |                                0     |                    7   |   831   | 136134 |                      0.947 |
|          6 | temporal   | C&C          |   5,152 |                    0 |                                0     |                  806   |  1650.5 |   1985 |                      0.385 |
|          1 | temporal   | DDoS         |     211 |                    0 |                                0     |                  211   |   211   |    211 |                      1     |
|          0 | temporal   | FileDownload |       0 |                  nan |                              nan     |                  nan   |   nan   |    nan |                    nan     |
|          2 | temporal   | PortScan     |  75,752 |                    0 |                                0     |                37876   | 50255.2 |  53350 |                      0.704 |
|         42 | temporal   | all classes  | 226,875 |                    5 |                                0     |                    7   |  1363.3 | 189485 |                      0.835 |
|          1 | stratified | Attack       |   1,798 |                    0 |                                0     |                 1798   |  1798   |   1798 |                      1     |
|         37 | stratified | Benign       | 140,573 |                   10 |                                0     |                    4   |  1109.6 | 131673 |                      0.937 |
|          6 | stratified | C&C          |   4,600 |                    0 |                                0     |                  725   |  1471   |   1664 |                      0.362 |
|          1 | stratified | DDoS         |      63 |                    0 |                                0     |                   63   |    63   |     63 |                      1     |
|          1 | stratified | FileDownload |       2 |                    0 |                                0     |                    2   |     2   |      2 |                      1     |
|          3 | stratified | PortScan     |  79,845 |                    0 |                                0     |                22128   | 50576.8 |  57689 |                      0.723 |
|         37 | stratified | all classes  | 226,881 |                   10 |                                0     |                    4   |  1566.4 | 189364 |                      0.835 |

## CIC-IoT2023: host-pair cluster-size distribution per class (test sets)

Union of both test sets: 4,641 host-pair clusters.

| split    | class       |   flows |   clusters |   singleton clusters |   share of class flows in singletons |   flows/cluster median |     p90 |   max |   share in largest cluster |
|:---------|:------------|--------:|-----------:|---------------------:|-------------------------------------:|-----------------------:|--------:|------:|---------------------------:|
| temporal | Benign      |  52,993 |      3,424 |                1,069 |                                0.02  |                    3   |    28   |  3192 |                      0.06  |
| temporal | BruteForce  |     605 |          3 |                    0 |                                0     |                  211   |   327   |   356 |                      0.588 |
| temporal | DDoS-SYN    | 153,402 |          6 |                    0 |                                0     |                22946   | 49686.5 | 65525 |                      0.427 |
| temporal | DoS-HTTP    |  10,110 |          1 |                    0 |                                0     |                10110   | 10110   | 10110 |                      1     |
| temporal | MITM-ARP    |      25 |         13 |                    0 |                                0     |                    2   |     3   |     5 |                      0.2   |
| temporal | Mirai       |      10 |          6 |                    3 |                                0.3   |                    1.5 |     2.5 |     3 |                      0.3   |
| temporal | Recon       |  39,819 |         18 |                    0 |                                0     |                 2075   |  2678.2 |  3765 |                      0.095 |
| temporal | Web         |     192 |          8 |                    0 |                                0     |                    9   |    49.3 |   134 |                      0.698 |
| temporal | all classes | 257,156 |      3,465 |                1,072 |                                0.004 |                    3   |    31   | 65525 |                      0.255 |
| random   | Benign      |  48,323 |      3,750 |                1,511 |                                0.031 |                    2   |    24   |  2844 |                      0.059 |
| random   | BruteForce  |     324 |          3 |                    0 |                                0     |                  115   |   146.2 |   154 |                      0.475 |
| random   | DDoS-SYN    | 153,458 |          6 |                    0 |                                0     |                22073.5 | 34850.5 | 43172 |                      0.281 |
| random   | DoS-HTTP    |  11,845 |          2 |                    0 |                                0     |                 5922.5 |  7850.9 |  8333 |                      0.704 |
| random   | MITM-ARP    |      90 |         43 |                   17 |                                0.189 |                    1   |     3.8 |    15 |                      0.167 |
| random   | Mirai       |      12 |          7 |                    3 |                                0.25  |                    2   |     2.4 |     3 |                      0.25  |
| random   | Recon       |  42,943 |         57 |                    0 |                                0     |                  644   |  1150   |  2182 |                      0.051 |
| random   | Web         |     167 |         10 |                    0 |                                0     |                    9   |    37.2 |    48 |                      0.287 |
| random   | all classes | 257,162 |      3,858 |                1,531 |                                0.006 |                    2   |    29   | 43172 |                      0.168 |
