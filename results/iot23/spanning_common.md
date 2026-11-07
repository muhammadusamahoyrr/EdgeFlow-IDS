# IoT-23: boundary-spanning test flows and common-class macro-F1

Edge tree {'max_depth': 32, 'min_samples_leaf': 1, 'class_weight': 'balanced', 'random_state': 0}, trained on Zeek labels; splits of src/train_baseline.py. Spanning = test flow whose 5-tuple (either direction) also occurs in the same capture's training split (src/iot23/splits.py). Common classes: Attack, Benign, C&C, PortScan. Host-pair 95% CI: 1000 resamples of the split's own (capture, unordered host pair) clusters, seed 0, on the flows kept.

## Macro-F1 with and without spanning test flows

|                                         | temporal       | stratified     |
|:----------------------------------------|:---------------|:---------------|
| test flows                              | 226,875        | 226,881        |
| spanning                                | 9,326          | 13,174         |
| kept                                    | 217,549        | 213,707        |
| common-class macro-F1, all              | 0.9731         | 0.9558         |
| host-pair 95% CI, all                   | [0.919, 0.983] | [0.904, 0.969] |
| all-class macro-F1, all                 | 0.6487         | 0.8629         |
| common-class macro-F1, without spanning | 0.974          | 0.9181         |
| host-pair 95% CI, without spanning      | [0.874, 0.982] | [0.735, 0.955] |
| all-class macro-F1, without spanning    | 0.6493         | 0.8092         |
| common-class change                     | 0.0009         | -0.0377        |
| all-class change                        | 0.0006         | -0.0537        |

## Per class (all six classes; contribution = change of class F1 / 6)

| split      | class        | common   |   test support |   support after removal |   spanning removed |   flows predicted as class (all) |   predicted as class (kept) |   F1 all |   F1 without |   precision all |   precision without |   recall all |   recall without |   contribution to all-class change | flag                        |
|:-----------|:-------------|:---------|---------------:|------------------------:|-------------------:|---------------------------------:|----------------------------:|---------:|-------------:|----------------:|--------------------:|-------------:|-----------------:|-----------------------------------:|:----------------------------|
| temporal   | Attack       | True     |           1964 |                    1964 |                  0 |                             1959 |                        1958 |    0.996 |        0.996 |           0.997 |               0.998 |        0.995 |            0.995 |                             0      |                             |
| temporal   | Benign       | True     |         143796 |                  137148 |               6648 |                           138972 |                      132558 |    0.983 |        0.983 |           1     |               1     |        0.966 |            0.966 |                             0      |                             |
| temporal   | C&C          | True     |           5152 |                    3270 |               1882 |                             5683 |                        3569 |    0.945 |        0.949 |           0.901 |               0.909 |        0.994 |            0.992 |                             0.0006 |                             |
| temporal   | DDoS         | False    |            211 |                     211 |                  0 |                                0 |                           0 |    0     |        0     |           0     |               0     |        0     |            0     |                             0      |                             |
| temporal   | FileDownload | False    |              0 |                       0 |                  0 |                                0 |                           0 |    0     |        0     |           0     |               0     |        0     |            0     |                             0      | no test flows in this split |
| temporal   | PortScan     | True     |          75752 |                   74956 |                796 |                            80261 |                       79464 |    0.968 |        0.968 |           0.941 |               0.94  |        0.997 |            0.997 |                            -0.0001 |                             |
| stratified | Attack       | True     |           1798 |                    1788 |                 10 |                             1796 |                        1788 |    0.994 |        0.996 |           0.994 |               0.996 |        0.993 |            0.996 |                             0.0003 |                             |
| stratified | Benign       | True     |         140573 |                  131719 |               8854 |                           135604 |                      126889 |    0.981 |        0.98  |           0.999 |               0.999 |        0.963 |            0.962 |                            -0.0001 |                             |
| stratified | C&C          | True     |           4600 |                    1473 |               3127 |                             5714 |                        2498 |    0.885 |        0.733 |           0.799 |               0.583 |        0.992 |            0.988 |                            -0.0253 |                             |
| stratified | DDoS         | False    |             63 |                      63 |                  0 |                               98 |                          98 |    0.783 |        0.783 |           0.643 |               0.643 |        1     |            1     |                             0      |                             |
| stratified | FileDownload | False    |              2 |                       1 |                  1 |                                5 |                           4 |    0.571 |        0.4   |           0.4   |               0.25  |        1     |            1     |                            -0.0286 |                             |
| stratified | PortScan     | True     |          79845 |                   78663 |               1182 |                            83664 |                       82430 |    0.964 |        0.964 |           0.942 |               0.942 |        0.987 |            0.987 |                            -0      |                             |

Classes flagged LOSES ALL TEST FLOWS: none.

temporal: all-class change by class: C&C +0.0006, PortScan -0.0001, Benign +0.0000, Attack +0.0000, DDoS +0.0000, FileDownload +0.0000.
stratified: all-class change by class: FileDownload -0.0286, C&C -0.0253, Attack +0.0003, Benign -0.0001, DDoS +0.0000, PortScan -0.0000.
