"""CIC-IoT2023 split-gap decomposition (final review, item M2 / A4).

Trees: the baseline decision tree of Table perclass (class_weight balanced, random_state 0) and the
deployed edge tree (config.EDGE_TREE; the gateway loads results/models/decision_tree.pkl, which is
this tree trained on the temporal training split with all features). Splits: train_baseline.SPLITS
(temporal; random = stratified 70/30 seed 0).

  1. Per-class F1 random, temporal, difference; each class's share of the summed difference.
  2. Macro-F1 without BruteForce and its paired host-pair bootstrap (analysis/paired_diff).
  3. Macro-F1 over classes with >= MIN_PAIRS host pairs in BOTH test sets, with paired bootstrap.
  4. BruteForce per target in the temporal test set (and training set), for the retrained trees and
     the saved model files results/models/decision_tree.pkl and dt_nsga.pkl.

Usage: python src/analysis/final_gap.py
Output: results/final/gap_decomposition.md
"""
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.paired_diff import B, SEED, paired_bootstrap, union_cluster_ids  # noqa: E402
from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import SPLITS  # noqa: E402

OUT = RESULTS / "final"
MIN_PAIRS = 5
TREES = {"decision tree (Table perclass)": dict(class_weight="balanced", random_state=0),
         "deployed edge tree": EDGE_TREE}


def pairs_of(t):
    s, d = t.src_ip.astype(str).to_numpy(), t.dst_ip.astype(str).to_numpy()
    a, b = np.where(s < d, s, d), np.where(s < d, d, s)
    return pd.Series(t.source_file.astype(str).to_numpy().astype(object) + "|" + a.astype(object) + "|"
                     + b.astype(object), index=t.index)


def target_of(t):
    """BruteForce flows: the victim endpoint (ip:port) of the attacker .65."""
    att = "192.168.137.65"
    vic = np.where(t.src_ip.to_numpy() == att, t.dst_ip.to_numpy(), t.src_ip.to_numpy())
    port = np.where(t.src_ip.to_numpy() == att, t.dst_port.to_numpy(), t.src_port.to_numpy())
    return pd.Series([f"{v.split('.')[-1] if isinstance(v, str) else v}:{int(p)}" for v, p in zip(vic, port)],
                     index=t.index).map(lambda x: "." + x)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    classes = sorted(df.label.unique())
    k = len(classes)
    parts = {s: fn(df) for s, fn in SPLITS.items()}
    (cl_t, cl_s), n_cl = union_cluster_ids([parts["temporal"][1], parts["stratified"][1]])
    preds = {}
    for name, params in TREES.items():
        for split, (train, test) in parts.items():
            feats = feature_columns(train)
            m = DecisionTreeClassifier(**params).fit(train[feats].to_numpy(np.float32), train.label)
            preds[name, split] = (test.label.to_numpy(), m.predict(test[feats].to_numpy(np.float32)))
            print(name, split, "done", flush=True)

    # host pairs per class per test set
    npairs = {}
    for split, (_, test) in parts.items():
        hp = pairs_of(test)
        npairs[split] = test.assign(hp=hp).groupby("label").hp.nunique().reindex(classes).fillna(0).astype(int)
    sel_pairs = [i for i, c in enumerate(classes) if npairs["temporal"][c] >= MIN_PAIRS and npairs["stratified"][c] >= MIN_PAIRS]
    sel_nobf = [i for i, c in enumerate(classes) if c != "BruteForce"]

    md = ["# CIC-IoT2023: decomposition of the random-minus-temporal gap (final review M2)", "",
          f"Script: src/analysis/final_gap.py. Splits of src/train_baseline.py; paired host-pair bootstrap of "
          f"src/analysis/paired_diff.py ({B} resamples, seed {SEED}, union clusters {n_cl:,}). "
          f"Classes: {', '.join(classes)}.", ""]
    for name in TREES:
        yt, pt = preds[name, "temporal"]
        ys, ps = preds[name, "stratified"]
        ft = f1_score(yt, pt, labels=classes, average=None, zero_division=0)
        fs = f1_score(ys, ps, labels=classes, average=None, zero_division=0)
        diff = fs - ft
        tab = pd.DataFrame({"class": classes, "temporal test flows": [int((yt == c).sum()) for c in classes],
                            "host pairs temporal": npairs["temporal"].to_numpy(),
                            "host pairs random": npairs["stratified"].to_numpy(),
                            "F1 random": fs.round(3), "F1 temporal": ft.round(3), "random - temporal": diff.round(3),
                            "share of summed difference": (diff / diff.sum()).round(3)})
        a = (yt, pt, cl_t, n_cl)
        b = (ys, ps, cl_s, n_cl)
        res = []
        for label, sel in (("all 8 classes", None), ("without BruteForce (7)", sel_nobf),
                           (f">= {MIN_PAIRS} host pairs in both test sets ({len(sel_pairs)}: "
                            + ", ".join(classes[i] for i in sel_pairs) + ")", sel_pairs)):
            r = paired_bootstrap(a, b, classes, sel=sel)
            res.append({"classes": label, "temporal": round(r["A"], 3), "random": round(r["B"], 3),
                        "random - temporal": round(r["diff"], 3),
                        "paired 95% CI": f"[{r['diff_ci'][0]:.3f}, {r['diff_ci'][1]:.3f}]",
                        "share of resamples <= 0": round(r["p_le0"], 3)})
            print(name, res[-1], flush=True)
        md += [f"## {name}", "", tab.to_markdown(index=False), "",
               f"Summed per-class difference {diff.sum():.3f} (= {diff.sum() / k:.4f} macro-F1 points); "
               f"BruteForce contributes {diff[classes.index('BruteForce')]:.3f} "
               f"({diff[classes.index('BruteForce')] / diff.sum():.1%}).", "",
               "Paired host-pair bootstrap of random minus temporal:", "", pd.DataFrame(res).to_markdown(index=False), ""]

    # BruteForce per target
    tr, te = parts["temporal"]
    bf_te = te[te.label == "BruteForce"]
    bf_tr = tr[tr.label == "BruteForce"]
    tgt_te, tgt_tr = target_of(bf_te), target_of(bf_tr)
    models = {}
    for fname in ("decision_tree.pkl", "dt_nsga.pkl"):
        p = RESULTS / "models" / fname
        if p.exists():
            with open(p, "rb") as f:  # trusted: produced locally by train_edge_model.py
                bnd = pickle.load(f)
            models[f"{fname} ({len(bnd['features'])} features)"] = bnd["model"].predict(
                bf_te[bnd["features"]].to_numpy(np.float32))
            if fname == "decision_tree.pkl":
                full = bnd["model"].predict(te[bnd["features"]].to_numpy(np.float32))
                same = float((full == preds["deployed edge tree", "temporal"][1]).mean())
    mask_bf = (te.label == "BruteForce").to_numpy()
    for name in TREES:
        models[f"{name}, retrained"] = preds[name, "temporal"][1][mask_bf]
    rows = []
    for t in sorted(tgt_te.unique()):
        mk = (tgt_te == t).to_numpy()
        r = {"target": t, "test flows": int(mk.sum()),
             "test host pairs": int(pairs_of(bf_te)[mk].nunique()),
             "train flows": int((tgt_tr == t).sum()),
             "test period": f"{pd.to_datetime(bf_te.bidirectional_first_seen_ms[mk].min(), unit='ms'):%H:%M}-"
                            f"{pd.to_datetime(bf_te.bidirectional_first_seen_ms[mk].max(), unit='ms'):%H:%M} UTC"}
        for mname, p in models.items():
            r[f"{mname}: predicted BruteForce / any attack"] = f"{int((p[mk] == 'BruteForce').sum())} / {int((p[mk] != 'Benign').sum())}"
        rows.append(r)
    md += ["## BruteForce per target, temporal split", "",
           f"Attacker .65 (data/attackers.json). Training-set BruteForce targets: "
           + ", ".join(f"{t} {n}" for t, n in tgt_tr.value_counts().items()) + ".", "",
           pd.DataFrame(rows).to_markdown(index=False), "",
           "Deployed tree: src/gateway.py loads results/models/decision_tree.pkl by default and every live run's "
           "windows.json names it; dt_nsga.pkl is the NSGA-II 14-feature variant, not used live. "
           f"decision_tree.pkl predictions equal the retrained deployed edge tree on {same:.4%} of temporal test flows."]
    (OUT / "gap_decomposition.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
