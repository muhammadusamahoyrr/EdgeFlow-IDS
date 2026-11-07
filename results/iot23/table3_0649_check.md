# IoT-23 Table III: the two temporal macro-F1 values that round to 0.649

Script: src/diag/iot23_0649_check.py (edge tree, temporal split, macro-F1 over the six Zeek classes). Run 3 Nov 2026.

| tree trained on | scored vs file labels | scored vs Zeek labels |
|:----------------|----------------------:|----------------------:|
| file labels     |              0.648619 |              0.169076 |
| Zeek labels     |              0.157241 |              0.648727 |

The two diagonal values (0.6486, 0.6487) come from different models and label sets; the match at three decimals is a coincidence, not a copy error.
