"""Effect of the two label errors found by the blind audit (final review M8, plan item D2).

C1 (missed attack, DoS-HTTP_Flood): the attacker .66 also floods hosts that are not in the victim
   list of data/attackers.json (.71, .141). A flow of .66 to a LAN host on port 80 is relabelled
   DoS-HTTP when the same client opens >= 20 connections to that server:80 within +-5 s (the flood
   criterion of the audit rater); the count per server is reported.
C2 (over-inclusive, Web): the Web rule has no victim list, so any LAN host on port 80 counts as a
   victim. Web labels are restricted to the victims named in the evidence notes of attackers.json
   (SqlInjection .4/.86/.217; XSS and CommandInjection .11/.13/.236).

Scores (edge tree config.EDGE_TREE, macro-F1 over 8 classes, temporal and random splits of
train_baseline.SPLITS):
  1. the deployed model file (decision_tree.pkl, trained on the old labels) on corrected test labels;
  2. the tree retrained on corrected labels, both splits; per-class F1 and the random-temporal gap.
The data/attackers.json and flows.parquet files are NOT changed.

Usage: python src/analysis/label_corrections.py
Output: results/final/label_corrections.md
"""
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from config import EDGE_TREE, ID_COLUMNS, PROCESSED, RESULTS  # noqa: E402
from train_baseline import SEED, TRAIN_FRAC  # noqa: E402

OUT = RESULTS / "final"
LAN = "192.168.137."
DOS_ATT, DOS_VIC = LAN + "66", {LAN + "71", LAN + "141"}
WEB_VIC = {"SqlInjection": {LAN + "4", LAN + "86", LAN + "217"},
           "XSS": {LAN + "11", LAN + "13", LAN + "236"},
           "CommandInjection": {LAN + "11", LAN + "13", LAN + "236"}}
CTX_MS = 5000


def split_index(df, split, labels):
    """Row labels of train/test in the same order as train_baseline.SPLITS produces them."""
    if split == "temporal":
        o = df[["source_file", "bidirectional_first_seen_ms"]].sort_values(["source_file", "bidirectional_first_seen_ms"])
        rank = o.groupby("source_file").cumcount()
        size = o.groupby("source_file")["source_file"].transform("size")
        is_tr = (rank < size * TRAIN_FRAC).to_numpy()
        return o.index[is_tr], o.index[~is_tr]
    tr, te = train_test_split(df.index, train_size=TRAIN_FRAC, stratify=labels, random_state=SEED)
    return tr, te


def correct(df):
    """Adds label_new (corrected) next to label; returns C1 / C2 row labels and the C1 table."""
    folder = df.source_file.str.split("/").str[0]
    df["label_new"] = df.label
    # C1
    d = df[(folder == "DoS-HTTP_Flood") & (df.src_ip == DOS_ATT) & (df.dst_port == 80)
           & df.dst_ip.str.startswith(LAN) & ~df.dst_ip.isin(DOS_VIC) & (df.label == "Benign")]
    rate = pd.Series(0, index=d.index)
    allf = df[(folder == "DoS-HTTP_Flood") & (df.src_ip == DOS_ATT) & (df.dst_port == 80)]
    for dst, g in allf.groupby("dst_ip"):
        t = np.sort(g.bidirectional_first_seen_ms.to_numpy())
        sel = d[d.dst_ip == dst]
        ts = sel.bidirectional_first_seen_ms.to_numpy()
        rate[sel.index] = np.searchsorted(t, ts + CTX_MS, "right") - np.searchsorted(t, ts - CTX_MS, "left")
    c1 = d.index[rate >= 20]
    df.loc[c1, "label_new"] = "DoS-HTTP"
    c1_tab = d.assign(flood=rate >= 20).groupby(["dst_ip", "flood"]).size().rename("flows").reset_index()
    # C2
    c2 = []
    for cap, vic in WEB_VIC.items():
        w = df[(folder == cap) & (df.label == "Web")]
        c2 += list(w.index[~w.src_ip.isin(vic) & ~w.dst_ip.isin(vic)])
    df.loc[c2, "label_new"] = "Benign"
    return c1, c2, c1_tab


def f1s(y, p, classes):
    per = f1_score(y, p, labels=classes, average=None, zero_division=0)
    return float(per.mean()), dict(zip(classes, per.round(3)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    df.index = pd.RangeIndex(len(df))
    c1, c2, c1_tab = correct(df)
    classes = sorted(df.label.unique())
    md = ["# Effect of the label errors found by the audit (final review M8)", "",
          "Script: src/analysis/label_corrections.py (corrections C1, C2 in its docstring). "
          "attackers.json and flows.parquet are unchanged; corrections are applied in memory.", "",
          f"- C1 DoS-HTTP flood to unlisted victims: {len(c1):,} flows relabelled Benign -> DoS-HTTP.",
          f"- C2 Web flows outside the evidence victims: {len(c2):,} flows relabelled Web -> Benign.", "",
          "C1 candidates (.66 -> unlisted LAN host :80, labelled Benign) by server and flood criterion:", "",
          c1_tab.to_markdown(index=False), ""]
    cand = [c for c in df.columns if c not in ID_COLUMNS and c not in ("label_new",)
            and pd.api.types.is_numeric_dtype(df[c])]
    X = df[cand].to_numpy(np.float32)
    y_old, y_new = df.label.to_numpy(), df.label_new.to_numpy()
    idx = {("old", s): split_index(df, s, y_old) for s in ("temporal", "stratified")}
    idx.update({("corrected", s): split_index(df, s, y_new) for s in ("temporal", "stratified")})
    for s in ("temporal", "stratified"):
        tr, te = idx["corrected", s]
        md.append(f"- {s} split: corrected labels in test {(y_old[te] != y_new[te]).sum():,}, "
                  f"in train {(y_old[tr] != y_new[tr]).sum():,}")
    md.append("")

    rows = []
    with open(RESULTS / "models" / "decision_tree.pkl", "rb") as fh:  # project's own model file
        bundle = pickle.load(fh)
    _, te = idx["corrected", "temporal"]
    p = bundle["model"].predict(df.loc[te, bundle["features"]].to_numpy(np.float32))
    for lab, y in (("old", y_old), ("corrected", y_new)):
        mf, pc = f1s(y[te], p, classes)
        rows.append({"model": "deployed file (old-label training)", "split": "temporal", "labels": lab,
                     "macro-F1": round(mf, 4), **pc})

    res = {}
    for (lab, s), (tr, te) in idx.items():
        y = y_old if lab == "old" else y_new
        cols = [i for i, c in enumerate(cand) if df[c].iloc[tr].nunique() > 1]  # = feature_columns(train)
        m = DecisionTreeClassifier(**EDGE_TREE).fit(X[np.asarray(tr)][:, cols], y[tr])
        mf, pc = f1s(y[te], m.predict(X[np.asarray(te)][:, cols]), classes)
        res[lab, s] = (mf, pc)
        rows.append({"model": "edge tree retrained", "split": s, "labels": lab, "macro-F1": round(mf, 4), **pc})
        print(lab, s, round(mf, 4), flush=True)
    t = pd.DataFrame(rows)
    md += ["## Macro-F1 and per-class F1", "", t.to_markdown(index=False), ""]
    for lab in ("old", "corrected"):
        (ms, ps), (mt, pt) = res[lab, "stratified"], res[lab, "temporal"]
        diff = {c: ps[c] - pt[c] for c in classes}
        tot = sum(diff.values())
        md += [f"## Random-minus-temporal gap, {lab} labels", "",
               f"Macro-F1 random {ms:.4f}, temporal {mt:.4f}, gap {ms - mt:+.4f}. Per class (share of summed difference):", "",
               pd.DataFrame({"class": classes, "random": [ps[c] for c in classes], "temporal": [pt[c] for c in classes],
                             "difference": [round(diff[c], 3) for c in classes],
                             "share": [f"{diff[c] / tot:.0%}" if tot else "-" for c in classes]}).to_markdown(index=False), ""]
    (OUT / "label_corrections.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
