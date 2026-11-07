# IoT-23: temporal versus stratified split (edge tree, Zeek labels)

Edge tree parameters: {'max_depth': 32, 'min_samples_leaf': 1, 'class_weight': 'balanced', 'random_state': 0}. Host-pair clusters = (capture, unordered host pair).

| split      |   train flows |   test flows |   macro-F1 | flow bootstrap 95% CI   | host-pair bootstrap 95% CI   |   host-pair clusters |   Benign FPR |   macro-F1, common classes |
|:-----------|--------------:|-------------:|-----------:|:------------------------|:-----------------------------|---------------------:|-------------:|---------------------------:|
| temporal   |       529,393 |      226,875 |      0.649 | [0.648, 0.650]          | [0.613, 0.655]               |              207,778 |       0.034  |                      0.973 |
| stratified |       529,387 |      226,881 |      0.863 | [0.764, 0.923]          | [0.638, 0.939]               |              202,938 |       0.0368 |                      0.956 |

Common classes (train and test flows in both splits): Attack, Benign, C&C, PortScan. Classes missing from a split's train or test set score F1 = 0 and pull macro-F1 down mechanically.

Per-class F1 (flow bootstrap 200 resamples; host-pair bootstrap 1000 resamples):

| split      | class        |   test support |   host pairs |   train support |    F1 | flow 95% CI    | host-pair 95% CI   |
|:-----------|:-------------|---------------:|-------------:|----------------:|------:|:---------------|:-------------------|
| temporal   | Attack       |           1964 |           65 |            4030 | 0.996 | [0.995, 0.998] | [0.993, 0.998]     |
| temporal   | Benign       |         143796 |       135629 |          324779 | 0.983 | [0.982, 0.983] | [0.980, 0.984]     |
| temporal   | C&C          |           5152 |            7 |           10182 | 0.945 | [0.941, 0.949] | [0.731, 0.983]     |
| temporal   | DDoS         |            211 |            3 |               0 | 0     | [0.000, 0.000] | [0.000, 0.000]     |
| temporal   | FileDownload |              0 |            0 |               6 | 0     | [0.000, 0.000] | [0.000, 0.000]     |
| temporal   | PortScan     |          75752 |        72105 |          190396 | 0.968 | [0.967, 0.969] | [0.965, 0.972]     |
| stratified | Attack       |           1798 |          144 |            4196 | 0.994 | [0.991, 0.996] | [0.991, 0.996]     |
| stratified | Benign       |         140573 |       129514 |          328002 | 0.981 | [0.980, 0.981] | [0.979, 0.982]     |
| stratified | C&C          |           4600 |           10 |           10734 | 0.885 | [0.878, 0.891] | [0.679, 0.940]     |
| stratified | DDoS         |             63 |            2 |             148 | 0.783 | [0.710, 0.838] | [0.000, 1.000]     |
| stratified | FileDownload |              2 |            1 |               4 | 0.571 | [0.000, 0.943] | [0.000, 1.000]     |
| stratified | PortScan     |          79845 |        73393 |          186303 | 0.964 | [0.963, 0.965] | [0.961, 0.967]     |

Boundary-spanning test flows (5-tuple, either direction, also in the same capture's training split):

|                           | temporal                            | stratified                                        |
|:--------------------------|:------------------------------------|:--------------------------------------------------|
| spanning test flows       | 9,326 / 226,875                     | 13,174 / 226,881                                  |
| share                     | 0.041                               | 0.058                                             |
| macro-F1 all              | 0.649                               | 0.863                                             |
| macro-F1 without spanning | 0.649                               | 0.809                                             |
| same, over classes left   | 0.779                               | 0.809                                             |
| classes left              | Attack, Benign, C&C, DDoS, PortScan | Attack, Benign, C&C, DDoS, FileDownload, PortScan |
| share Attack              | 0.0                                 | 0.006                                             |
| share Benign              | 0.046                               | 0.063                                             |
| share C&C                 | 0.365                               | 0.68                                              |
| share DDoS                | 0.0                                 | 0.0                                               |
| share FileDownload        | nan                                 | 0.5                                               |
| share PortScan            | 0.011                               | 0.015                                             |
