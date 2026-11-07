"""File-label FPR decomposition and leave-one-capture-out (final review, item M1 / A3).

Both datasets, deployed edge tree (config.EDGE_TREE), seed 0.
  CIC-IoT2023: file label = capture folder's class (config.FOLDER_TO_CLASS); evidence labels from
               extract_flows.py. Benign capture = Benign_Final (one pcap).
  IoT-23:      file label = iot23 file_label column (honeypots Benign); Zeek labels.

Part A (temporal and stratified splits of train_baseline.py, same as file_label_baseline.py):
  Benign FPR (Benign test flows under evidence/Zeek labels predicted as any attack) of the
  file-label model and the evidence/Zeek-label model, split into
    (i)  background: Benign flows inside attack/malware captures (trained under the attack name by
         the file-label model), and
    (ii) benign captures: flows of the CIC Benign capture / the three IoT-23 benign-device captures,
  plus per capture.
Part B (leave-one-capture-out, LOCO): for each held-out capture, train on ALL flows of every other
  capture, predict all flows of the held-out capture, report the FPR on its evidence/Zeek-Benign
  flows. The held-out capture's background was never seen under any label.
  CIC has a single Benign capture: holding it out leaves the file-label model without any Benign
  training flow (FPR = 1 by construction); reported as such.

Usage: python src/analysis/final_filelabel.py
Output: results/final/filelabel_decomposition.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from config import EDGE_TREE, FOLDER_TO_CLASS, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import SPLITS  # noqa: E402

OUT = RESULTS / "final"


def load(ds):
    if ds == "CIC-IoT2023":
        df = pd.read_parquet(PROCESSED / "flows.parquet")
        df["file_label"] = df.source_file.str.split("/").str[0].map(FOLDER_TO_CLASS)
    else:
        df = pd.read_parquet(PROCESSED / "iot23_flows.parquet")
    df["capture"] = df.source_file.astype(str).str.split("/").str[0]
    cap_file = df.groupby("capture").file_label.first()
    benign_caps = sorted(cap_file[cap_file == "Benign"].index)
    return df, benign_caps


def fit_predict(train, test, target, feats):
    m = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train[target].to_numpy())
    return m.predict(test[feats].to_numpy(np.float32)), list(m.classes_)


def rate(fp, n):
    return f"{fp / n:.4f} ({fp:,}/{n:,})" if n else "n/a"


def part_a(ds, df, benign_caps):
    summary, percap = [], []
    lab_name = "evidence" if ds == "CIC-IoT2023" else "Zeek"
    for split, fn in SPLITS.items():
        train, test = fn(df)
        feats = feature_columns(train)
        ben = test.label.to_numpy() == "Benign"
        cap = test.capture.to_numpy()
        in_bcap = np.isin(cap, benign_caps)
        for target, name in (("file_label", "file-label model"), ("label", f"{lab_name}-label model")):
            p, _ = fit_predict(train, test, target, feats)
            fp = ben & (p != "Benign")
            g_bg, g_bc = ben & ~in_bcap, ben & in_bcap
            summary.append({"split": split, "model": name,
                            "pooled Benign FPR": rate(int(fp.sum()), int(ben.sum())),
                            "(i) background in attack captures": rate(int((fp & g_bg).sum()), int(g_bg.sum())),
                            "(ii) benign capture(s)": rate(int((fp & g_bc).sum()), int(g_bc.sum())),
                            "share of FPs from (i)": round(float((fp & g_bg).sum() / max(fp.sum(), 1)), 4)})
            print(ds, summary[-1], flush=True)
            for c in sorted(np.unique(cap[ben])):
                mk = ben & (cap == c)
                vc = pd.Series(p[mk & fp]).value_counts()
                percap.append({"split": split, "model": name, "capture": c,
                               "group": "(ii) benign capture" if c in benign_caps else "(i) attack capture",
                               "Benign test flows": int(mk.sum()), "FP": int((mk & fp).sum()),
                               "FPR": round(float((mk & fp).sum() / mk.sum()), 4),
                               "top FP classes": ", ".join(f"{k} {v}" for k, v in vc.head(3).items())})
    return pd.DataFrame(summary), pd.DataFrame(percap)


def part_b(ds, df, benign_caps):
    rows = []
    lab_name = "evidence" if ds == "CIC-IoT2023" else "Zeek"
    feats_all = feature_columns(df)
    for held in sorted(df.capture.unique()):
        tr, te = df[df.capture != held], df[df.capture == held]
        feats = [f for f in feats_all if tr[f].nunique() > 1]
        ben = te.label.to_numpy() == "Benign"
        row = {"held-out capture": held,
               "group": "(ii) benign capture" if held in benign_caps else "(i) attack capture",
               "file label": te.file_label.iloc[0], "Benign flows in held-out capture": int(ben.sum())}
        for target, name in (("file_label", "file-label"), ("label", f"{lab_name}-label")):
            p, classes = fit_predict(tr, te, target, feats)
            fp = ben & (p != "Benign")
            note = "" if "Benign" in classes else " (no Benign class in training)"
            row[f"FPR {name} model"] = (f"{fp.sum() / ben.sum():.4f}{note}" if ben.sum() else "n/a")
            vc = pd.Series(p[fp]).value_counts()
            row[f"top FP classes ({name})"] = ", ".join(f"{k} {v}" for k, v in vc.head(2).items())
        rows.append(row)
        print(ds, row, flush=True)
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    md = ["# File-label FPR decomposition and leave-one-capture-out (final review M1)", "",
          f"Deployed edge tree {EDGE_TREE}, seed 0. Script: src/analysis/final_filelabel.py. FPR = share of "
          "Benign test flows (evidence labels on CIC-IoT2023, Zeek labels on IoT-23) predicted as any attack class. "
          "Format: rate (FP/n).", "",
          "(i) = Benign flows inside attack/malware captures (the file-label model is trained on this background "
          "under the capture's attack name); (ii) = flows of benign captures (CIC: Benign_Final; IoT-23: the three "
          "benign-device captures), the only Benign class the file-label model ever sees.", ""]
    for ds in ("CIC-IoT2023", "IoT-23"):
        df, bcaps = load(ds)
        s, pc = part_a(ds, df, bcaps)
        lo = part_b(ds, df, bcaps)
        md += [f"## {ds}", "", f"Benign captures: {', '.join(bcaps)}. Captures: {df.capture.nunique()}.", "",
               "### A. Temporal and stratified splits: decomposition", "", s.to_markdown(index=False), "",
               "### A. Per capture", "", pc.to_markdown(index=False), "",
               "### B. Leave-one-capture-out (train on all flows of the other captures)", "",
               lo.to_markdown(index=False), ""]
        if ds == "CIC-IoT2023":
            md += ["CIC-IoT2023 has one Benign capture. Holding it out removes every file-label Benign training flow, "
                   "so the file-label model cannot predict Benign at all (FPR 1 by construction); the evidence-label "
                   "model still learns Benign from the background of the attack captures.", ""]
    (OUT / "filelabel_decomposition.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
