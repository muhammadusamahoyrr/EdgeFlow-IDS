"""Train the gateway model on the temporal TRAIN split only and save it for live use.

The model is the decision tree with the validation-tuned limits (config.EDGE_TREE). Also stores,
per pcap, the train/test boundary (start time of the last training flow; live windows are cut
just after it) and the connection keys (5-tuples) of training flows that were still running
after the boundary. eval_live.py drops those connections from both the offline and the live side,
so no training traffic is scored in a live window. (Using the last training flow's END as the
boundary is not workable: long background connections last until the end of each capture.)

Usage: python src/train_edge_model.py [--features nsga]
  --features all   (default) all statistical features
  --features nsga  the NSGA-II edge subset from results/nsga/pareto.csv (run nsga_select.py first)
Output: results/models/decision_tree.pkl or results/models/dt_nsga.pkl
"""
import argparse
import pickle

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns
from train_baseline import temporal_split


def main(which):
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    train, _ = temporal_split(df)
    feats = feature_columns(train)
    name = "decision_tree.pkl"
    if which == "nsga":
        pick = (RESULTS / "nsga" / "edge_pick.txt").read_text().split()
        feats = [f for f in feats if f in pick]
        name = "dt_nsga.pkl"
    model = DecisionTreeClassifier(**EDGE_TREE)
    model.fit(train[feats].to_numpy(np.float32), train["label"].to_numpy())
    cutoff = train.groupby("source_file")["bidirectional_first_seen_ms"].max().astype(int).to_dict()
    running = train[train.bidirectional_last_seen_ms > train.source_file.map(cutoff)]
    continuing = {f: sorted({(r.src_ip, int(r.src_port), r.dst_ip, int(r.dst_port), int(r.protocol))
                             for r in g.itertuples()})
                  for f, g in running.groupby("source_file")}
    print("training connections still running after the boundary:",
          {f: len(v) for f, v in continuing.items()})
    out = RESULTS / "models"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / name, "wb") as f:
        pickle.dump({"model": model, "features": feats, "classes": list(model.classes_),
                     "train_cutoff_ms": cutoff, "continuing_connections": continuing,
                     "tree": EDGE_TREE}, f)
    print(f"saved {out / name}: {len(feats)} features, {model.tree_.node_count} nodes, "
          f"classes {list(model.classes_)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", choices=["all", "nsga"], default="all")
    main(ap.parse_args().features)
