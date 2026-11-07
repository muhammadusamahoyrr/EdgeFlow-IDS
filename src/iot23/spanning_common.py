"""IoT-23: boundary-spanning test flows and the common-class macro-F1 (review round 6).

Question: does removing boundary-spanning test flows (5-tuple, either direction, also present in
the same capture's training split; splits.py) change the common-class macro-F1 (Attack, Benign,
C&C, PortScan), and which classes drive the all-class drop of the stratified split (0.863 ->
0.809 in results/iot23/splits.md)?

Setup exactly as src/iot23/splits.py and common_class_ci.py: edge tree (config.EDGE_TREE) trained
on Zeek labels, splits of src/train_baseline.py. Common-class macro-F1 = sklearn f1_score with
labels=COMMON, average='macro' (predictions of other classes count as errors of the common
classes). Host-pair intervals: 1000 resamples of each split's own (capture, unordered host pair)
clusters, seed 0 (common_class_ci.own_cluster_ci), recomputed on the kept flows only.

Per class and split: test support before/after removal, F1/precision/recall before/after, and the
contribution of each class to the all-class macro-F1 change (delta F1 / number of classes).
A class that loses all its test flows is flagged.

Usage: python src/iot23/spanning_common.py
Output: results/iot23/spanning_common.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score, precision_recall_fscore_support  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.cluster_ci import cluster_ids  # noqa: E402
from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from iot23.common_class_ci import COMMON, own_cluster_ci  # noqa: E402
from iot23.splits import spanning  # noqa: E402
from train_baseline import SPLITS  # noqa: E402


def main():
    df = pd.read_parquet(PROCESSED / "iot23_flows.parquet")
    classes = sorted(df.label.unique())
    k = len(classes)
    sel = [classes.index(c) for c in COMMON]
    summary, per_class = [], []
    for split, fn in SPLITS.items():
        train, test = fn(df)
        feats = feature_columns(train)
        m = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train.label)
        p = m.predict(test[feats].to_numpy(np.float32))
        y = test.label.to_numpy()
        cl = cluster_ids(test.source_file.to_numpy(), test.src_ip.to_numpy(), test.dst_ip.to_numpy())
        sp = spanning(train, test)
        keep = ~sp
        row = {"split": split, "test flows": f"{len(y):,}", "spanning": f"{int(sp.sum()):,}",
               "kept": f"{int(keep.sum()):,}"}
        for tag, mask in (("all", np.ones(len(y), bool)), ("without spanning", keep)):
            cf1 = f1_score(y[mask], p[mask], labels=COMMON, average="macro", zero_division=0)
            af1 = f1_score(y[mask], p[mask], labels=classes, average="macro", zero_division=0)
            lo, hi, n = own_cluster_ci(y[mask], p[mask], cl[mask], classes, sel)
            row[f"common-class macro-F1, {tag}"] = round(cf1, 4)
            row[f"host-pair 95% CI, {tag}"] = f"[{lo:.3f}, {hi:.3f}]"
            row[f"all-class macro-F1, {tag}"] = round(af1, 4)
        row["common-class change"] = round(row["common-class macro-F1, without spanning"]
                                           - row["common-class macro-F1, all"], 4)
        row["all-class change"] = round(row["all-class macro-F1, without spanning"]
                                        - row["all-class macro-F1, all"], 4)
        summary.append(row)
        print(row)
        pa, ra, fa, _ = precision_recall_fscore_support(y, p, labels=classes, zero_division=0)
        pk, rk, fk, _ = precision_recall_fscore_support(y[keep], p[keep], labels=classes, zero_division=0)
        for i, c in enumerate(classes):
            n_all, n_keep = int((y == c).sum()), int(((y == c) & keep).sum())
            flag = ""
            if n_all > 0 and n_keep == 0:
                flag = "LOSES ALL TEST FLOWS"
            elif n_all == 0:
                flag = "no test flows in this split"
            per_class.append({"split": split, "class": c, "common": c in COMMON,
                              "test support": n_all, "support after removal": n_keep,
                              "spanning removed": n_all - n_keep,
                              "flows predicted as class (all)": int((p == c).sum()),
                              "predicted as class (kept)": int((p[keep] == c).sum()),
                              "F1 all": round(fa[i], 3), "F1 without": round(fk[i], 3),
                              "precision all": round(pa[i], 3), "precision without": round(pk[i], 3),
                              "recall all": round(ra[i], 3), "recall without": round(rk[i], 3),
                              "contribution to all-class change": round((fk[i] - fa[i]) / k, 4),
                              "flag": flag})
    pc = pd.DataFrame(per_class)
    md = ["# IoT-23: boundary-spanning test flows and common-class macro-F1", "",
          f"Edge tree {EDGE_TREE}, trained on Zeek labels; splits of src/train_baseline.py. Spanning = test "
          "flow whose 5-tuple (either direction) also occurs in the same capture's training split "
          f"(src/iot23/splits.py). Common classes: {', '.join(COMMON)}. Host-pair 95% CI: 1000 resamples "
          "of the split's own (capture, unordered host pair) clusters, seed 0, on the flows kept.", "",
          "## Macro-F1 with and without spanning test flows", "",
          pd.DataFrame(summary).set_index("split").T.to_markdown(), "",
          "## Per class (all six classes; contribution = change of class F1 / 6)", "",
          pc.to_markdown(index=False), "",
          "Classes flagged LOSES ALL TEST FLOWS: "
          + (", ".join(f"{r['class']} ({r['split']})" for _, r in pc[pc.flag == "LOSES ALL TEST FLOWS"].iterrows())
             or "none") + ".", ""]
    for split in SPLITS:
        s = pc[pc.split == split]
        top = s.reindex(s["contribution to all-class change"].abs().sort_values(ascending=False).index)
        md.append(f"{split}: all-class change by class: "
                  + ", ".join(f"{r['class']} {r['contribution to all-class change']:+.4f}" for _, r in top.iterrows())
                  + ".")
    (RESULTS / "iot23" / "spanning_common.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
