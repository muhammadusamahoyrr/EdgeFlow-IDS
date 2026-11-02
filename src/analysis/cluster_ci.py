"""Confidence intervals that respect correlated flows (paper revision, reviewer item M2).

Flows of the same host pair in the same capture are not independent (e.g. DDoS-SYN: ~500k flows
from 6 sources), so resampling single flows gives intervals that are too narrow. Here the
bootstrap resamples whole clusters = (capture file, unordered host pair). Macro-F1 is computed
from summed per-cluster confusion matrices, which is exact and fast.

Usage: python src/analysis/cluster_ci.py
Output: results/cluster_ci.md (edge tree and decision tree, temporal and stratified splits)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

B = 1000
SEED = 0


def cluster_ids(source_file, src_ip, dst_ip):
    a = np.where(src_ip < dst_ip, src_ip, dst_ip)
    b = np.where(src_ip < dst_ip, dst_ip, src_ip)
    key = pd.Series(source_file).astype(str) + "|" + pd.Series(a).astype(str) + "|" + pd.Series(b).astype(str)
    return pd.factorize(key)[0]


def macro_from_cm(cm):
    k = cm.shape[-1] - 1
    tp = np.einsum("...ii->...i", cm[..., :k, :k]).astype(float)
    support = cm[..., :k, :].sum(axis=-1)
    predicted = cm[..., :k, :k].sum(axis=-2)
    denom = support + predicted
    f1 = np.divide(2 * tp, denom, out=np.zeros_like(tp), where=denom > 0)
    return f1.mean(axis=-1)


def cluster_bootstrap(y, pred, clusters, classes, b=B, seed=SEED):
    """95% interval of macro-F1 (labels=classes, zero_division=0) resampling whole clusters."""
    k = len(classes)
    idx = {c: i for i, c in enumerate(classes)}
    yi = np.array([idx[v] for v in y])
    pi = np.array([idx.get(v, k) for v in pred])
    n_cl = clusters.max() + 1
    cell = (clusters * k + yi) * (k + 1) + pi
    per_cluster = np.bincount(cell, minlength=n_cl * k * (k + 1)).reshape(n_cl, k, k + 1)
    rng = np.random.default_rng(seed)
    vals = np.empty(b)
    for i in range(b):
        w = np.bincount(rng.integers(0, n_cl, n_cl), minlength=n_cl)
        vals[i] = macro_from_cm(np.tensordot(w, per_cluster, axes=1)[None])[0]
    point = macro_from_cm(per_cluster.sum(axis=0)[None])[0]
    assert abs(point - f1_score(y, pred, labels=classes, average="macro", zero_division=0)) < 1e-9
    return point, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)), n_cl


def main():
    from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns
    from train_baseline import SPLITS, bootstrap_macro_f1

    df = pd.read_parquet(PROCESSED / "flows.parquet")
    classes = sorted(df.label.unique())
    rows = []
    for split, fn in SPLITS.items():
        train, test = fn(df)
        feats = feature_columns(train)
        for name, params in (("decision tree", dict(class_weight="balanced", random_state=0)),
                             ("edge tree", EDGE_TREE)):
            m = DecisionTreeClassifier(**params).fit(train[feats].to_numpy(np.float32), train.label)
            p = m.predict(test[feats].to_numpy(np.float32))
            y = test.label.to_numpy()
            cl = cluster_ids(test.source_file.to_numpy(), test.src_ip.to_numpy(), test.dst_ip.to_numpy())
            point, lo, hi, n_cl = cluster_bootstrap(y, p, cl, classes)
            flo, fhi = bootstrap_macro_f1(y, p, classes)
            rows.append({"split": split, "model": name, "macro-F1": round(point, 3),
                         "flow bootstrap 95% CI": f"[{flo:.3f}, {fhi:.3f}]",
                         "host-pair bootstrap 95% CI": f"[{lo:.3f}, {hi:.3f}]",
                         "host-pair clusters": f"{n_cl:,}"})
            print(rows[-1])
    md = ["# Flow-level versus host-pair (cluster) bootstrap intervals", "",
          f"{B} resamples of whole (capture, host pair) clusters; the flow bootstrap resamples single test flows (200 resamples, as in the baselines).", "",
          pd.DataFrame(rows).to_markdown(index=False)]
    (RESULTS / "cluster_ci.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
