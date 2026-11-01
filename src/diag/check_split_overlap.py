"""How much do connections spanning the temporal train/test boundary affect the test score?

A long connection is cut into several flows (idle 15 s / active 120 s); its first pieces can be in
the training split and later pieces in the test split. This marks every test flow whose 5-tuple
(either direction) also occurs in the training split of the same pcap, and compares the edge
tree's macro-F1 with and without those flows.

Usage: python src/diag/check_split_overlap.py
Output: results/split_overlap.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import bootstrap_macro_f1, temporal_split  # noqa: E402


def keys(df):
    fwd = list(zip(df.source_file, df.src_ip, df.src_port, df.dst_ip, df.dst_port, df.protocol))
    rev = list(zip(df.source_file, df.dst_ip, df.dst_port, df.src_ip, df.src_port, df.protocol))
    return fwd, rev


def main():
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    train, test = temporal_split(df)
    feats = feature_columns(train)
    tf, tr = keys(train)
    seen = set(tf) | set(tr)
    f, _ = keys(test)
    overlap = np.array([k in seen for k in f])
    classes = sorted(df["label"].unique())
    model = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train["label"])
    pred = model.predict(test[feats].to_numpy(np.float32))
    y = test["label"].to_numpy()

    def score(mask):
        lo, hi = bootstrap_macro_f1(y[mask], pred[mask], classes)
        return f1_score(y[mask], pred[mask], labels=classes, average="macro", zero_division=0), lo, hi

    all_f1 = score(np.ones(len(y), bool))
    clean_f1 = score(~overlap)
    # Classes that keep test flows after the removal (Mirai, for example, can vanish entirely,
    # which would otherwise count as F1 = 0 in the macro average).
    kept = [c for c in classes if ((y == c) & ~overlap).any()]

    def per_class(mask):
        return f1_score(y[mask], pred[mask], labels=classes, average=None, zero_division=0)

    pc_all, pc_clean = per_class(np.ones(len(y), bool)), per_class(~overlap)
    idx = [classes.index(c) for c in kept]
    same_classes = (float(np.mean(pc_all[idx])), float(np.mean(pc_clean[idx])))
    by_class = (pd.DataFrame({"label": y, "overlap": overlap})
                  .groupby("label").overlap.agg(["sum", "size"]))
    by_class["share"] = (by_class["sum"] / by_class["size"]).round(3)
    md = ["# Connections spanning the temporal train/test boundary", "",
          f"Test flows whose 5-tuple also occurs in the same pcap's training split: "
          f"{int(overlap.sum()):,} of {len(y):,} ({overlap.mean():.1%}).", "",
          "| Test set | Macro-F1 [95% CI] (edge tree) |", "|---|---|",
          f"| All test flows | {all_f1[0]:.3f} [{all_f1[1]:.3f}, {all_f1[2]:.3f}] |",
          f"| Without spanning connections | {clean_f1[0]:.3f} [{clean_f1[1]:.3f}, {clean_f1[2]:.3f}] |", "",
          f"Macro-F1 over the {len(kept)} classes that still have test flows after removal "
          f"({', '.join(kept)}): all {same_classes[0]:.3f} vs without spanning {same_classes[1]:.3f}.", "",
          "| Class | F1, all test flows | F1, without spanning connections |", "|---|---|---|",
          *[f"| {c} | {pc_all[i]:.3f} | {pc_clean[i]:.3f}{'' if c in kept else ' (no test flows left)'} |"
            for i, c in enumerate(classes)], "",
          "Spanning flows per class:", "", by_class.rename(columns={"sum": "spanning", "size": "test flows"}).to_markdown()]
    (RESULTS / "split_overlap.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
