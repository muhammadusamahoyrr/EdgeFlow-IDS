# IoT-23: common-class macro-F1 with host-pair bootstrap, and paired split difference

Edge tree {'max_depth': 32, 'min_samples_leaf': 1, 'class_weight': 'balanced', 'random_state': 0}, trained on Zeek labels; splits of src/train_baseline.py. Common classes (train and test flows in both splits): Attack, Benign, C&C, PortScan. 1000 resamples, seed 0.

## Marginal intervals (each split's own host-pair clusters)

| split      |   test flows |   host-pair clusters |   common-class macro-F1 | host-pair 95% CI   |   all-class macro-F1 | all-class host-pair 95% CI   |
|:-----------|-------------:|---------------------:|------------------------:|:-------------------|---------------------:|:-----------------------------|
| temporal   |      226,875 |              207,778 |                   0.973 | [0.919, 0.983]     |                0.649 | [0.613, 0.655]               |
| stratified |      226,881 |              202,938 |                   0.956 | [0.904, 0.969]     |                0.863 | [0.638, 0.939]               |

## Paired bootstrap of the difference (stratified minus temporal)

The two test sets are different 30% subsets of the same flows, so their clusters overlap only partly: temporal 207,778 clusters, stratified 202,938, shared 62,366, union 348,350. Pairing: clusters are keyed by (capture, unordered host pair) over the union; each resample draws union clusters with replacement and applies the same multiplicities to both splits (a cluster absent from a split's test set contributes nothing to it); both macro-F1 values are recomputed from summed per-cluster confusion matrices and differenced. Percentile intervals.

| macro-F1 over                                  |   temporal |   stratified |   stratified - temporal | paired 95% CI of difference   |   share of resamples with diff <= 0 | temporal CI (union resampling)   | stratified CI (union resampling)   |   corr over resamples |
|:-----------------------------------------------|-----------:|-------------:|------------------------:|:------------------------------|------------------------------------:|:---------------------------------|:-----------------------------------|----------------------:|
| common classes (Attack, Benign, C&C, PortScan) |      0.973 |        0.956 |                  -0.017 | [-0.039, -0.009]              |                               0.991 | [0.918, 0.982]                   | [0.892, 0.970]                     |                 0.866 |
| all six classes                                |      0.649 |        0.863 |                   0.214 | [-0.014, 0.293]               |                               0.047 | [0.612, 0.655]                   | [0.634, 0.938]                     |                 0.103 |
