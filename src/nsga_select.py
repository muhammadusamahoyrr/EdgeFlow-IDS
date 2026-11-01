"""NSGA-II feature selection for the edge model (pymoo).

Model: the size-limited decision tree (config.EDGE_TREE) used by the gateway.
Objectives (all minimised), measured on a validation split carved from the TRAIN period only
(the last 20% of each pcap's training flows, by time), so the test period is never touched:
  1. 1 - macro-F1 (validation)
  2. number of selected features (model inputs)
  3. decision-tree node count, on the class-capped fit sample (a proxy for model size)
Note: NFStream computes all statistics anyway, so fewer features reduces model inputs and
size, not flow-extraction cost.

Afterwards every Pareto-optimal subset is retrained on the full train split and scored on the
temporal test split with its real node count, size and latency. The edge subset is chosen on
VALIDATION F1 only (fewest features within 0.01 of the best), never on test results.

Usage: python src/nsga_select.py [--pop 40 --gen 30 --per-class 5000 --seed 0]
Output: results/nsga/{pareto.csv, summary.md, edge_pick.txt}
"""
import argparse
import pickle

import numpy as np
import pandas as pd
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.optimize import minimize
from sklearn.metrics import f1_score
from sklearn.tree import DecisionTreeClassifier

from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns
from train_baseline import bootstrap_macro_f1, latency_stats, temporal_split

VAL_FRAC = 0.2


def inner_split(train):
    """Last VAL_FRAC of each pcap's training flows (by start time) become validation."""
    train = train.sort_values(["source_file", "bidirectional_first_seen_ms"])
    rank = train.groupby("source_file").cumcount()
    size = train.groupby("source_file")["source_file"].transform("size")
    is_fit = rank < size * (1 - VAL_FRAC)
    return train[is_fit], train[~is_fit]


def cap_per_class(df, n, seed):
    parts = [g.sample(min(len(g), n), random_state=seed) for _, g in df.groupby("label")]
    return pd.concat(parts)


def tree():
    return DecisionTreeClassifier(**EDGE_TREE)


def macro(y, p, classes):
    return f1_score(y, p, labels=classes, average="macro", zero_division=0)


class FeatureSelection(ElementwiseProblem):
    def __init__(self, X_fit, y_fit, X_val, y_val, classes):
        super().__init__(n_var=X_fit.shape[1], n_obj=3, xl=0, xu=1, vtype=bool)
        self.data = (X_fit, y_fit, X_val, y_val)
        self.classes = classes

    def _evaluate(self, x, out, *args, **kwargs):
        cols = np.flatnonzero(x)
        if len(cols) == 0:
            out["F"] = [1.0, 0, 0]
            return
        X_fit, y_fit, X_val, y_val = self.data
        m = tree().fit(X_fit[:, cols], y_fit)
        out["F"] = [1 - macro(y_val, m.predict(X_val[:, cols]), self.classes), len(cols),
                    m.tree_.node_count]


def main(pop, gen, per_class, seed):
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    train, test = temporal_split(df)
    feats = feature_columns(train)
    fit, val = inner_split(train)
    fit = cap_per_class(fit, per_class, seed)
    classes = sorted(train["label"].unique())
    print(f"fit {len(fit):,} (capped {per_class}/class) | val {len(val):,} | {len(feats)} features")
    print("val support:", val["label"].value_counts().to_dict())

    X_val, y_val = val[feats].to_numpy(np.float32), val["label"].to_numpy()
    problem = FeatureSelection(fit[feats].to_numpy(np.float32), fit["label"].to_numpy(),
                               X_val, y_val, classes)
    algo = NSGA2(pop_size=pop, sampling=BinaryRandomSampling(), crossover=TwoPointCrossover(),
                 mutation=BitflipMutation(), eliminate_duplicates=True)
    res = minimize(problem, algo, ("n_gen", gen), seed=seed, verbose=True)

    X_tr, y_tr = train[feats].to_numpy(np.float32), train["label"].to_numpy()
    X_te, y_te = test[feats].to_numpy(np.float32), test["label"].to_numpy()
    F = np.atleast_2d(res.F)
    masks = [np.ones(len(feats), bool)] + [np.asarray(x, bool) for x in np.atleast_2d(res.X)]
    rows = []
    for i, mask in enumerate(masks):
        cols = np.flatnonzero(mask)
        if len(cols) == 0:
            continue
        m = tree().fit(X_tr[:, cols], y_tr)
        pred = m.predict(X_te[:, cols])
        lo, hi = bootstrap_macro_f1(y_te, pred, classes)
        lat = latency_stats(m, X_te[:, cols])
        rows.append({
            "subset": "all_features" if i == 0 else f"pareto_{i}",
            "n_features": len(cols),
            "val_macro_f1_capped_fit": None if i == 0 else round(1 - float(F[i - 1][0]), 4),
            "test_macro_f1": round(macro(y_te, pred, classes), 4),
            "test_ci95": f"[{lo:.3f}, {hi:.3f}]",
            "nodes": int(m.tree_.node_count),
            "size_kb": round(len(pickle.dumps(m)) / 1024, 1),
            "single_ms": round(lat["single_ms_median"], 4),
            "single_ms_iqr": "[{:.3f}, {:.3f}]".format(*lat["single_ms_iqr"]),
            "batch_ms_per_flow": round(lat["batch_ms_per_flow"], 5),
            "features": " ".join(feats[c] for c in cols),
        })
    table = pd.DataFrame(rows).drop_duplicates("features").sort_values("n_features")
    out = RESULTS / "nsga"
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "pareto.csv", index=False)

    pareto = table[table.subset != "all_features"]
    best_val = pareto.val_macro_f1_capped_fit.max()
    pick = (pareto[pareto.val_macro_f1_capped_fit >= best_val - 0.01]
            .sort_values(["n_features", "nodes"]).iloc[0])
    (out / "edge_pick.txt").write_text(pick.features + "\n")

    full = table[table.subset == "all_features"].iloc[0]
    md = ["# NSGA-II feature selection (size-limited decision tree)", "",
          f"Tree: `{EDGE_TREE}`. Population {pop}, generations {gen}, seed {seed}.",
          "Objectives: 1 - validation macro-F1, number of features, node count (on the capped fit "
          "sample). Validation = last 20% of the training period; the test split is only used "
          "for the columns marked test.", "",
          "| Subset | Features | Val macro-F1 | Test macro-F1 [95% CI] | Nodes | Size (KB) | "
          "Single-flow ms [IQR] | Batch ms/flow |",
          "|---|---|---|---|---|---|---|---|"]
    for r in table.itertuples():
        md.append(f"| {r.subset} | {r.n_features} | {r.val_macro_f1_capped_fit} | "
                  f"{r.test_macro_f1} {r.test_ci95} | {r.nodes} | {r.size_kb} | "
                  f"{r.single_ms} {r.single_ms_iqr} | {r.batch_ms_per_flow} |")
    md += ["", f"**Edge pick (chosen on validation):** {pick.subset}: {pick.n_features} features vs "
               f"{full.n_features}; test macro-F1 {pick.test_macro_f1} {pick.test_ci95} vs "
               f"{full.test_macro_f1} {full.test_ci95}; nodes {pick.nodes} vs {full.nodes}; "
               f"size {pick.size_kb} KB vs {full.size_kb} KB; batch {pick.batch_ms_per_flow} vs "
               f"{full.batch_ms_per_flow} ms/flow.",
           "", f"Features: `{pick.features}`"]
    (out / "summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", type=int, default=40)
    ap.add_argument("--gen", type=int, default=30)
    ap.add_argument("--per-class", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    main(a.pop, a.gen, a.per_class, a.seed)
