"""IoT-23: Benign FPR per capture for the file-label and Zeek-label models (reviewer request).

Same models and splits as src/iot23/file_label_baseline.py: edge tree (config.EDGE_TREE) trained
on file labels or on Zeek labels, temporal and stratified splits of src/train_baseline.py.
Benign FPR = share of test flows with Zeek label Benign that the model calls anything but Benign,
per capture; the macro average weights each capture with Benign test flows equally, the pooled
value weights flows (= the FPR in file_label_baseline.md). Also shows how many of the split's
Benign test flows each capture supplies.

Usage: python src/iot23/fpr_per_capture.py
Output: results/iot23/fpr_per_capture.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import SPLITS  # noqa: E402


def main():
    df = pd.read_parquet(PROCESSED / "iot23_flows.parquet")
    sections, summary = [], []
    for split, fn in SPLITS.items():
        train, test = fn(df)
        feats = feature_columns(train)
        X_tr, X_te = train[feats].to_numpy(np.float32), test[feats].to_numpy(np.float32)
        benign = test.label.to_numpy() == "Benign"
        cap = test.source_file.str.split("/").str[0].to_numpy()
        t = pd.DataFrame({"capture": cap[benign], "file label": test.file_label.to_numpy()[benign]})
        for trained_on, name in (("file_label", "file-label model"), ("label", "Zeek-label model")):
            p = DecisionTreeClassifier(**EDGE_TREE).fit(X_tr, train[trained_on].to_numpy()).predict(X_te)
            t[name] = p[benign] != "Benign"
        g = t.groupby(["capture", "file label"])
        tab = g.size().to_frame("Benign test flows")
        n_b = int(benign.sum())
        tab["share of split's Benign test flows"] = (tab["Benign test flows"] / n_b).round(4)
        for name in ("file-label model", "Zeek-label model"):
            tab[f"FP ({name})"] = g[name].sum().astype(int)
            tab[f"FPR ({name})"] = g[name].mean().round(4)
        tab = tab.reset_index()
        all_caps = sorted(df.source_file.str.split("/").str[0].unique())
        missing = [c for c in all_caps if c not in set(tab.capture)]
        sections += [f"## {split} split ({n_b:,} Benign test flows)", "", tab.to_markdown(index=False), ""]
        if missing:
            sections += [f"Captures without Benign test flows: {', '.join(missing)}.", ""]
        for name in ("file-label model", "Zeek-label model"):
            hp = tab[tab["file label"] == "Benign"]
            mal = tab[tab["file label"] != "Benign"]
            summary.append({"split": split, "model": name,
                            "pooled Benign FPR (flow-weighted)": round(float(t[name].mean()), 4),
                            "macro-avg FPR over captures": round(float(tab[f"FPR ({name})"].mean()), 4),
                            "captures": len(tab),
                            "macro-avg, honeypot captures": round(float(hp[f"FPR ({name})"].mean()), 4),
                            "macro-avg, malware captures": round(float(mal[f"FPR ({name})"].mean()), 4),
                            "min-max over captures": f"{tab[f'FPR ({name})'].min():.3f}-{tab[f'FPR ({name})'].max():.3f}"})
            print(summary[-1])
    md = ["# IoT-23: Benign FPR per capture (file-label vs Zeek-label edge tree)", "",
          f"Edge tree {EDGE_TREE}; both models scored against Zeek labels. FPR = Benign (Zeek) test flows "
          "predicted as any attack class. Macro average: unweighted mean over captures that have Benign "
          "test flows; pooled: over all Benign test flows (as in results/iot23/file_label_baseline.md).", "",
          "## Summary", "", pd.DataFrame(summary).to_markdown(index=False), "", *sections,
          "File label = the class labelling-by-capture gives every flow of the capture (honeypots Benign; "
          "src/iot23/extract_label.FAMILY_CLASS). The file-label model learns Benign only from the honeypot "
          "captures; the Benign background of every malware capture is labelled with that capture's attack "
          "class in training."]
    (RESULTS / "iot23" / "fpr_per_capture.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
