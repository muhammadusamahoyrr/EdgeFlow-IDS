# IoT-23: capture-level (file) labels versus Zeek labels (edge tree)

Edge tree parameters: {'max_depth': 32, 'min_samples_leaf': 1, 'class_weight': 'balanced', 'random_state': 0}. Classes: Attack, Benign, C&C, DDoS, FileDownload, PortScan.

Flows whose file label differs from the Zeek label: 63.1% of 756,268.

| split      | trained on   |   apparent macro-F1 (file labels) |   true macro-F1 (Zeek labels) |   true Benign FPR | background flows called attack   |
|:-----------|:-------------|----------------------------------:|------------------------------:|------------------:|:---------------------------------|
| temporal   | file labels  |                             0.649 |                         0.169 |             0.985 | 141,590 / 143,796                |
| temporal   | Zeek labels  |                             0.157 |                         0.649 |             0.034 | 4,884 / 143,796                  |
| stratified | file labels  |                             0.692 |                         0.149 |             0.984 | 138,323 / 140,573                |
| stratified | Zeek labels  |                             0.167 |                         0.863 |             0.037 | 5,170 / 140,573                  |

apparent = scored against file labels, as a file-label study would report;
true = scored against the Zeek labels. Macro-F1 is over all Zeek classes in both cases.

File label per malware family (the family's main malicious behaviour in IoT-23; honeypots Benign):

| family    | file label   |
|:----------|:-------------|
| Benign    | Benign       |
| Hakai     | C&C          |
| Hide&Seek | PortScan     |
| Mirai     | DDoS         |
| Muhstik   | PortScan     |
| Torii     | C&C          |
| Trojan    | FileDownload |
