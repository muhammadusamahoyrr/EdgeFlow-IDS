"""CIC-IoT2023: seed spread of macro-F1 under the random (stratified 70/30) split (review round 8).

The paper reports random-split macro-F1 for seed 0 only (decision tree 0.869, results/baseline_stratified).
Here seeds 0-4 are run in three ways:
  joint      : split seed = model seed = s (train_test_split random_state and DecisionTreeClassifier
               random_state both s);
  split only : split seed s, model seed 0;
  model only : split seed 0, model seed s.
Models: unconstrained decision tree (class_weight balanced) and the deployed edge tree (config.EDGE_TREE
with random_state replaced). Macro-F1 over all 8 classes (sklearn, zero_division=0). Seed 0 of every
variant must reproduce the seed-0 numbers (checked).

Usage: python src/analysis/random_seed_spread.py
Output: results/random_seed_spread.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from train_baseline import TRAIN_FRAC  # noqa: E402

SEEDS = range(5)
MODELS = {"decision tree": dict(class_weight="balanced"),
          "edge tree (deployed)": {k: v for k, v in EDGE_TREE.items() if k != "random_state"}}


def main():
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    classes = sorted(df.label.unique())
    splits = {}

    def split(s):
        if s not in splits:
            tr, te = train_test_split(df, train_size=TRAIN_FRAC, stratify=df["label"], random_state=s)
            feats = feature_columns(tr)
            splits[s] = (tr[feats].to_numpy(np.float32), tr.label.to_numpy(),
                         te[feats].to_numpy(np.float32), te.label.to_numpy())
        return splits[s]

    cache, rows = {}, []

    def score(name, ss, ms):
        if (name, ss, ms) not in cache:
            xtr, ytr, xte, yte = split(ss)
            m = DecisionTreeClassifier(**MODELS[name], random_state=ms).fit(xtr, ytr)
            cache[name, ss, ms] = f1_score(yte, m.predict(xte), labels=classes, average="macro", zero_division=0)
            print(name, ss, ms, round(cache[name, ss, ms], 4), flush=True)
        return cache[name, ss, ms]

    variants = {"joint (split = model seed)": lambda s: (s, s), "split seed only (model seed 0)": lambda s: (s, 0),
                "model seed only (split seed 0)": lambda s: (0, s)}
    for name in MODELS:
        for vname, f in variants.items():
            v = np.array([score(name, *f(s)) for s in SEEDS])
            rows.append({"model": name, "variant": vname,
                         **{f"seed {s}": round(float(x), 4) for s, x in zip(SEEDS, v)},
                         "mean": round(float(v.mean()), 4), "SD": round(float(v.std(ddof=1)), 4),
                         "min": round(float(v.min()), 4), "max": round(float(v.max()), 4),
                         "range": round(float(v.max() - v.min()), 4)})
    md = ["# CIC-IoT2023: random-split seed spread of macro-F1 (review round 8)", "",
          f"Stratified 70/30 split (sklearn train_test_split), macro-F1 over all {len(classes)} classes; seeds "
          f"{list(SEEDS)}. Edge tree = config.EDGE_TREE {EDGE_TREE} with random_state varied. "
          "Script: src/analysis/random_seed_spread.py. SD = sample SD over the 5 seeds.", "",
          pd.DataFrame(rows).to_markdown(index=False), "",
          "Seed 0 reproduces results/baseline_stratified/metrics.json (decision tree, edge tree) if the seed-0 "
          "column equals the macro-F1 reported there (checked below).", ""]
    import json
    met = json.loads((RESULTS / "baseline_stratified" / "metrics.json").read_text())["models"]
    for key, name in (("decision_tree", "decision tree"), ("decision_tree_edge", "edge tree (deployed)")):
        ref = met[key].get("macro_f1")
        md.append(f"- {name}: metrics.json macro_f1 = {ref}, seed 0 here = {cache[name, 0, 0]:.6f}")
    (RESULTS / "random_seed_spread.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
