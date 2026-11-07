"""Random-minus-temporal gap WITHOUT BruteForce at every cluster unit, both conventions (round 17, item 2).

The paper reports the without-BruteForce gap only with host-pair clusters (+0.036 [0.007, 0.199],
results/final/gap_decomposition.md, zero convention). Here the deployed edge tree's paired bootstrap
is repeated for the 7 classes other than BruteForce at each cluster unit of
analysis/cluster_sensitivity_cic.py (host pair, attacker host, attacker device, capture), with the
same draws (seed 0, 1000 resamples), under
  zero    : macro-F1 over the 7 classes, a class absent from a resample scores F1 = 0
  present : macro-F1 over those of the 7 classes with test support > 0 in that split's resample.
The all-classes rows are included as a check against results/cluster_sensitivity_cic_present.md.

Usage: python src/analysis/gap_nobf_units.py
Output: results/final/gap_nobf_units.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.cluster_sensitivity_cic import SCHEMES, union_ids  # noqa: E402
from analysis.cluster_sensitivity_cic_present import f1s  # noqa: E402
from analysis.paired_diff import B, SEED, per_cluster_cm  # noqa: E402
from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import SPLITS  # noqa: E402


def conv(s, k, sel):
    f, sup = f1s(s, k)
    f, sup = f[..., sel], sup[..., sel]
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
    for split, (train, test) in parts.items():
        feats = feature_columns(train)
        m = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train.label)
        preds[split] = (test.label.to_numpy(), m.predict(test[feats].to_numpy(np.float32)))
    del parts
    sels = {"all 8 classes": list(range(k)), "without BruteForce (7)": [i for i, c in enumerate(classes) if c != "BruteForce"]}
    rows = []
    for scheme in SCHEMES:
        (cl_t, cl_s), n_u = union_ids(tests, scheme)
        cma = per_cluster_cm(*preds["temporal"], cl_t, classes, n_u)
        cmb = per_cluster_cm(*preds["stratified"], cl_s, classes, n_u)
        for sname, sel in sels.items():
            rng = np.random.default_rng(SEED)
            z, p = np.empty((B, 2)), np.empty((B, 2))
            for i in range(B):
                w = np.bincount(rng.integers(0, n_u, n_u), minlength=n_u).astype(np.float64)
                for j, cm in enumerate((cma, cmb)):
                    z[i, j], p[i, j] = conv(w @ cm, k, sel)
            pt = [conv(cm.sum(0), k, sel)[0] for cm in (cma, cmb)]
            dz, dp = z[:, 1] - z[:, 0], p[:, 1] - p[:, 0]
            rows.append({"clusters": scheme, "classes": sname, "difference": round(float(pt[1] - pt[0]), 3),
                         "paired CI, zero": pct(dz), "share <= 0 (zero)": round(float((dz <= 0).mean()), 3),
                         "paired CI, present": pct(dp), "share <= 0 (present)": round(float((dp <= 0).mean()), 3)})
            print(rows[-1], flush=True)
    md = ["# Random-minus-temporal gap without BruteForce, by cluster unit (round 17)", "",
          f"Deployed edge tree, paired bootstrap ({B} resamples, seed {SEED}, same draws as "
          "cluster_sensitivity_cic_present.py). Script: src/analysis/gap_nobf_units.py.", "",
          pd.DataFrame(rows).to_markdown(index=False)]
    (RESULTS / "final" / "gap_nobf_units.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
