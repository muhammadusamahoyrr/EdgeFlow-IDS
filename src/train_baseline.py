"""Baseline models on all features.

Splits (--split):
  temporal   (default) inside each pcap, flows are ordered by start time; the first 70% go to
             train and the last 30% to test, so no future flows leak into training.
  stratified random 70/30, stratified by label: the optimistic setting most papers report.
The feature list is decided on the training split only.

Reports macro-F1, per-class precision/recall, confusion matrix, model size (pickled bytes)
and single-flow inference latency (median of repeated predict calls, 1 thread).

Usage: python src/train_baseline.py [--split temporal|stratified]
Output: results/baseline_<split>/{metrics.json, report.md, confusion_<model>.csv}
"""
import argparse
import json
import pickle
import time

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns

TRAIN_FRAC = 0.7
SEED = 0
LATENCY_CALLS = 300
LATENCY_REPEATS = 5
BOOTSTRAP = 200
MIN_SUPPORT = 50


def temporal_split(df):
    df = df.sort_values(["source_file", "bidirectional_first_seen_ms"])
    rank = df.groupby("source_file").cumcount()
    size = df.groupby("source_file")["source_file"].transform("size")
    is_train = rank < (size * TRAIN_FRAC)
    return df[is_train], df[~is_train]


def stratified_split(df):
    train, test = train_test_split(df, train_size=TRAIN_FRAC, stratify=df["label"], random_state=SEED)
    return train, test


SPLITS = {"temporal": temporal_split, "stratified": stratified_split}


def models():
    return {
        "majority": DummyClassifier(strategy="most_frequent"),
        "decision_tree": DecisionTreeClassifier(class_weight="balanced", random_state=SEED),
        "decision_tree_edge": DecisionTreeClassifier(**EDGE_TREE),
        "random_forest": RandomForestClassifier(n_estimators=100, class_weight="balanced_subsample",
                                                n_jobs=-1, random_state=SEED),
        "hist_gboost": HistGradientBoostingClassifier(class_weight="balanced", random_state=SEED),
    }


def latency_stats(model, X):
    """Single-flow predict latency (median and IQR over LATENCY_REPEATS x LATENCY_CALLS calls; this
    is dominated by sklearn's per-call overhead) and batch latency per flow (1,000-row predict)."""
    if hasattr(model, "n_jobs"):
        model.set_params(n_jobs=1)
    rng = np.random.default_rng(SEED)
    times = []
    for _ in range(LATENCY_REPEATS):
        for r in X[rng.integers(0, len(X), LATENCY_CALLS)]:
            t0 = time.perf_counter()
            model.predict(r.reshape(1, -1))
            times.append((time.perf_counter() - t0) * 1000)
    batch = X[rng.integers(0, len(X), 1000)]
    bt = []
    for _ in range(LATENCY_REPEATS):
        t0 = time.perf_counter()
        model.predict(batch)
        bt.append((time.perf_counter() - t0) * 1000 / len(batch))
    q1, med, q3 = np.percentile(times, [25, 50, 75])
    return {"single_ms_median": float(med), "single_ms_iqr": [float(q1), float(q3)],
            "batch_ms_per_flow": float(np.median(bt))}


def single_flow_latency_ms(model, X):
    return latency_stats(model, X)["single_ms_median"]


def bootstrap_macro_f1(y, pred, classes):
    """95% bootstrap interval of macro-F1 over test flows (BOOTSTRAP resamples)."""
    # Same definition as f1_score(average="macro", zero_division=0, labels=classes), computed from
    # a confusion matrix per resample so it stays fast on ~250k test flows.
    k = len(classes)
    index = {c: i for i, c in enumerate(classes)}
    yi = np.array([index[v] for v in y])
    pi = np.array([index.get(v, k) for v in pred])
    rng = np.random.default_rng(SEED)
    n = len(yi)
    vals = []
    for _ in range(BOOTSTRAP):
        idx = rng.integers(0, n, n)
        cm = np.bincount(yi[idx] * (k + 1) + pi[idx], minlength=k * (k + 1)).reshape(k, k + 1)
        tp = np.diag(cm[:, :k]).astype(float)
        support = cm.sum(axis=1)
        predicted = cm[:, :k].sum(axis=0)
        denom = support + predicted
        f1 = np.divide(2 * tp, denom, out=np.zeros(k), where=denom > 0)
        vals.append(f1.mean())
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def main(split):
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    train, test = SPLITS[split](df)
    feats = feature_columns(train)
    X_tr, y_tr = train[feats].to_numpy(np.float32), train["label"].to_numpy()
    X_te, y_te = test[feats].to_numpy(np.float32), test["label"].to_numpy()
    classes = sorted(df["label"].unique())

    print(f"features: {len(feats)} | train {len(train):,} | test {len(test):,}")
    print("train classes:", pd.Series(y_tr).value_counts().to_dict())
    print("test classes: ", pd.Series(y_te).value_counts().to_dict())
    missing = set(classes) - set(y_te)
    if missing:
        print(f"WARNING: classes absent from test split: {missing}")

    out_dir = RESULTS / f"baseline_{split}"
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = {"features": feats, "n_train": len(train), "n_test": len(test),
               "train_classes": pd.Series(y_tr).value_counts().to_dict(),
               "test_classes": pd.Series(y_te).value_counts().to_dict(), "models": {}}

    for name, model in models().items():
        t0 = time.perf_counter()
        model.fit(X_tr, y_tr)
        fit_s = time.perf_counter() - t0
        pred = model.predict(X_te)
        rep = classification_report(y_te, pred, labels=classes, output_dict=True, zero_division=0)
        cm = pd.DataFrame(confusion_matrix(y_te, pred, labels=classes), index=classes, columns=classes)
        cm.to_csv(out_dir / f"confusion_{name}.csv")
        big = [c for c in classes if (y_te == c).sum() >= MIN_SUPPORT]
        is_benign = y_te == "Benign"
        lat = latency_stats(model, X_te)
        m = {
            "macro_f1": f1_score(y_te, pred, labels=classes, average="macro", zero_division=0),
            "macro_f1_ci95": bootstrap_macro_f1(y_te, pred, classes),
            f"macro_f1_classes_ge_{MIN_SUPPORT}": f1_score(y_te, pred, labels=big, average="macro",
                                                           zero_division=0),
            "benign_false_positive_rate": float((pred[is_benign] != "Benign").mean()),
            "attack_detection_rate": float((pred[~is_benign] != "Benign").mean()),
            "per_class": {c: {k: rep[c][k] for k in ("precision", "recall", "f1-score", "support")}
                          for c in classes},
            "fit_seconds": fit_s,
            "model_bytes": len(pickle.dumps(model)),
            "tree_nodes": int(model.tree_.node_count) if hasattr(model, "tree_") else None,
            **lat,
        }
        metrics["models"][name] = m
        print(f"\n[{name}] macro-F1 {m['macro_f1']:.4f} {np.round(m['macro_f1_ci95'], 4)} | "
              f"benign FPR {m['benign_false_positive_rate']:.4f} | fit {fit_s:.1f}s | "
              f"size {m['model_bytes']/1024:.0f} KB | single {lat['single_ms_median']:.3f} ms")
        print(cm.to_string())

    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    support = pd.Series(y_te).value_counts()
    lines = [f"# Baseline results (all features, {split} 70/30 split)", "",
             f"Features: {len(feats)} · train {len(train):,} · test {len(test):,}",
             f"Test support: " + ", ".join(f"{c} {support.get(c, 0):,}" for c in classes),
             f"Classes with < {MIN_SUPPORT} test flows make macro-F1 noisy; see the CI and the "
             f"macro-F1 over classes with >= {MIN_SUPPORT} test flows.", "",
             "| Model | Macro-F1 [95% CI] | Macro-F1 (>=50) | Benign FPR | Attack detection | "
             "Size (KB) | Nodes | Single-flow ms (median) | Batch ms/flow |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, m in metrics["models"].items():
        lo, hi = m["macro_f1_ci95"]
        lines.append(f"| {name} | {m['macro_f1']:.3f} [{lo:.3f}, {hi:.3f}] | "
                     f"{m[f'macro_f1_classes_ge_{MIN_SUPPORT}']:.3f} | "
                     f"{m['benign_false_positive_rate']:.4f} | {m['attack_detection_rate']:.4f} | "
                     f"{m['model_bytes']/1024:.0f} | {m['tree_nodes'] or '-'} | "
                     f"{m['single_ms_median']:.3f} | {m['batch_ms_per_flow']:.4f} |")
    lines += ["", "Per-class precision / recall / F1:", "",
              "| Model | " + " | ".join(classes) + " |", "|---|" + "---|" * len(classes)]
    for name, m in metrics["models"].items():
        cells = [f"{m['per_class'][c]['precision']:.2f} / {m['per_class'][c]['recall']:.2f} / "
                 f"{m['per_class'][c]['f1-score']:.2f}" for c in classes]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n")
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=sorted(SPLITS), default="temporal")
    main(ap.parse_args().split)
