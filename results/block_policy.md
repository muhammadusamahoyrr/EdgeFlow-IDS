# Blocking policy tuning (validation = last 20% of the training period)

|   k | ignore_mitm_flow_verdicts   |   attack_pairs |   attack_pairs_blocked |   false_blocks |   attack_flows_after_block |
|----:|:----------------------------|---------------:|-----------------------:|---------------:|---------------------------:|
|   1 | False                       |             42 |                     29 |            128 |                      0.996 |
|   2 | False                       |             42 |                     26 |             46 |                      0.996 |
|   3 | False                       |             42 |                     21 |             27 |                      0.995 |
|   5 | False                       |             42 |                     21 |             13 |                      0.995 |
|  10 | False                       |             42 |                     20 |              6 |                      0.995 |
|   1 | True                        |             42 |                     28 |             59 |                      0.996 |
|   2 | True                        |             42 |                     26 |             15 |                      0.996 |
|   3 | True                        |             42 |                     21 |              6 |                      0.995 |
|   5 | True                        |             42 |                     21 |              3 |                      0.995 |
|  10 | True                        |             42 |                     20 |              1 |                      0.995 |

Chosen: `{'min_attack_verdicts': 10, 'ignore_mitm_flow_verdicts': True}`
