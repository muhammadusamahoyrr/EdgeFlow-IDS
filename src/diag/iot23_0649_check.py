"""Unrounded check of the two IoT-23 temporal macro-F1 values that both round to 0.649 (Table III)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd
from sklearn.metrics import f1_score
from sklearn.tree import DecisionTreeClassifier
from config import EDGE_TREE, PROCESSED, feature_columns
from train_baseline import SPLITS
df = pd.read_parquet(PROCESSED / "iot23_flows.parquet")
classes = sorted(df.label.unique())
train, test = SPLITS["temporal"](df)
feats = feature_columns(train)
for target in ("file_label", "label"):
    p = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train[target]).predict(test[feats].to_numpy(np.float32))
    print(target, "vs file", f"{f1_score(test.file_label, p, labels=classes, average='macro', zero_division=0):.6f}",
          "vs Zeek", f"{f1_score(test.label, p, labels=classes, average='macro', zero_division=0):.6f}", flush=True)
