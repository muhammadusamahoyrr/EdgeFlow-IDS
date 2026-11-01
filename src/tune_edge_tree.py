"""Choose the edge decision tree's size limits on VALIDATION data (never on the test split).

Validation = last 20% of each pcap's training flows (same inner split as nsga_select.py); the
tree is fit on the remaining 80%. For each (max_depth, min_samples_leaf) we record validation
macro-F1, Benign false-positive rate and node count. Rule: among settings whose validation
macro-F1 is within 0.01 of the best and whose Benign FPR is within 0.5 percentage points of the
lowest, take the one with the fewest nodes.

Usage: python src/tune_edge_tree.py
Output: results/edge_tree_tuning.md, results/edge_tree.json (read by config.edge_tree())
"""
import json
import pickle

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.tree import DecisionTreeClassifier

from config import PROCESSED, RESULTS, feature_columns
from nsga_select import inner_split
from train_baseline import temporal_split

GRID_DEPTH = [None, 32, 24, 16]
GRID_LEAF = [1, 3, 10]


def main():
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    train, _ = temporal_split(df)
    feats = feature_columns(train)
    fit, val = inner_split(train)
    classes = sorted(train["label"].unique())
    X_fit, y_fit = fit[feats].to_numpy(np.float32), fit["label"].to_numpy()
    X_val, y_val = val[feats].to_numpy(np.float32), val["label"].to_numpy()
    rows = []
    for depth in GRID_DEPTH:
        for leaf in GRID_LEAF:
            params = dict(max_depth=depth, min_samples_leaf=leaf, class_weight="balanced",
                          random_state=0)
            m = DecisionTreeClassifier(**params).fit(X_fit, y_fit)
            p = m.predict(X_val)
            benign = y_val == "Benign"
            rows.append({"max_depth": depth, "min_samples_leaf": leaf,
                         "val_macro_f1": f1_score(y_val, p, labels=classes, average="macro",
                                                  zero_division=0),
                         "val_benign_fpr": float((p[benign] != "Benign").mean()),
                         "nodes": int(m.tree_.node_count),
                         "size_kb": len(pickle.dumps(m)) / 1024})
            print(rows[-1])
    t = pd.DataFrame(rows)
    ok = t[(t.val_macro_f1 >= t.val_macro_f1.max() - 0.01)
           & (t.val_benign_fpr <= t.val_benign_fpr.min() + 0.005)]
    if ok.empty:
        ok = t[t.val_macro_f1 >= t.val_macro_f1.max() - 0.01]
    best = ok.sort_values("nodes").iloc[0]
    params = {"max_depth": None if pd.isna(best.max_depth) else int(best.max_depth),
              "min_samples_leaf": int(best.min_samples_leaf),
              "class_weight": "balanced", "random_state": 0}
    (RESULTS / "edge_tree.json").write_text(json.dumps(params, indent=2))
    md = ["# Edge tree tuning (validation = last 20% of the training period)", "",
          t.round(4).to_markdown(index=False), "", f"Chosen: `{params}`"]
    (RESULTS / "edge_tree_tuning.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
