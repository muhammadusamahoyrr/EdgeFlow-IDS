# CIC-IoT2023: cluster-unit sensitivity of the random-minus-temporal difference (review round 8)

Models: unconstrained decision tree and deployed edge tree {'max_depth': 32, 'min_samples_leaf': 1, 'class_weight': 'balanced', 'random_state': 0}; splits of src/train_baseline.py (temporal per capture; random = stratified 70/30, seed 0); macro-F1 over all 8 classes (Benign, BruteForce, DDoS-SYN, DoS-HTTP, MITM-ARP, Mirai, Recon, Web). 1000 resamples, seed 0, percentile intervals. Point estimates do not depend on the clustering. Script: src/analysis/cluster_sensitivity_cic.py.

Cluster units:

- **host pair**: (capture, unordered host pair), the paper's scheme (results/cluster_ci.md, results/paired_diff.md).
- **attacker host**: a flow involving one of its capture's confirmed attackers (data/attackers.json; IP rule: src or dst IP is a listed attacker; MAC rule for ARP spoofing: src/dst MAC is the attacker MAC) belongs to the cluster (capture, attacker IP); every other flow keeps its host-pair cluster. The label is not used to build the key.
- **attacker device**: as attacker host, but one cluster per attacker IP across captures (assumes the same IP is the same device in different captures; not documented by the dataset; supplementary).
- **capture**: the pcap (10 clusters). All attack classes except Web (3 captures) sit in one capture each, so most resamples miss at least one class, whose F1 is then 0: a stress test, not a calibrated interval.

Host-pair rows reproduce results/paired_diff.md and results/cluster_ci.md: **yes**.

## Attacker assignment (test sets)

| split    |   test flows |   flows assigned to an attacker | attack-labelled flows assigned   |   benign-labelled flows assigned |
|:---------|-------------:|--------------------------------:|:---------------------------------|---------------------------------:|
| temporal |      257,156 |                         206,547 | 204,163 / 204,163                |                            2,384 |
| random   |      257,162 |                         209,653 | 208,839 / 208,839                |                              814 |

## Number of clusters

| clusters        |   temporal test |   random test |   union |
|:----------------|----------------:|--------------:|--------:|
| host pair       |           3,465 |         3,858 |   4,641 |
| attacker host   |           3,413 |         3,738 |   4,520 |
| attacker device |           3,409 |         3,734 |   4,516 |
| capture         |              10 |            10 |      10 |

## Paired bootstrap of random minus temporal (union clusters, same draw for both splits)

| clusters        | model                |   union clusters |   temporal |   random |   random - temporal | paired 95% CI   |   share diff <= 0 | temporal CI (union)   | random CI (union)   | resamples missing a class (temporal / random)   |
|:----------------|:---------------------|-----------------:|-----------:|---------:|--------------------:|:----------------|------------------:|:----------------------|:--------------------|:------------------------------------------------|
| host pair       | decision tree        |            4,641 |      0.731 |    0.869 |               0.137 | [0.024, 0.278]  |             0.001 | [0.573, 0.829]        | [0.735, 0.876]      | 0.399 / 0.178                                   |
| host pair       | edge tree (deployed) |            4,641 |      0.725 |    0.867 |               0.142 | [0.025, 0.287]  |             0.001 | [0.564, 0.830]        | [0.732, 0.874]      | 0.399 / 0.178                                   |
| attacker host   | decision tree        |            4,520 |      0.731 |    0.869 |               0.137 | [0.002, 0.165]  |             0.017 | [0.466, 0.740]        | [0.486, 0.881]      | 0.829 / 0.827                                   |
| attacker host   | edge tree (deployed) |            4,520 |      0.725 |    0.867 |               0.142 | [0.004, 0.179]  |             0.007 | [0.458, 0.736]        | [0.485, 0.878]      | 0.829 / 0.827                                   |
| attacker device | decision tree        |            4,516 |      0.731 |    0.869 |               0.137 | [-0.004, 0.164] |             0.057 | [0.374, 0.742]        | [0.461, 0.883]      | 0.759 / 0.757                                   |
| attacker device | edge tree (deployed) |            4,516 |      0.725 |    0.867 |               0.142 | [-0.002, 0.176] |             0.036 | [0.374, 0.736]        | [0.460, 0.881]      | 0.759 / 0.757                                   |
| capture         | decision tree        |               10 |      0.731 |    0.869 |               0.137 | [0.001, 0.151]  |             0.022 | [0.361, 0.726]        | [0.448, 0.856]      | 0.971 / 0.971                                   |
| capture         | edge tree (deployed) |               10 |      0.725 |    0.867 |               0.142 | [0.004, 0.153]  |             0.013 | [0.360, 0.719]        | [0.447, 0.855]      | 0.971 / 0.971                                   |

## Marginal intervals (each split resamples its own clusters)

| clusters        | model                | split    |   n clusters |   macro-F1 | 95% CI         |   resamples missing a class |
|:----------------|:---------------------|:---------|-------------:|-----------:|:---------------|----------------------------:|
| host pair       | decision tree        | temporal |        3,465 |      0.731 | [0.577, 0.823] |                       0.407 |
| host pair       | decision tree        | random   |        3,858 |      0.869 | [0.735, 0.877] |                       0.176 |
| host pair       | edge tree (deployed) | temporal |        3,465 |      0.725 | [0.568, 0.822] |                       0.407 |
| host pair       | edge tree (deployed) | random   |        3,858 |      0.867 | [0.733, 0.875] |                       0.176 |
| attacker host   | decision tree        | temporal |        3,413 |      0.731 | [0.460, 0.739] |                       0.838 |
| attacker host   | decision tree        | random   |        3,738 |      0.869 | [0.487, 0.879] |                       0.859 |
| attacker host   | edge tree (deployed) | temporal |        3,413 |      0.725 | [0.449, 0.734] |                       0.838 |
| attacker host   | edge tree (deployed) | random   |        3,738 |      0.867 | [0.487, 0.877] |                       0.859 |
| attacker device | decision tree        | temporal |        3,409 |      0.731 | [0.372, 0.741] |                       0.759 |
| attacker device | decision tree        | random   |        3,734 |      0.869 | [0.468, 0.884] |                       0.769 |
| attacker device | edge tree (deployed) | temporal |        3,409 |      0.725 | [0.365, 0.738] |                       0.759 |
| attacker device | edge tree (deployed) | random   |        3,734 |      0.867 | [0.468, 0.882] |                       0.769 |
| capture         | decision tree        | temporal |           10 |      0.731 | [0.361, 0.726] |                       0.971 |
| capture         | decision tree        | random   |           10 |      0.869 | [0.469, 0.858] |                       0.974 |
| capture         | edge tree (deployed) | temporal |           10 |      0.725 | [0.360, 0.719] |                       0.971 |
| capture         | edge tree (deployed) | random   |           10 |      0.867 | [0.468, 0.858] |                       0.974 |

'resamples missing a class' = share of resamples in which at least one of the 8 classes has no test flow in that split.
