# CIC-IoT2023: paired host-pair bootstrap of the random-minus-temporal macro-F1 difference

Splits and models as in src/analysis/cluster_ci.py (temporal = per capture, first 70% of flows by start time; random = stratified 70/30, seed 0). Macro-F1 over all 8 classes (Benign, BruteForce, DDoS-SYN, DoS-HTTP, MITM-ARP, Mirai, Recon, Web). 1000 resamples, seed 0.

Pairing: clusters = (capture file, unordered host pair) keyed over the union of both test sets (4,641 union clusters; temporal test 3,465, random test 3,858, shared 2,682). Each resample draws union clusters with replacement and applies the same multiplicities to both splits; a cluster missing from one test set contributes nothing to it. Both macro-F1 values are recomputed and differenced per resample (percentile interval).

| model         |   temporal macro-F1 |   random macro-F1 |   difference (random - temporal) | paired 95% CI of difference   |   share of resamples with diff <= 0 | temporal CI (union resampling)   | random CI (union resampling)   |   corr(temporal, random) over resamples |
|:--------------|--------------------:|------------------:|---------------------------------:|:------------------------------|------------------------------------:|:---------------------------------|:-------------------------------|----------------------------------------:|
| edge tree     |               0.725 |             0.867 |                            0.142 | [0.025, 0.287]                |                               0.001 | [0.564, 0.830]                   | [0.732, 0.874]                 |                                   0.406 |
| decision tree |               0.731 |             0.869 |                            0.137 | [0.024, 0.278]                |                               0.001 | [0.573, 0.829]                   | [0.735, 0.876]                 |                                   0.416 |

The marginal intervals under union resampling are close to, but not identical with, those in results/cluster_ci.md (which resample each split's own clusters); the per-split numbers of drawn clusters vary here because a drawn union cluster may be absent from one split.
