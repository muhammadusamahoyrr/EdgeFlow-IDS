# Flow-level versus host-pair (cluster) bootstrap intervals

1000 resamples of whole (capture, host pair) clusters; the flow bootstrap resamples single test flows (200 resamples, as in the baselines).

| split      | model         |   macro-F1 | flow bootstrap 95% CI   | host-pair bootstrap 95% CI   |   host-pair clusters |
|:-----------|:--------------|-----------:|:------------------------|:-----------------------------|---------------------:|
| temporal   | decision tree |      0.731 | [0.712, 0.742]          | [0.577, 0.823]               |                3,465 |
| temporal   | edge tree     |      0.725 | [0.702, 0.741]          | [0.568, 0.822]               |                3,465 |
| stratified | decision tree |      0.869 | [0.861, 0.875]          | [0.735, 0.877]               |                3,858 |
| stratified | edge tree     |      0.867 | [0.860, 0.873]          | [0.733, 0.875]               |                3,858 |
