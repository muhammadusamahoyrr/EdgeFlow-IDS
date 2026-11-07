"""CIC-IoT2023 cluster sensitivity, robustness variant: macro-F1 over the classes PRESENT in each
bootstrap resample (review round 8).

With coarse cluster units (attacker host, capture) most resamples omit at least one class entirely
(results/cluster_sensitivity_cic.md: 76-97%), because BruteForce, DoS-HTTP, Recon and MITM-ARP each
have a single attacker and every attack class except Web sits in one capture. The paper's convention
(sklearn macro-F1 over all 8 classes, zero_division=0) then scores the missing class F1 = 0 in that
resample, which drags the marginal intervals down and, in the paired bootstrap, sets the class's
contribution to the difference to 0 whenever its cluster is not drawn. This script recomputes, with
the SAME draws (same rng sequence as analysis/paired_diff.paired_bootstrap and own_boot), both
  zero      : macro-F1 over all 8 classes, missing class F1 = 0 (reproduces cluster_sensitivity_cic.md)
  present   : macro-F1 over the classes with test support > 0 in that split's resample.
Clusterings, models and splits are imported from analysis/cluster_sensitivity_cic.py.

Usage: python src/analysis/cluster_sensitivity_cic_present.py
Output: results/cluster_sensitivity_cic_present.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.cluster_sensitivity_cic import SCHEMES, union_ids  # noqa: E402
from analysis.paired_diff import B, SEED, per_cluster_cm  # noqa: E402
from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import SPLITS  # noqa: E402


def f1s(s, k):
    """s: (..., k*(k+1)) summed counts -> (per-class F1, per-class support)."""
    cm = s.reshape(*s.shape[:-1], k, k + 1)
    tp = np.einsum("...ii->...i", cm[..., :k, :k])
    sup = cm.sum(-1)
    pred = cm[..., :k, :k].sum(-2)
    den = sup + pred
    return np.divide(2 * tp, den, out=np.zeros_like(tp), where=den > 0), sup


def both(s, k):
    f, sup = f1s(s, k)
    present = sup > 0
    return f.mean(-1), (f * present).sum(-1) / np.maximum(present.sum(-1), 1)


def pct(v):
    return f"[{np.percentile(v, 2.5):.3f}, {np.percentile(v, 97.5):.3f}]"


def main():
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    classes = sorted(df.label.unique())
    k = len(classes)
    parts = {s: fn(df) for s, fn in SPLITS.items()}
    tests = [parts["temporal"][1], parts["stratified"][1]]
    preds = {}
    for name, params in (("decision tree", dict(class_weight="balanced", random_state=0)),
                         ("edge tree (deployed)", EDGE_TREE)):
        for split, (train, test) in parts.items():
            feats = feature_columns(train)
            m = DecisionTreeClassifier(**params).fit(train[feats].to_numpy(np.float32), train.label)
            preds[name, split] = (test.label.to_numpy(), m.predict(test[feats].to_numpy(np.float32)))

    paired, marg = [], []
    for scheme in SCHEMES:
        (cl_t, cl_s), n_u = union_ids(tests, scheme)
        for name in ("decision tree", "edge tree (deployed)"):
            # paired (union) bootstrap, same draws as paired_bootstrap
            cma = per_cluster_cm(*preds[name, "temporal"], cl_t, classes, n_u)
            cmb = per_cluster_cm(*preds[name, "stratified"], cl_s, classes, n_u)
            rng = np.random.default_rng(SEED)
            z, p = np.empty((B, 2)), np.empty((B, 2))
            for i in range(B):
                w = np.bincount(rng.integers(0, n_u, n_u), minlength=n_u).astype(np.float64)
                for j, cm in enumerate((cma, cmb)):
                    z[i, j], p[i, j] = both(w @ cm, k)
            pt_z = [both(cm.sum(0), k)[0] for cm in (cma, cmb)]
            dz, dp = z[:, 1] - z[:, 0], p[:, 1] - p[:, 0]
            paired.append({"clusters": scheme, "model": name, "difference": round(pt_z[1] - pt_z[0], 3),
                           "paired CI, zero convention": pct(dz), "share <= 0 (zero)": round(float((dz <= 0).mean()), 3),
                           "paired CI, present classes": pct(dp), "share <= 0 (present)": round(float((dp <= 0).mean()), 3),
                           "temporal CI, present (union)": pct(p[:, 0]), "random CI, present (union)": pct(p[:, 1])})
            print(paired[-1], flush=True)
            # marginal, own clusters, same draws as own_boot / cluster_ci
            for split, cl in (("temporal", cl_t), ("stratified", cl_s)):
                c = pd.factorize(cl)[0]
                n = c.max() + 1
                cm = per_cluster_cm(*preds[name, split], c, classes, n)
                rng = np.random.default_rng(SEED)
                v = np.empty((B, 2))
                for i in range(B):
                    w = np.bincount(rng.integers(0, n, n), minlength=n).astype(np.float64)
                    v[i] = both(w @ cm, k)
                marg.append({"clusters": scheme, "model": name,
                             "split": "random" if split == "stratified" else split,
                             "macro-F1": round(float(both(cm.sum(0), k)[0]), 3),
                             "CI, zero convention": pct(v[:, 0]), "CI, present classes": pct(v[:, 1])})
                print(marg[-1], flush=True)

    md = ["# CIC-IoT2023 cluster sensitivity: macro-F1 over the classes present in each resample (review round 8)", "",
          "Same clusterings, models, splits and bootstrap draws as results/cluster_sensitivity_cic.md "
          f"({B} resamples, seed {SEED}). 'zero convention' = macro-F1 over all {k} classes with F1 = 0 for a class "
          "absent from the resample (the paper's convention; these columns reproduce "
          "results/cluster_sensitivity_cic.md); 'present classes' = macro-F1 averaged only over the classes with "
          "test support > 0 in that split's resample. Point estimates are identical (all classes present). "
          "Script: src/analysis/cluster_sensitivity_cic_present.py.", "",
          "## Paired bootstrap of random minus temporal", "", pd.DataFrame(paired).to_markdown(index=False), "",
          "## Marginal intervals (each split resamples its own clusters)", "", pd.DataFrame(marg).to_markdown(index=False)]
    (RESULTS / "cluster_sensitivity_cic_present.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
