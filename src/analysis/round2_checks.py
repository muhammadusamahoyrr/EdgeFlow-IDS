"""Second-round review checks (no new experiments).

1. Per-class recall with host-pair bootstrap intervals, temporal vs stratified split (edge tree):
   is the brute-force recall drop robust when whole host pairs are resampled?
2. Pair-level false blocks for the enforced live runs: a block is false if the blocked pair carries
   no attack flow in that window (the definition used for the k-curve), next to the trigger-flow
   definition used by eval_enforce.py.

Usage: python src/analysis/round2_checks.py
Output: results/round2_checks.md
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.cluster_ci import cluster_ids  # noqa: E402
from config import ATTACKERS_FILE, EDGE_TREE, FOLDER_TO_CLASS, PROCESSED, RESULTS, feature_columns  # noqa: E402
from eval_live import in_window  # noqa: E402
from extract_flows import label_flows  # noqa: E402
from train_baseline import SPLITS  # noqa: E402

B = 1000


def recall_ci(y, p, clusters, cls, seed=0):
    """Recall of one class with a host-pair bootstrap 95% interval; also the number of pairs."""
    mask = y == cls
    cl = clusters[mask]
    hit = (p[mask] == cls).astype(float)
    ids, inv = np.unique(cl, return_inverse=True)
    tp = np.bincount(inv, weights=hit)
    n = np.bincount(inv).astype(float)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        w = np.bincount(rng.integers(0, len(ids), len(ids)), minlength=len(ids))
        vals.append((w @ tp) / (w @ n))
    return hit.mean(), np.percentile(vals, 2.5), np.percentile(vals, 97.5), len(ids)


def per_class_section():
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    classes = sorted(df.label.unique())
    rows = []
    for split, fn in SPLITS.items():
        train, test = fn(df)
        feats = feature_columns(train)
        m = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train.label)
        p = m.predict(test[feats].to_numpy(np.float32))
        y = test.label.to_numpy()
        cl = cluster_ids(test.source_file.to_numpy(), test.src_ip.to_numpy(), test.dst_ip.to_numpy())
        for c in classes:
            r, lo, hi, n = recall_ci(y, p, cl, c)
            rows.append({"split": split, "class": c, "recall": round(r, 3),
                         "host-pair 95% CI": f"[{lo:.3f}, {hi:.3f}]", "host pairs": n,
                         "test flows": int((y == c).sum())})
    return pd.DataFrame(rows)


def false_block_section():
    attackers = json.loads(ATTACKERS_FILE.read_text())
    rows = []
    for tag in ("enforce_k1", "enforce_policy"):
        run = RESULTS / "live" / tag
        meta = json.loads((run / "windows.json").read_text())
        live = pd.read_csv(run / "flows.csv")
        blocked = trig_false = pair_false = 0
        for w in meta["windows"]:
            d = label_flows(in_window(live, w).copy(), FOLDER_TO_CLASS[w["folder"]], attackers.get(w["folder"], {}))
            d["pair"] = [tuple(sorted(p)) for p in zip(d.src_ip, d.dst_ip)]
            trig = d[d.blocked_now == 1]
            att_pairs = set(d[d.label != "Benign"].pair)
            blocked += len(trig)
            trig_false += int((trig.label == "Benign").sum())
            pair_false += sum(1 for p in trig.pair if p not in att_pairs)
        rows.append({"run": tag, "pairs blocked": blocked,
                     "false (trigger flow benign)": trig_false,
                     "false (pair has no attack flow in window)": pair_false})
    return pd.DataFrame(rows)


def main():
    pc = per_class_section()
    fb = false_block_section()
    md = ["# Second-round review checks", "",
          "## Per-class recall with host-pair bootstrap (edge tree)", "", pc.to_markdown(index=False), "",
          "## False blocks under two definitions (enforced live runs)", "", fb.to_markdown(index=False)]
    (RESULTS / "round2_checks.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
