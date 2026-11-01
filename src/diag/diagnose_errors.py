"""Where do misclassified flows come from? Retrains the decision tree (temporal split) and groups
errors of one true class predicted as another by file / IPs / port.
Usage: python diagnose_errors.py <true_label> <predicted_label>
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # EdgeFlow-IDS: import from src
import sys

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from config import PROCESSED, feature_columns
from train_baseline import SEED, temporal_split

true_lbl, pred_lbl = sys.argv[1], sys.argv[2]
df = pd.read_parquet(PROCESSED / "flows.parquet")
train, test = temporal_split(df)
feats = feature_columns(train)
model = DecisionTreeClassifier(class_weight="balanced", random_state=SEED)
model.fit(train[feats].to_numpy(np.float32), train["label"])
test = test.assign(pred=model.predict(test[feats].to_numpy(np.float32)))
err = test[(test.label == true_lbl) & (test.pred == pred_lbl)]
print(f"{len(err):,} test flows: true {true_lbl} -> predicted {pred_lbl}")
print(err.groupby("source_file").size().sort_values(ascending=False).to_string())
print(err.groupby(["source_file", "src_ip", "dst_ip", "dst_port", "protocol"]).size()
         .sort_values(ascending=False).head(12).to_string())
print("median packets", err.bidirectional_packets.median(), "| SYN", err.src2dst_syn_packets.median(),
      "| ACK", err.bidirectional_ack_packets.median())
