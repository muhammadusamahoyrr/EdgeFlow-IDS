"""IoT-23: what do capture-level ("file") labels cost? Same protocol as
src/analysis/file_label_baseline.py.

file_label = the class every flow of a capture gets when labelling by capture: Benign for the
honeypot captures, otherwise the family's main malicious behaviour (extract_label.FAMILY_CLASS).
For both splits the edge tree (config.EDGE_TREE) is trained on file labels and scored twice:
  apparent: against file labels (what a file-label study would report)
  true:     against the Zeek labels (the dataset's own per-connection labels)
and compared with the tree trained on Zeek labels.

Usage: python src/iot23/file_label_baseline.py
Output: results/iot23/file_label_baseline.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import SPLITS  # noqa: E402


def macro(y, p, classes):
    return f1_score(y, p, labels=classes, average="macro", zero_division=0)


def main():
    df = pd.read_parquet(PROCESSED / "iot23_flows.parquet")
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
                "trained on": "file labels" if trained_on == "file_label" else "Zeek labels",
                "apparent macro-F1 (file labels)": round(macro(y_file, p, classes), 3),
                "true macro-F1 (Zeek labels)": round(macro(y_ev, p, classes), 3),
                "true Benign FPR": round(float((p[benign] != "Benign").mean()), 3),
                "background flows called attack": f"{int((p[benign] != 'Benign').sum()):,} / {int(benign.sum()):,}",
            })
            print(rows[-1])
    t = pd.DataFrame(rows)
    share = (df.label != df.file_label).mean()
    fam = df.groupby("family").file_label.first().to_frame("file label").reset_index()
    md = ["# IoT-23: capture-level (file) labels versus Zeek labels (edge tree)", "",
          f"Edge tree parameters: {EDGE_TREE}. Classes: {', '.join(classes)}.", "",
          f"Flows whose file label differs from the Zeek label: {share:.1%} of {len(df):,}.", "",
          t.to_markdown(index=False), "",
          "apparent = scored against file labels, as a file-label study would report;",
          "true = scored against the Zeek labels. Macro-F1 is over all Zeek classes in both cases.", "",
          "File label per malware family (the family's main malicious behaviour in IoT-23; honeypots Benign):", "",
          fam.to_markdown(index=False)]
    (RESULTS / "iot23" / "file_label_baseline.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
