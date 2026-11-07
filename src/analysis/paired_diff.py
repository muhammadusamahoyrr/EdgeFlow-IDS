"""Paired host-pair bootstrap of the macro-F1 difference between two splits (reviewer request).

The temporal and stratified (random) test sets are different subsets of the same flow table, so
their host-pair clusters overlap only partly. Pairing: clusters are keyed by (capture file,
unordered host pair) over the UNION of both test sets; each bootstrap resample draws union
clusters with replacement and applies the same cluster multiplicities to both splits (a cluster
absent from one split's test set contributes nothing to that split). Both macro-F1 values are
recomputed from summed per-cluster confusion matrices and their difference is recorded.
This keeps the correlation between the two estimates (shared hosts, shared captures) in the
interval of the difference.

Used here for CIC-IoT2023 (edge tree and unconstrained decision tree, same setup as
cluster_ci.py); src/iot23/common_class_ci.py reuses paired_bootstrap() for IoT-23.

Usage: python src/analysis/paired_diff.py
Output: results/paired_diff.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402

B = 1000
SEED = 0


def union_cluster_ids(tests):
    """tests: list of DataFrames (source_file, src_ip, dst_ip). Returns one id array per test set,
    ids shared across sets for the same (capture, unordered host pair)."""
    keys = []
    for t in tests:
        s, d = t.src_ip.astype(str).to_numpy(), t.dst_ip.astype(str).to_numpy()
        a, b = np.where(s < d, s, d), np.where(s < d, d, s)
        keys.append(t.source_file.astype(str).to_numpy().astype(object) + "|" + a.astype(object) + "|" + b.astype(object))
    codes, uniq = pd.factorize(np.concatenate(keys))
    out, i = [], 0
    for k in keys:
        out.append(codes[i:i + len(k)])
        i += len(k)
    return out, len(uniq)


def per_cluster_cm(y, pred, clusters, classes, n_cl):
    """(n_cl, k, k+1) confusion counts; column k = predicted label outside `classes`."""
    k = len(classes)
    idx = {c: i for i, c in enumerate(classes)}
    yi = np.array([idx[v] for v in y])
    pi = np.array([idx.get(v, k) for v in pred])
    cell = (clusters * k + yi) * (k + 1) + pi
    return np.bincount(cell, minlength=n_cl * k * (k + 1)).reshape(n_cl, k * (k + 1)).astype(np.float64)


def macro_sel(cm_flat, k, sel):
    """Macro-F1 over class indices `sel` from flattened (..., k*(k+1)) confusion counts
    (same as sklearn f1_score(labels=sel classes, average='macro', zero_division=0))."""
    cm = cm_flat.reshape(*cm_flat.shape[:-1], k, k + 1)
    tp = np.einsum("...ii->...i", cm[..., :k, :k])
    support = cm.sum(axis=-1)
    predicted = cm[..., :k, :k].sum(axis=-2)
    denom = support + predicted
    f1 = np.divide(2 * tp, denom, out=np.zeros_like(tp), where=denom > 0)
    return f1[..., sel].mean(axis=-1)


def paired_bootstrap(a, b, classes, sel=None, b_res=B, seed=SEED):
    """a, b: (y, pred, cluster ids) for split A and split B, cluster ids from union_cluster_ids
    (same id space, n_cl = number of union clusters passed as a[3]). Returns dict with point
    values, marginal CIs under the paired (union) resampling, and the CI of B - A."""
    (ya, pa, ca, n_cl), (yb, pb, cb, _) = a, b
    k = len(classes)
    sel = list(range(k)) if sel is None else sel
    cma = per_cluster_cm(ya, pa, ca, classes, n_cl)
    cmb = per_cluster_cm(yb, pb, cb, classes, n_cl)
    pt_a, pt_b = macro_sel(cma.sum(0), k, sel), macro_sel(cmb.sum(0), k, sel)
    labs = [classes[i] for i in sel]
    assert abs(pt_a - f1_score(ya, pa, labels=labs, average="macro", zero_division=0)) < 1e-9
    assert abs(pt_b - f1_score(yb, pb, labels=labs, average="macro", zero_division=0)) < 1e-9
    both = np.stack([cma, cmb], axis=1).reshape(n_cl, -1)  # (n_cl, 2*k*(k+1))
    rng = np.random.default_rng(seed)
    va, vb = np.empty(b_res), np.empty(b_res)
    for i in range(b_res):
        w = np.bincount(rng.integers(0, n_cl, n_cl), minlength=n_cl).astype(np.float64)
        s = (w @ both).reshape(2, -1)
        va[i], vb[i] = macro_sel(s[0], k, sel), macro_sel(s[1], k, sel)
    d = vb - va
    pct = lambda v: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))  # noqa: E731
    return {"A": pt_a, "B": pt_b, "diff": pt_b - pt_a, "A_ci": pct(va), "B_ci": pct(vb), "diff_ci": pct(d),
            "p_le0": float((d <= 0).mean()), "sd_diff": float(d.std(ddof=1)),
            "corr": float(np.corrcoef(va, vb)[0, 1]), "n_union": n_cl,
            "n_A": int(len(np.unique(ca))), "n_B": int(len(np.unique(cb))),
            "n_shared": int(len(np.intersect1d(np.unique(ca), np.unique(cb))))}


def fmt(r):
    return {"temporal macro-F1": round(r["A"], 3), "random macro-F1": round(r["B"], 3),
            "difference (random - temporal)": round(r["diff"], 3),
            "paired 95% CI of difference": f"[{r['diff_ci'][0]:.3f}, {r['diff_ci'][1]:.3f}]",
            "share of resamples with diff <= 0": round(r["p_le0"], 4),
            "temporal CI (union resampling)": f"[{r['A_ci'][0]:.3f}, {r['A_ci'][1]:.3f}]",
            "random CI (union resampling)": f"[{r['B_ci'][0]:.3f}, {r['B_ci'][1]:.3f}]",
            "corr(temporal, random) over resamples": round(r["corr"], 3)}


def main():
    from sklearn.tree import DecisionTreeClassifier

    from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns
    from train_baseline import SPLITS

    df = pd.read_parquet(PROCESSED / "flows.parquet")
    classes = sorted(df.label.unique())
    parts = {s: fn(df) for s, fn in SPLITS.items()}
    (cl_t, cl_s), n_cl = union_cluster_ids([parts["temporal"][1], parts["stratified"][1]])
    rows, info = [], None
    for name, params in (("edge tree", EDGE_TREE), ("decision tree", dict(class_weight="balanced", random_state=0))):
        res = {}
        for split, (train, test) in parts.items():
            feats = feature_columns(train)
            m = DecisionTreeClassifier(**params).fit(train[feats].to_numpy(np.float32), train.label)
            res[split] = (test.label.to_numpy(), m.predict(test[feats].to_numpy(np.float32)))
        r = paired_bootstrap((*res["temporal"], cl_t, n_cl), (*res["stratified"], cl_s, n_cl), classes)
        rows.append({"model": name, **fmt(r)})
        info = r
        print(rows[-1])
    md = ["# CIC-IoT2023: paired host-pair bootstrap of the random-minus-temporal macro-F1 difference", "",
          f"Splits and models as in src/analysis/cluster_ci.py (temporal = per capture, first 70% of flows by "
          f"start time; random = stratified 70/30, seed 0). Macro-F1 over all {len(classes)} classes "
          f"({', '.join(classes)}). {B} resamples, seed {SEED}.", "",
          "Pairing: clusters = (capture file, unordered host pair) keyed over the union of both test sets "
          f"({info['n_union']:,} union clusters; temporal test {info['n_A']:,}, random test {info['n_B']:,}, "
          f"shared {info['n_shared']:,}). Each resample draws union clusters with replacement and applies the "
          "same multiplicities to both splits; a cluster missing from one test set contributes nothing to it. "
          "Both macro-F1 values are recomputed and differenced per resample (percentile interval).", "",
          pd.DataFrame(rows).to_markdown(index=False), "",
          "The marginal intervals under union resampling are close to, but not identical with, those in "
          "results/cluster_ci.md (which resample each split's own clusters); the per-split numbers of drawn "
          "clusters vary here because a drawn union cluster may be absent from one split."]
    (RESULTS / "paired_diff.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
