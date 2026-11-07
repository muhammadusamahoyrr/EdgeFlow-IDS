# IoT-23: Benign FPR per capture (file-label vs Zeek-label edge tree)

Edge tree {'max_depth': 32, 'min_samples_leaf': 1, 'class_weight': 'balanced', 'random_state': 0}; both models scored against Zeek labels. FPR = Benign (Zeek) test flows predicted as any attack class. Macro average: unweighted mean over captures that have Benign test flows; pooled: over all Benign test flows (as in results/iot23/file_label_baseline.md).

## Summary

| split      | model            |   pooled Benign FPR (flow-weighted) |   macro-avg FPR over captures |   captures |   macro-avg, honeypot captures |   macro-avg, malware captures | min-max over captures   |
|:-----------|:-----------------|------------------------------------:|------------------------------:|-----------:|-------------------------------:|------------------------------:|:------------------------|
| temporal   | file-label model |                              0.9847 |                        0.7092 |         10 |                         0.046  |                        0.9934 | 0.007-1.000             |
| temporal   | Zeek-label model |                              0.034  |                        0.0492 |         10 |                         0.0015 |                        0.0697 | 0.000-0.252             |
| stratified | file-label model |                              0.984  |                        0.707  |         10 |                         0.04   |                        0.9928 | 0.002-1.000             |
| stratified | Zeek-label model |                              0.0368 |                        0.0558 |         10 |                         0.0073 |                        0.0766 | 0.000-0.313             |

## temporal split (143,796 Benign test flows)

| capture                           | file label   |   Benign test flows |   share of split's Benign test flows |   FP (file-label model) |   FPR (file-label model) |   FP (Zeek-label model) |   FPR (Zeek-label model) |
|:----------------------------------|:-------------|--------------------:|-------------------------------------:|------------------------:|-------------------------:|------------------------:|-------------------------:|
| CTU-Honeypot-Capture-4-1          | Benign       |                1373 |                               0.0095 |                       9 |                   0.0066 |                       1 |                   0.0007 |
| CTU-Honeypot-Capture-5-1          | Benign       |                 802 |                               0.0056 |                      97 |                   0.1209 |                       3 |                   0.0037 |
| CTU-Honeypot-Capture-7-1-Somfy-01 | Benign       |                  96 |                               0.0007 |                       1 |                   0.0104 |                       0 |                   0      |
| CTU-IoT-Malware-Capture-1-1       | PortScan     |              136828 |                               0.9515 |                  136827 |                   1      |                    4410 |                   0.0322 |
| CTU-IoT-Malware-Capture-20-1      | C&C          |                 938 |                               0.0065 |                     930 |                   0.9915 |                       0 |                   0      |
| CTU-IoT-Malware-Capture-21-1      | C&C          |                 829 |                               0.0058 |                     824 |                   0.994  |                       0 |                   0      |
| CTU-IoT-Malware-Capture-3-1       | PortScan     |                 832 |                               0.0058 |                     809 |                   0.9724 |                     210 |                   0.2524 |
| CTU-IoT-Malware-Capture-34-1      | DDoS         |                 172 |                               0.0012 |                     172 |                   1      |                       0 |                   0      |
| CTU-IoT-Malware-Capture-42-1      | FileDownload |                1279 |                               0.0089 |                    1274 |                   0.9961 |                     260 |                   0.2033 |
| CTU-IoT-Malware-Capture-8-1       | C&C          |                 647 |                               0.0045 |                     647 |                   1      |                       0 |                   0      |

## stratified split (140,573 Benign test flows)

| capture                           | file label   |   Benign test flows |   share of split's Benign test flows |   FP (file-label model) |   FPR (file-label model) |   FP (Zeek-label model) |   FPR (Zeek-label model) |
|:----------------------------------|:-------------|--------------------:|-------------------------------------:|------------------------:|-------------------------:|------------------------:|-------------------------:|
| CTU-Honeypot-Capture-4-1          | Benign       |                1338 |                               0.0095 |                       2 |                   0.0015 |                       0 |                   0      |
| CTU-Honeypot-Capture-5-1          | Benign       |                 826 |                               0.0059 |                      56 |                   0.0678 |                      18 |                   0.0218 |
| CTU-Honeypot-Capture-7-1-Somfy-01 | Benign       |                  79 |                               0.0006 |                       4 |                   0.0506 |                       0 |                   0      |
| CTU-IoT-Malware-Capture-1-1       | PortScan     |              132379 |                               0.9417 |                  132369 |                   0.9999 |                    4461 |                   0.0337 |
| CTU-IoT-Malware-Capture-20-1      | C&C          |                 942 |                               0.0067 |                     929 |                   0.9862 |                       0 |                   0      |
| CTU-IoT-Malware-Capture-21-1      | C&C          |                 987 |                               0.007  |                     986 |                   0.999  |                       0 |                   0      |
| CTU-IoT-Malware-Capture-3-1       | PortScan     |                1489 |                               0.0106 |                    1453 |                   0.9758 |                     466 |                   0.313  |
| CTU-IoT-Malware-Capture-34-1      | DDoS         |                 556 |                               0.004  |                     552 |                   0.9928 |                      16 |                   0.0288 |
| CTU-IoT-Malware-Capture-42-1      | FileDownload |                1298 |                               0.0092 |                    1293 |                   0.9961 |                     209 |                   0.161  |
| CTU-IoT-Malware-Capture-8-1       | C&C          |                 679 |                               0.0048 |                     679 |                   1      |                       0 |                   0      |

File label = the class labelling-by-capture gives every flow of the capture (honeypots Benign; src/iot23/extract_label.FAMILY_CLASS). The file-label model learns Benign only from the honeypot captures; the Benign background of every malware capture is labelled with that capture's attack class in training.
