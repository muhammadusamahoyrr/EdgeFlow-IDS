# CIC-IoT2023 cluster sensitivity: macro-F1 over the classes present in each resample (review round 8)

Same clusterings, models, splits and bootstrap draws as results/cluster_sensitivity_cic.md (1000 resamples, seed 0). 'zero convention' = macro-F1 over all 8 classes with F1 = 0 for a class absent from the resample (the paper's convention; these columns reproduce results/cluster_sensitivity_cic.md); 'present classes' = macro-F1 averaged only over the classes with test support > 0 in that split's resample. Point estimates are identical (all classes present). Script: src/analysis/cluster_sensitivity_cic_present.py.

## Paired bootstrap of random minus temporal

| clusters        | model                |   difference | paired CI, zero convention   |   share <= 0 (zero) | paired CI, present classes   |   share <= 0 (present) | temporal CI, present (union)   | random CI, present (union)   |
|:----------------|:---------------------|-------------:|:-----------------------------|--------------------:|:-----------------------------|-----------------------:|:-------------------------------|:-----------------------------|
| host pair       | decision tree        |        0.137 | [0.024, 0.278]               |               0.001 | [0.026, 0.202]               |                  0.001 | [0.654, 0.833]                 | [0.838, 0.876]               |
| host pair       | edge tree (deployed) |        0.142 | [0.025, 0.287]               |               0.001 | [0.026, 0.212]               |                  0.001 | [0.645, 0.834]                 | [0.835, 0.874]               |
| attacker host   | decision tree        |        0.137 | [0.002, 0.165]               |               0.017 | [0.002, 0.202]               |                  0.017 | [0.647, 0.968]                 | [0.790, 0.986]               |
| attacker host   | edge tree (deployed) |        0.142 | [0.004, 0.179]               |               0.007 | [0.007, 0.216]               |                  0.007 | [0.634, 0.962]                 | [0.787, 0.985]               |
| attacker device | decision tree        |        0.137 | [-0.004, 0.164]              |               0.057 | [-0.007, 0.216]              |                  0.057 | [0.612, 0.980]                 | [0.814, 0.996]               |
| attacker device | edge tree (deployed) |        0.142 | [-0.002, 0.176]              |               0.036 | [-0.003, 0.225]              |                  0.036 | [0.603, 0.974]                 | [0.811, 0.996]               |
| capture         | decision tree        |        0.137 | [0.001, 0.151]               |               0.022 | [0.002, 0.223]               |                  0.022 | [0.587, 0.963]                 | [0.755, 0.983]               |
| capture         | edge tree (deployed) |        0.142 | [0.004, 0.153]               |               0.013 | [0.007, 0.221]               |                  0.013 | [0.586, 0.958]                 | [0.752, 0.982]               |

## Marginal intervals (each split resamples its own clusters)

| clusters        | model                | split    |   macro-F1 | CI, zero convention   | CI, present classes   |
|:----------------|:---------------------|:---------|-----------:|:----------------------|:----------------------|
| host pair       | decision tree        | temporal |      0.731 | [0.577, 0.823]        | [0.660, 0.827]        |
| host pair       | decision tree        | random   |      0.869 | [0.735, 0.877]        | [0.835, 0.877]        |
| host pair       | edge tree (deployed) | temporal |      0.725 | [0.568, 0.822]        | [0.650, 0.827]        |
| host pair       | edge tree (deployed) | random   |      0.867 | [0.733, 0.875]        | [0.833, 0.875]        |
| attacker host   | decision tree        | temporal |      0.731 | [0.460, 0.739]        | [0.655, 0.967]        |
| attacker host   | decision tree        | random   |      0.869 | [0.487, 0.879]        | [0.791, 0.985]        |
| attacker host   | edge tree (deployed) | temporal |      0.725 | [0.449, 0.734]        | [0.634, 0.959]        |
| attacker host   | edge tree (deployed) | random   |      0.867 | [0.487, 0.877]        | [0.789, 0.984]        |
| attacker device | decision tree        | temporal |      0.731 | [0.372, 0.741]        | [0.613, 0.981]        |
| attacker device | decision tree        | random   |      0.869 | [0.468, 0.884]        | [0.814, 0.996]        |
| attacker device | edge tree (deployed) | temporal |      0.725 | [0.365, 0.738]        | [0.597, 0.975]        |
| attacker device | edge tree (deployed) | random   |      0.867 | [0.468, 0.882]        | [0.811, 0.996]        |
| capture         | decision tree        | temporal |      0.731 | [0.361, 0.726]        | [0.587, 0.963]        |
| capture         | decision tree        | random   |      0.869 | [0.469, 0.858]        | [0.766, 0.983]        |
| capture         | edge tree (deployed) | temporal |      0.725 | [0.360, 0.719]        | [0.586, 0.958]        |
| capture         | edge tree (deployed) | random   |      0.867 | [0.468, 0.858]        | [0.763, 0.983]        |
