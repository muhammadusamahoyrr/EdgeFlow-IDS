"""What the benchmark as distributed reports (paper revision, external review item 2).

The official CIC-IoT2023 per-pcap CSV files (data/raw/official_csv, see download_official_csv.py)
hold 39 packet-window features per row and no IPs, timestamps or label column: the only label is
the file name, so evidence-based relabelling is impossible on them. We train the same
decision-tree settings on the ten matching files with file labels and report:
  - stratified random 70/30 split (the usual benchmark protocol);
  - a row-order split per file (first 70% of rows for training), assuming rows follow capture
    order, which the files do not document.

Usage: python src/analysis/official_csv_baseline.py
Output: results/official_csv_baseline.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.metrics import f1_score, recall_score  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from config import EDGE_TREE, FOLDER_TO_CLASS, RAW, RESULTS  # noqa: E402


def load():
    parts = []
    for f in sorted((RAW / "official_csv").rglob("*.csv")):
        d = pd.read_csv(f)
        d["label"] = FOLDER_TO_CLASS[f.parent.name]
        d["source_file"] = f.parent.name
        d["row"] = np.arange(len(d))
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def row_order_split(df, frac=0.7):
    n = df.groupby("source_file").row.transform("size")
    is_train = df.row < n * frac
    return df[is_train], df[~is_train]


def main():
    df = load()
    feats = [c for c in df.columns if c not in ("label", "source_file", "row")]
    df[feats] = df[feats].replace([np.inf, -np.inf], np.nan).fillna(0)
    classes = sorted(df.label.unique())
    splits = {
        "stratified random 70/30": train_test_split(df, train_size=0.7, stratify=df.label, random_state=0),
        "row order per file 70/30": row_order_split(df),
    }
    models = {"decision tree": lambda: DecisionTreeClassifier(**EDGE_TREE),
              "random forest": lambda: RandomForestClassifier(n_estimators=100, class_weight="balanced_subsample",
                                                              n_jobs=-1, random_state=0)}
    rows = []
    for sname, (tr, te) in splits.items():
        for mname, make in models.items():
            m = make().fit(tr[feats].to_numpy(np.float32), tr.label)
            p = m.predict(te[feats].to_numpy(np.float32))
            rec = recall_score(te.label, p, labels=classes, average=None, zero_division=0)
            rows.append({"split": sname, "model": mname,
                         "macro-F1 (file labels)": round(f1_score(te.label, p, labels=classes, average="macro", zero_division=0), 3),
                         "accuracy": round(float((p == te.label.to_numpy()).mean()), 3),
                         **{f"recall {c}": round(float(r), 3) for c, r in zip(classes, rec)}})
            print(rows[-1])
    counts = df.groupby("source_file").size().rename("rows")
    md = ["# Official CIC-IoT2023 CSV features with file labels (benchmark as distributed)", "",
          f"{len(df):,} rows, {len(feats)} features, ten per-pcap CSV files matching this project's captures. "
          "No IPs, timestamps or label column: labels come from the file name only.", "",
          pd.DataFrame(rows).to_markdown(index=False), "", counts.to_frame().to_markdown()]
    (RESULTS / "official_csv_baseline.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
