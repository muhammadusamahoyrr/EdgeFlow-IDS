# Random-minus-temporal gap without BruteForce, by cluster unit (round 17)

Deployed edge tree, paired bootstrap (1000 resamples, seed 0, same draws as cluster_sensitivity_cic_present.py). Script: src/analysis/gap_nobf_units.py.

| clusters        | classes                |   difference | paired CI, zero   |   share <= 0 (zero) | paired CI, present   |   share <= 0 (present) |
|:----------------|:-----------------------|-------------:|:------------------|--------------------:|:---------------------|-----------------------:|
| host pair       | all 8 classes          |        0.142 | [0.025, 0.287]    |               0.001 | [0.026, 0.212]       |                  0.001 |
| host pair       | without BruteForce (7) |        0.036 | [0.007, 0.199]    |               0.006 | [0.008, 0.105]       |                  0.006 |
| attacker host   | all 8 classes          |        0.142 | [0.004, 0.179]    |               0.007 | [0.007, 0.216]       |                  0.007 |
| attacker host   | without BruteForce (7) |        0.036 | [0.002, 0.083]    |               0.011 | [0.003, 0.095]       |                  0.011 |
| attacker device | all 8 classes          |        0.142 | [-0.002, 0.176]   |               0.036 | [-0.003, 0.225]      |                  0.036 |
| attacker device | without BruteForce (7) |        0.036 | [-0.002, 0.083]   |               0.036 | [-0.003, 0.099]      |                  0.036 |
| capture         | all 8 classes          |        0.142 | [0.004, 0.153]    |               0.013 | [0.007, 0.221]       |                  0.013 |
| capture         | without BruteForce (7) |        0.036 | [-0.004, 0.050]   |               0.054 | [-0.007, 0.064]      |                  0.054 |
