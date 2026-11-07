"""Headline numbers under the labels corrected by the blind audit (final review round 11, P1).

The audit (label_audit.py) found two label errors; label_corrections.correct() applies them in
memory (C1: 2,269 flows .66 -> .174:80 Benign -> DoS-HTTP; C2: 2 Web flows -> Benign).
attackers.json and flows.parquet are NOT changed. This script recomputes, old vs corrected:

  1. Table II   background share of each attack capture; share of flows where file-name and
                evidence labels differ.
  2. Setup/IV   deployed tree (decision_tree.pkl) on the temporal test set: macro-F1 with
                host-pair CI, per-class n / pairs / F1 / recall, pooled Benign FPR and its
                decomposition (background in attack captures vs the Benign capture).
                All corrected flows lie in the temporal test period, so the deployed tree's
                training data are unchanged and only the scoring moves.
  3. Table III  file-label tree on the temporal split scored against evidence labels.
  4. Table III  leave-one-capture-out (LOCO) Benign FPR of both trees, per capture, with the
                Benign (background) count of each held-out capture.
  5. Response   blocking replay of persistent_counters.py at k = 1..20 (reset 60 s / persistent),
                MITM-ARP verdicts ignored, with the falsely blocked pairs listed for k >= 5.

Usage: python src/analysis/corrected_headline.py
Output: results/final/corrected_headline.md
"""
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score, recall_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.cluster_ci import cluster_bootstrap, cluster_ids  # noqa: E402
from analysis.label_corrections import correct, split_index  # noqa: E402
from analysis.persistent_counters import block_times  # noqa: E402
from config import EDGE_TREE, FOLDER_TO_CLASS, PROCESSED, RESULTS, feature_columns  # noqa: E402

OUT = RESULTS / "final"
LABS = ("label", "label_new")
NAME = {"label": "old", "label_new": "corrected"}


def pct(a, b):
    return f"{a / b:.4f} ({a:,}/{b:,})" if b else "n/a"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    df.index = pd.RangeIndex(len(df))
    c1, c2, _ = correct(df)
    df["capture"] = df.source_file.astype(str).str.split("/").str[0]
    df["file_label"] = df.capture.map(FOLDER_TO_CLASS)
    classes = sorted(df.label.unique())
    md = ["# Headline numbers under corrected labels (round 11, P1)", "",
          "Script: src/analysis/corrected_headline.py. Corrections C1 (2,269 flows) and C2 (2 flows) of "
          "label_corrections.py, applied in memory.", ""]

    # 1. background share
    rows = []
    for cap, g in df.groupby("capture"):
        if FOLDER_TO_CLASS.get(cap) == "Benign":
            continue
        rows.append({"capture": cap, "flows": len(g),
                     **{f"background {NAME[l]}": round(float((g[l] == "Benign").mean()), 4) for l in LABS}})
    md += ["## 1. Background share (Table II)", "", pd.DataFrame(rows).to_markdown(index=False), ""]
    for l in LABS:
        md.append(f"- file-name vs {NAME[l]} evidence labels differ: {pct(int((df.file_label != df[l]).sum()), len(df))}")
    md.append("")

    # 2. deployed tree, temporal split
    tr, te = split_index(df, "temporal", df.label.to_numpy())
    test = df.loc[te]
    with open(RESULTS / "models" / "decision_tree.pkl", "rb") as fh:  # project's own model file
        bundle = pickle.load(fh)
    p = bundle["model"].predict(test[bundle["features"]].to_numpy(np.float32))
    cl = cluster_ids(test.source_file.to_numpy(), test.src_ip.to_numpy(), test.dst_ip.to_numpy())
    in_bcap = (test.file_label == "Benign").to_numpy()
    summ, per = [], []
    for l in LABS:
        y = test[l].to_numpy()
        point, lo, hi, _ = cluster_bootstrap(y, p, cl, classes)
        ben = y == "Benign"
        fp = ben & (p != "Benign")
        summ.append({"labels": NAME[l], "macro-F1": round(point, 4), "host-pair CI": f"[{lo:.3f}, {hi:.3f}]",
                     "macro-F1 w/o MITM-ARP": round(float(np.mean([f for c, f in zip(classes, f1_score(
                         y, p, labels=classes, average=None, zero_division=0)) if c != "MITM-ARP"])), 4),
                     "pooled Benign FPR": pct(int(fp.sum()), int(ben.sum())),
                     "background FPR": pct(int((fp & ~in_bcap).sum()), int((ben & ~in_bcap).sum())),
                     "Benign-capture FPR": pct(int((fp & in_bcap).sum()), int((ben & in_bcap).sum()))})
        f1 = f1_score(y, p, labels=classes, average=None, zero_division=0)
        rc = recall_score(y, p, labels=classes, average=None, zero_division=0)
        for c, f, r in zip(classes, f1, rc):
            m = y == c
            per.append({"labels": NAME[l], "class": c, "n": int(m.sum()), "pairs": int(len(np.unique(cl[m]))),
                        "F1": round(float(f), 3), "recall": round(float(r), 3)})
        dos = (test.capture == "DoS-HTTP_Flood").to_numpy() & ben
        summ[-1]["DoS-HTTP capture background FPR"] = pct(int((dos & fp).sum()), int(dos.sum()))
        print(summ[-1], flush=True)
    md += ["## 2. Deployed tree, temporal test set (setup, Table IV)", "",
           pd.DataFrame(summ).to_markdown(index=False), "", pd.DataFrame(per).to_markdown(index=False), ""]

    # 3. file-label tree, temporal split, against evidence labels
    train = df.loc[tr]
    feats = feature_columns(train)
    m = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train.file_label.to_numpy())
    pf = m.predict(test[feats].to_numpy(np.float32))
    rows = []
    for l in LABS:
        y = test[l].to_numpy()
        ben = y == "Benign"
        fp = ben & (pf != "Benign")
        rows.append({"labels": NAME[l],
                     "macro-F1 vs evidence": round(float(f1_score(y, pf, labels=classes, average="macro", zero_division=0)), 4),
                     "pooled FPR": pct(int(fp.sum()), int(ben.sum())),
                     "background FPR": pct(int((fp & ~in_bcap).sum()), int((ben & ~in_bcap).sum())),
                     "Benign-capture FPR": pct(int((fp & in_bcap).sum()), int((ben & in_bcap).sum()))})
    del train
    md += ["## 3. File-label tree, temporal split, scored against evidence labels (Table III)", "",
           pd.DataFrame(rows).to_markdown(index=False), ""]

    # 4. LOCO
    feats_all = feature_columns(df)
    rows = []
    for held in sorted(df.capture.unique()):
        trm = (df.capture != held).to_numpy()
        fts = [f for f in feats_all if df.loc[trm, f].nunique() > 1]
        Xtr = df.loc[trm, fts].to_numpy(np.float32)
        Xte = df.loc[~trm, fts].to_numpy(np.float32)
        row = {"held-out capture": held}
        pfl = DecisionTreeClassifier(**EDGE_TREE).fit(Xtr, df.file_label.to_numpy()[trm]).predict(Xte)
        for l in LABS:
            pe = DecisionTreeClassifier(**EDGE_TREE).fit(Xtr, df[l].to_numpy()[trm]).predict(Xte)
            ben = df[l].to_numpy()[~trm] == "Benign"
            row[f"Benign flows ({NAME[l]})"] = int(ben.sum())
            row[f"FPR file-label tree ({NAME[l]})"] = round(float((ben & (pfl != "Benign")).sum() / ben.sum()), 4)
            row[f"FPR evidence tree ({NAME[l]})"] = round(float((ben & (pe != "Benign")).sum() / ben.sum()), 4)
            row[f"paired diff ({NAME[l]})"] = round(row[f"FPR file-label tree ({NAME[l]})"] - row[f"FPR evidence tree ({NAME[l]})"], 4)
        rows.append(row)
        print(row, flush=True)
        del Xtr, Xte
    md += ["## 4. Leave-one-capture-out Benign FPR (Table III); paired diff = file-label minus evidence tree", "",
           pd.DataFrame(rows).to_markdown(index=False), ""]

    # 5. blocking replay (persistent_counters.py logic), MITM-ARP verdicts ignored
    s, d = test.src_ip.astype(str).to_numpy(), test.dst_ip.astype(str).to_numpy()
    lo_, hi_ = np.where(s < d, s, d), np.where(s < d, d, s)
    pair = test.source_file.astype(str).to_numpy().astype(object) + "|" + lo_.astype(object) + "|" + hi_.astype(object)
    span = test.groupby("source_file").agg(a=("bidirectional_first_seen_ms", "min"), b=("bidirectional_last_seen_ms", "max"))
    exposure_h = float((span.b - span.a).sum()) / 3.6e6
    v = pd.DataFrame({"pair": pair, "t": test.bidirectional_last_seen_ms.astype(np.int64).to_numpy(),
                      "t0": test.source_file.map(span.a).astype(np.int64).to_numpy()})
    v = v[(p != "Benign") & (p != "MITM-ARP")].sort_values(["pair", "t"]).reset_index(drop=True)
    rows, lists = [], []
    for l in LABS:
        att_pairs = set(pair[test[l].to_numpy() != "Benign"])
        n_ben = len(set(pair)) - len(att_pairs)
        for hname, mode in (("reset 60 s", "reset"), ("persistent", "persistent")):
            for k in (1, 2, 3, 5, 10, 20):
                blocked = set(block_times(v, k, mode, 60).index)
                false = sorted(blocked - att_pairs)
                rows.append({"labels": NAME[l], "horizon": hname, "k": k,
                             "attacker pairs blocked": f"{len(att_pairs & blocked)}/{len(att_pairs)}",
                             "false blocks": len(false), "per hour": round(len(false) / exposure_h, 1),
                             "benign-only pairs": n_ben})
                if k >= 5:
                    lists.append(f"- {NAME[l]}, {hname}, k={k}: " + "; ".join(false))
    md += [f"## 5. Blocking replay, MITM-ARP verdicts ignored (exposure {exposure_h:.2f} h)", "",
           pd.DataFrame(rows).to_markdown(index=False), "", "Falsely blocked pairs:", ""] + lists + [""]
    (OUT / "corrected_headline.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
