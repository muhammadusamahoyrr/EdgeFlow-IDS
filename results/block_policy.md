# Blocking policy tuning (validation = last 20% of the training period)

|   k | ignore_mitm_flow_verdicts   |   attack_pairs |   attack_pairs_blocked |   false_blocks |   attack_flows_after_block |
|----:|:----------------------------|---------------:|-----------------------:|---------------:|---------------------------:|
|   1 | False                       |             41 |                     28 |            122 |                      0.996 |
|   2 | False                       |             41 |                     25 |             44 |                      0.996 |
|   3 | False                       |             41 |                     21 |             28 |                      0.995 |
|   5 | False                       |             41 |                     21 |             14 |                      0.995 |
|  10 | False                       |             41 |                     20 |              7 |                      0.995 |
|   1 | True                        |             41 |                     27 |             56 |                      0.996 |
|   2 | True                        |             41 |                     25 |             15 |                      0.996 |
|   3 | True                        |             41 |                     21 |              7 |                      0.995 |
|   5 | True                        |             41 |                     21 |              4 |                      0.995 |
|  10 | True                        |             41 |                     20 |              1 |                      0.995 |

Chosen: `{'min_attack_verdicts': 10, 'ignore_mitm_flow_verdicts': True}`
