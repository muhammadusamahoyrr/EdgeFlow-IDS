"""IoT-23: temporal versus stratified split for the edge tree, with flow-level and host-pair CIs.

Splits are those of src/train_baseline.py (temporal = per capture, time-ordered 70/30 by flow
start; stratified = random 70/30 stratified by label). The edge tree (config.EDGE_TREE) is trained
on Zeek labels. Intervals (95%):
  flow bootstrap:      macro-F1 via train_baseline.bootstrap_macro_f1 (200 resamples of test flows)
  host-pair bootstrap: macro-F1 via analysis/cluster_ci.cluster_bootstrap (1000 resamples of
                       (capture, unordered host pair) clusters)
  per-class F1 uses the same two resampling schemes (200 / 1000 resamples, seed 0).
Boundary-spanning share: test flows whose 5-tuple (either direction) also occurs in the training
split of the same capture (diag/check_split_overlap.keys), and macro-F1 without them.

Usage: python src/iot23/splits.py
Output: results/iot23/splits.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.cluster_ci import cluster_bootstrap, cluster_ids  # noqa: E402
from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from diag.check_split_overlap import keys  # noqa: E402
from train_baseline import SPLITS, bootstrap_macro_f1  # noqa: E402


def per_class_ci(y, pred, clusters, classes, b, seed=0):
    """95% interval of per-class F1, resampling whole clusters (one flow per cluster = flow bootstrap)."""
    k = len(classes)
    idx = {c: i for i, c in enumerate(classes)}
    yi = np.array([idx[v] for v in y])
    pi = np.array([idx.get(v, k) for v in pred])
    n_cl = clusters.max() + 1
    cell = (clusters * k + yi) * (k + 1) + pi
    per_cluster = np.bincount(cell, minlength=n_cl * k * (k + 1)).reshape(n_cl, k * (k + 1)).astype(float)
    rng = np.random.default_rng(seed)
    vals = np.empty((b, k))
    for i in range(b):
        w = np.bincount(rng.integers(0, n_cl, n_cl), minlength=n_cl).astype(float)
        cm = (w @ per_cluster).reshape(k, k + 1)
        tp = np.diag(cm[:, :k])
        denom = cm.sum(axis=1) + cm[:, :k].sum(axis=0)
        vals[i] = np.divide(2 * tp, denom, out=np.zeros(k), where=denom > 0)
    return np.percentile(vals, 2.5, axis=0), np.percentile(vals, 97.5, axis=0)


def spanning(train, test):
    tf, tr = keys(train)
    seen = set(tf) | set(tr)
    return np.array([k in seen for k in keys(test)[0]])


def main():
    df = pd.read_parquet(PROCESSED / "iot23_flows.parquet")
    classes = sorted(df.label.unique())
    summary, per_class, span_rows = [], [], []
    parts = {split: fn(df) for split, fn in SPLITS.items()}
    # classes with train and test flows in every split: macro-F1 over these compares like with like
    common = [c for c in classes if all((tr.label == c).any() and (te.label == c).any() for tr, te in parts.values())]
    for split, (train, test) in parts.items():
        feats = feature_columns(train)
        m = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train.label)
        p = m.predict(test[feats].to_numpy(np.float32))
        y = test.label.to_numpy()
        cl = cluster_ids(test.source_file.to_numpy(), test.src_ip.to_numpy(), test.dst_ip.to_numpy())
        point, lo, hi, n_cl = cluster_bootstrap(y, p, cl, classes)
        flo, fhi = bootstrap_macro_f1(y, p, classes)
        benign = y == "Benign"
        summary.append({"split": split, "train flows": f"{len(train):,}", "test flows": f"{len(test):,}",
                        "macro-F1": round(point, 3), "flow bootstrap 95% CI": f"[{flo:.3f}, {fhi:.3f}]",
                        "host-pair bootstrap 95% CI": f"[{lo:.3f}, {hi:.3f}]", "host-pair clusters": f"{n_cl:,}",
                        "Benign FPR": round(float((p[benign] != "Benign").mean()), 4),
                        "macro-F1, common classes": round(f1_score(y, p, labels=common, average="macro",
                                                                   zero_division=0), 3)})
        print(summary[-1])
        f1 = f1_score(y, p, labels=classes, average=None, zero_division=0)
        f_lo, f_hi = per_class_ci(y, p, np.arange(len(y)), classes, b=200)
        c_lo, c_hi = per_class_ci(y, p, cl, classes, b=1000)
        n_pairs = pd.Series(cl).groupby(y).nunique()
        for i, c in enumerate(classes):
            per_class.append({"split": split, "class": c, "test support": int((y == c).sum()),
                              "host pairs": int(n_pairs.get(c, 0)),
                              "train support": int((train.label == c).sum()), "F1": round(f1[i], 3),
                              "flow 95% CI": f"[{f_lo[i]:.3f}, {f_hi[i]:.3f}]",
                              "host-pair 95% CI": f"[{c_lo[i]:.3f}, {c_hi[i]:.3f}]"})
        sp = spanning(train, test)
        kept = [c for c in classes if ((y == c) & ~sp).any()]
        span_rows.append({"split": split, "spanning test flows": f"{int(sp.sum()):,} / {len(y):,}",
                          "share": round(sp.mean(), 3),
                          "macro-F1 all": round(point, 3),
                          "macro-F1 without spanning": round(f1_score(y[~sp], p[~sp], labels=classes,
                                                                      average="macro", zero_division=0), 3),
                          "same, over classes left": round(f1_score(y[~sp], p[~sp], labels=kept,
                                                                    average="macro", zero_division=0), 3),
                          "classes left": ", ".join(kept),
                          **{f"share {c}": round(sp[y == c].mean(), 3) if (y == c).any() else None
                             for c in classes}})
        print(span_rows[-1])
    md = ["# IoT-23: temporal versus stratified split (edge tree, Zeek labels)", "",
          f"Edge tree parameters: {EDGE_TREE}. Host-pair clusters = (capture, unordered host pair).", "",
          pd.DataFrame(summary).to_markdown(index=False), "",
          f"Common classes (train and test flows in both splits): {', '.join(common)}. Classes missing from "
          "a split's train or test set score F1 = 0 and pull macro-F1 down mechanically.", "",
          "Per-class F1 (flow bootstrap 200 resamples; host-pair bootstrap 1000 resamples):", "",
          pd.DataFrame(per_class).to_markdown(index=False), "",
          "Boundary-spanning test flows (5-tuple, either direction, also in the same capture's training split):", "",
          pd.DataFrame(span_rows).set_index("split").T.to_markdown()]
    (RESULTS / "iot23" / "splits.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
