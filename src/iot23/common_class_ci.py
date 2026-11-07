"""IoT-23: common-class macro-F1 (Attack, Benign, C&C, PortScan) for the temporal and stratified
splits with host-pair bootstrap intervals, and a paired bootstrap of stratified minus temporal.

Setup as in src/iot23/splits.py (edge tree, config.EDGE_TREE, trained on Zeek labels; splits of
src/train_baseline.py). Common-class macro-F1 = sklearn f1_score(labels=common, average='macro'):
per-class F1 of the four common classes, where predictions of DDoS/FileDownload and true
DDoS/FileDownload flows still count as false positives / false negatives of the common classes.

Intervals (1000 resamples, seed 0):
  marginal: each split's own (capture, unordered host pair) clusters, as in splits.py;
  paired:   clusters keyed over the union of both test sets (analysis/paired_diff.py); the same
            cluster multiplicities are applied to both splits and the difference is recomputed.
The all-class macro-F1 difference (0.863 - 0.649) is given too, with the same pairing.

Usage: python src/iot23/common_class_ci.py
Output: results/iot23/common_class_ci.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.paired_diff import B, SEED, macro_sel, paired_bootstrap, per_cluster_cm, union_cluster_ids  # noqa: E402
from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import SPLITS  # noqa: E402

COMMON = ["Attack", "Benign", "C&C", "PortScan"]


def own_cluster_ci(y, p, cl_union, classes, sel, b=B, seed=SEED):
    """Marginal interval resampling only this split's own clusters (re-indexed)."""
    cl = pd.factorize(cl_union)[0]
    n = cl.max() + 1
    cm = per_cluster_cm(y, p, cl, classes, n)
    rng = np.random.default_rng(seed)
    v = np.empty(b)
    for i in range(b):
        w = np.bincount(rng.integers(0, n, n), minlength=n).astype(np.float64)
        v[i] = macro_sel(w @ cm, len(classes), sel)
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), n


def main():
    df = pd.read_parquet(PROCESSED / "iot23_flows.parquet")
    classes = sorted(df.label.unique())
    sel = [classes.index(c) for c in COMMON]
    parts = {s: fn(df) for s, fn in SPLITS.items()}
    (cl_t, cl_s), n_cl = union_cluster_ids([parts["temporal"][1], parts["stratified"][1]])
    preds = {}
    for split, (train, test) in parts.items():
        feats = feature_columns(train)
        m = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train.label)
        preds[split] = (test.label.to_numpy(), m.predict(test[feats].to_numpy(np.float32)))
    cls = {"temporal": cl_t, "stratified": cl_s}
    marg = []
    for split in parts:
        y, p = preds[split]
        k = len(classes)
        cm = per_cluster_cm(y, p, pd.factorize(cls[split])[0], classes, pd.factorize(cls[split])[0].max() + 1)
        lo, hi, n = own_cluster_ci(y, p, cls[split], classes, sel)
        alo, ahi, _ = own_cluster_ci(y, p, cls[split], classes, list(range(k)))
        marg.append({"split": split, "test flows": f"{len(y):,}", "host-pair clusters": f"{n:,}",
                     "common-class macro-F1": round(macro_sel(cm.sum(0), k, sel), 3),
                     "host-pair 95% CI": f"[{lo:.3f}, {hi:.3f}]",
                     "all-class macro-F1": round(macro_sel(cm.sum(0), k, list(range(k))), 3),
                     "all-class host-pair 95% CI": f"[{alo:.3f}, {ahi:.3f}]"})
        print(marg[-1])
    paired = []
    for name, s in (("common classes (Attack, Benign, C&C, PortScan)", sel), ("all six classes", None)):
        r = paired_bootstrap((*preds["temporal"], cl_t, n_cl), (*preds["stratified"], cl_s, n_cl), classes, sel=s)
        paired.append({"macro-F1 over": name, "temporal": round(r["A"], 3), "stratified": round(r["B"], 3),
                       "stratified - temporal": round(r["diff"], 3),
                       "paired 95% CI of difference": f"[{r['diff_ci'][0]:.3f}, {r['diff_ci'][1]:.3f}]",
                       "share of resamples with diff <= 0": round(r["p_le0"], 4),
                       "temporal CI (union resampling)": f"[{r['A_ci'][0]:.3f}, {r['A_ci'][1]:.3f}]",
                       "stratified CI (union resampling)": f"[{r['B_ci'][0]:.3f}, {r['B_ci'][1]:.3f}]",
                       "corr over resamples": round(r["corr"], 3)})
        info = r
        print(paired[-1])
    md = ["# IoT-23: common-class macro-F1 with host-pair bootstrap, and paired split difference", "",
          f"Edge tree {EDGE_TREE}, trained on Zeek labels; splits of src/train_baseline.py. Common classes "
          f"(train and test flows in both splits): {', '.join(COMMON)}. {B} resamples, seed {SEED}.", "",
          "## Marginal intervals (each split's own host-pair clusters)", "",
          pd.DataFrame(marg).to_markdown(index=False), "",
          "## Paired bootstrap of the difference (stratified minus temporal)", "",
          "The two test sets are different 30% subsets of the same flows, so their clusters overlap only "
          f"partly: temporal {info['n_A']:,} clusters, stratified {info['n_B']:,}, shared {info['n_shared']:,}, "
          f"union {info['n_union']:,}. Pairing: clusters are keyed by (capture, unordered host pair) over the "
          "union; each resample draws union clusters with replacement and applies the same multiplicities to "
          "both splits (a cluster absent from a split's test set contributes nothing to it); both macro-F1 "
          "values are recomputed from summed per-cluster confusion matrices and differenced. Percentile "
          "intervals.", "",
          pd.DataFrame(paired).to_markdown(index=False)]
    (RESULTS / "iot23" / "common_class_ci.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
