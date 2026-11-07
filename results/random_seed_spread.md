# CIC-IoT2023: random-split seed spread of macro-F1 (review round 8)

Stratified 70/30 split (sklearn train_test_split), macro-F1 over all 8 classes; seeds [0, 1, 2, 3, 4]. Edge tree = config.EDGE_TREE {'max_depth': 32, 'min_samples_leaf': 1, 'class_weight': 'balanced', 'random_state': 0} with random_state varied. Script: src/analysis/random_seed_spread.py. SD = sample SD over the 5 seeds.

| model                | variant                        |   seed 0 |   seed 1 |   seed 2 |   seed 3 |   seed 4 |   mean |     SD |    min |    max |   range |
|:---------------------|:-------------------------------|---------:|---------:|---------:|---------:|---------:|-------:|-------:|-------:|-------:|--------:|
| decision tree        | joint (split = model seed)     |   0.8687 |   0.8535 |   0.8609 |   0.8726 |   0.8616 | 0.8635 | 0.0074 | 0.8535 | 0.8726 |  0.0191 |
| decision tree        | split seed only (model seed 0) |   0.8687 |   0.8523 |   0.8594 |   0.8722 |   0.8599 | 0.8625 | 0.008  | 0.8523 | 0.8722 |  0.0199 |
| decision tree        | model seed only (split seed 0) |   0.8687 |   0.8675 |   0.8686 |   0.8679 |   0.8663 | 0.8678 | 0.001  | 0.8663 | 0.8687 |  0.0025 |
| edge tree (deployed) | joint (split = model seed)     |   0.8669 |   0.8526 |   0.8591 |   0.8728 |   0.862  | 0.8627 | 0.0077 | 0.8526 | 0.8728 |  0.0202 |
| edge tree (deployed) | split seed only (model seed 0) |   0.8669 |   0.8535 |   0.86   |   0.8697 |   0.86   | 0.862  | 0.0064 | 0.8535 | 0.8697 |  0.0163 |
| edge tree (deployed) | model seed only (split seed 0) |   0.8669 |   0.8666 |   0.8692 |   0.8681 |   0.8687 | 0.8679 | 0.0011 | 0.8666 | 0.8692 |  0.0027 |

Seed 0 reproduces results/baseline_stratified/metrics.json (decision tree, edge tree) if the seed-0 column equals the macro-F1 reported there (checked below).

- decision tree: metrics.json macro_f1 = 0.8687117580049233, seed 0 here = 0.868712
- edge tree (deployed): metrics.json macro_f1 = 0.866912372989346, seed 0 here = 0.866912
