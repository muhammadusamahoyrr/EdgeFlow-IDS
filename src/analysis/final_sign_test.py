"""Coarse-cluster sign / permutation tests of random minus temporal (final review, item M3 / A5).

Instead of percentile bootstrap intervals over 10 captures or ~20 attackers, list the per-cluster
paired differences and test their sign exactly. Per cluster, macro-F1 is computed over the classes
present in that cluster's test flows in BOTH splits (F1 within the cluster: a prediction of class c
on another class's flow in the cluster is a false positive for c). Clusters with no class present in
both splits are listed but not tested.

Cluster units (analysis/cluster_sensitivity_cic.keys):
  capture         : the pcap (10)
  attacker host   : (capture, attacker IP); only attacker clusters (flows involving a confirmed
                    attacker, data/attackers.json); benign-only host pairs are not part of this test
  attacker device : attacker IP across captures (only attacker clusters)
Tests: exact two-sided sign test (binomial, ties dropped) and exact sign-flip permutation test of the
mean difference (all 2^n sign patterns; two-sided, |mean| >= observed).

Trees: baseline decision tree (Table perclass) and deployed edge tree; seed 0.

Usage: python src/analysis/final_sign_test.py
Output: results/final/sign_test.md
"""
import itertools
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import binomtest  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.cluster_sensitivity_cic import keys  # noqa: E402
from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import SPLITS  # noqa: E402

OUT = RESULTS / "final"
TREES = {"decision tree (Table perclass)": dict(class_weight="balanced", random_state=0),
         "deployed edge tree": EDGE_TREE}


def perm_p(d):
    d = np.asarray(d, float)
    n = len(d)
    if n == 0:
        return None
    obs = abs(d.mean())
    if n <= 22:
        signs = np.array(list(itertools.product([1, -1], repeat=n)), dtype=float)
        stats = np.abs(signs @ d / n)
    else:
        rng = np.random.default_rng(0)
        signs = rng.choice([1.0, -1.0], size=(200000, n))
        stats = np.abs(signs @ d / n)
    return float((stats >= obs - 1e-12).mean())


def sign_p(d):
    d = np.asarray(d, float)
    nz = d[d != 0]
    if len(nz) == 0:
        return None, 0, 0
    pos = int((nz > 0).sum())
    return float(binomtest(pos, len(nz), 0.5).pvalue), pos, len(nz)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    parts = {s: fn(df) for s, fn in SPLITS.items()}
    preds = {}
    for name, params in TREES.items():
        for split, (train, test) in parts.items():
            feats = feature_columns(train)
            m = DecisionTreeClassifier(**params).fit(train[feats].to_numpy(np.float32), train.label)
            preds[name, split] = m.predict(test[feats].to_numpy(np.float32))
    md = ["# Coarse-cluster sign and permutation tests, random minus temporal (final review M3)", "",
          "Script: src/analysis/final_sign_test.py. Per cluster: macro-F1 over the classes present in the cluster's "
          "test flows in both splits; difference = random (stratified 70/30, seed 0) minus temporal. Exact two-sided "
          "sign test (ties dropped) and exact sign-flip permutation test of the mean difference.", ""]
    summary = []
    for scheme in ("capture", "attacker host", "attacker device"):
        kt = keys(parts["temporal"][1], scheme)
        ks = keys(parts["stratified"][1], scheme)
        yt, ys = parts["temporal"][1].label.to_numpy(), parts["stratified"][1].label.to_numpy()
        clusters = sorted(set(kt) | set(ks))
        if scheme != "capture":
            clusters = [c for c in clusters if str(c).startswith("att|")]
        for name in TREES:
            pt, ps = preds[name, "temporal"], preds[name, "stratified"]
            rows = []
            for c in clusters:
                mt, ms = kt == c, ks == c
                cls = sorted(set(yt[mt]) & set(ys[ms]))
                r = {"cluster": str(c).replace("att|", ""), "temporal flows": int(mt.sum()), "random flows": int(ms.sum()),
                     "classes (both splits)": ", ".join(cls)}
                if cls:
                    a = f1_score(yt[mt], pt[mt], labels=cls, average="macro", zero_division=0)
                    b = f1_score(ys[ms], ps[ms], labels=cls, average="macro", zero_division=0)
                    r.update({"temporal macro-F1": round(a, 4), "random macro-F1": round(b, 4),
                              "random - temporal": round(b - a, 4)})
                rows.append(r)
            t = pd.DataFrame(rows)
            d = t["random - temporal"].dropna().to_numpy() if "random - temporal" in t else np.array([])
            sp, pos, nz = sign_p(d)
            pp = perm_p(d)
            summary.append({"cluster unit": scheme, "tree": name, "clusters tested": len(d),
                            "positive / non-zero": f"{pos} / {nz}", "mean diff": round(float(d.mean()), 4) if len(d) else None,
                            "median diff": round(float(np.median(d)), 4) if len(d) else None,
                            "sign test p (two-sided)": round(sp, 4) if sp is not None else None,
                            "permutation p (two-sided)": round(pp, 4) if pp is not None else None})
            print(summary[-1], flush=True)
            md += [f"## {scheme}, {name}", "", t.to_markdown(index=False), ""]
    md[4:4] =["## Summary", "", pd.DataFrame(summary).to_markdown(index=False), "",
               "With n non-zero clusters the smallest attainable two-sided sign-test p is 2 * 0.5^n "
               "(n = 10: 0.002; n = 5: 0.0625).", ""]
    (OUT / "sign_test.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
