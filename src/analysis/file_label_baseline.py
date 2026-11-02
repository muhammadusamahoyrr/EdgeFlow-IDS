"""What do file-name labels cost? (paper revision, reviewer item M3)

Every flow in a capture gets the capture's class ("file labels"), as many published evaluations
do, versus the evidence-based labels of extract_flows.py. For both splits we train the edge tree
on file labels and score it twice:
  apparent: against file labels (what a file-label study would report)
  true:     against evidence labels (what the detector actually achieves)
and compare with the tree trained on evidence labels.

Usage: python src/analysis/file_label_baseline.py
Output: results/file_label_baseline.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from config import EDGE_TREE, FOLDER_TO_CLASS, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import SPLITS  # noqa: E402


def macro(y, p, classes):
    return f1_score(y, p, labels=classes, average="macro", zero_division=0)


def main():
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    df["file_label"] = df.source_file.str.split("/").str[0].map(FOLDER_TO_CLASS)
    classes = sorted(df.label.unique())
    rows = []
    for split, fn in SPLITS.items():
        train, test = fn(df)
        feats = feature_columns(train)
        X_tr, X_te = train[feats].to_numpy(np.float32), test[feats].to_numpy(np.float32)
        y_ev, y_file = test.label.to_numpy(), test.file_label.to_numpy()
        benign = y_ev == "Benign"
        for trained_on in ("file_label", "label"):
            m = DecisionTreeClassifier(**EDGE_TREE).fit(X_tr, train[trained_on].to_numpy())
            p = m.predict(X_te)
            rows.append({
                "split": split,
                "trained on": "file labels" if trained_on == "file_label" else "evidence labels",
                "apparent macro-F1 (file labels)": round(macro(y_file, p, classes), 3),
                "true macro-F1 (evidence labels)": round(macro(y_ev, p, classes), 3),
                "true Benign FPR": round(float((p[benign] != "Benign").mean()), 3),
                "background flows called attack": f"{int((p[benign] != 'Benign').sum()):,} / {int(benign.sum()):,}",
            })
            print(rows[-1])
    t = pd.DataFrame(rows)
    share = (df.label != df.file_label).mean()
    md = ["# File-name labels versus evidence-based labels (edge tree)", "",
          f"Flows whose file label differs from the evidence label: {share:.1%} of {len(df):,}.", "",
          t.to_markdown(index=False), "",
          "apparent = scored against file labels, as a file-label study would report;",
          "true = scored against the evidence labels."]
    (RESULTS / "file_label_baseline.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
