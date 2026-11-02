# File-name labels versus evidence-based labels (edge tree)

Flows whose file label differs from the evidence label: 13.4% of 857,206.

| split      | trained on      |   apparent macro-F1 (file labels) |   true macro-F1 (evidence labels) |   true Benign FPR | background flows called attack   |
|:-----------|:----------------|----------------------------------:|----------------------------------:|------------------:|:---------------------------------|
| temporal   | file labels     |                             0.537 |                             0.396 |             0.718 | 38,034 / 52,993                  |
| temporal   | evidence labels |                             0.409 |                             0.725 |             0.038 | 2,030 / 52,993                   |
| stratified | file labels     |                             0.617 |                             0.426 |             0.702 | 33,939 / 48,323                  |
| stratified | evidence labels |                             0.439 |                             0.867 |             0.011 | 555 / 48,323                     |

apparent = scored against file labels, as a file-label study would report;
true = scored against the evidence labels.
