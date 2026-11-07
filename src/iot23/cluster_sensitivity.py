"""IoT-23 (and CIC-IoT2023) cluster sensitivity of the bootstrap intervals (review round 7).

Question: the host-pair bootstrap on IoT-23 resamples ~348k union clusters for ~454k test flows,
most of them single-flow clusters (scans, floods, one-off Benign connections). How does the choice
of cluster change the reported intervals?

Cluster definitions (all keyed by capture file, so no cluster spans two captures):
  host pair  : (capture, unordered {src_ip, dst_ip})   -- the scheme used in the paper so far
  capture    : (capture)                                -- 10 clusters; very coarse
  originator : (capture, src_ip), where src_ip is NFStream's flow source = the host that sent the
               flow's first packet (the connection originator). In the malware captures this is
               almost always the infected device (the attacker), for inbound flows the remote host.
  local host : (capture, local endpoint): src_ip if it is a private/link-local/unspecified address,
               else dst_ip if that is, else src_ip. Folds inbound flows (e.g. a C&C server talking to
               the infected device) into the device; in the benign captures it is the IoT device
               (or another LAN host).  Supplementary to the originator scheme.

Model and splits exactly as src/iot23/common_class_ci.py (edge tree config.EDGE_TREE trained on Zeek
labels; splits of src/train_baseline.py). For every scheme:
  marginal 95% CIs, each split resampling its own clusters (as common_class_ci.own_cluster_ci,
  1000 resamples, seed 0): common-class macro-F1 (Attack, Benign, C&C, PortScan), all-class
  macro-F1, C&C F1;
  paired 95% CI of stratified minus temporal (analysis/paired_diff.paired_bootstrap, union keying).
The host-pair rows must reproduce results/iot23/common_class_ci.md (checked in the output).
Also reported: share of resamples in which some common class has no test flow (coarse schemes).

Cluster-size distributions: per scheme, split and class (flows of the class per cluster that
contains it), and the same for CIC-IoT2023 host-pair clusters (data/processed/flows.parquet).

Usage: python src/iot23/cluster_sensitivity.py
Output: results/iot23/cluster_sensitivity.md
"""
import ipaddress
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.paired_diff import B, SEED, macro_sel, paired_bootstrap, per_cluster_cm  # noqa: E402
from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from iot23.common_class_ci import COMMON  # noqa: E402
from train_baseline import SPLITS  # noqa: E402


def _local(ip, cache={}):
    if ip not in cache:
        try:
            a = ipaddress.ip_address(ip)
            cache[ip] = a.is_private or a.is_link_local or a.is_unspecified
        except ValueError:
            cache[ip] = False
    return cache[ip]


def keys(t, scheme):
    f = t.source_file.astype(str).to_numpy().astype(object)
    s, d = t.src_ip.astype(str).to_numpy(), t.dst_ip.astype(str).to_numpy()
    if scheme == "host pair":
        a, b = np.where(s < d, s, d), np.where(s < d, d, s)
        return f + "|" + a.astype(object) + "|" + b.astype(object)
    if scheme == "capture":
        return f
    if scheme == "originator":
        return f + "|" + s.astype(object)
    if scheme == "local host":
        ls = np.array([_local(x) for x in s])
        ld = np.array([_local(x) for x in d])
        h = np.where(ls, s, np.where(ld, d, s))
        return f + "|" + h.astype(object)
    raise ValueError(scheme)


def union_ids(tests, scheme):
    ks = [keys(t, scheme) for t in tests]
    codes, uniq = pd.factorize(np.concatenate(ks))
    out, i = [], 0
    for k in ks:
        out.append(codes[i:i + len(k)])
        i += len(k)
    return out, len(uniq)


def own_boot(y, p, cl_union, classes, sels, common_idx, b=B, seed=SEED):
    """Same draws as common_class_ci.own_cluster_ci; returns CIs for several selections and the
    share of resamples in which some common class has zero test support."""
    cl = pd.factorize(cl_union)[0]
    n = cl.max() + 1
    k = len(classes)
    cm = per_cluster_cm(y, p, cl, classes, n)
    rng = np.random.default_rng(seed)
    v = np.empty((b, len(sels)))
    missing = 0
    for i in range(b):
        w = np.bincount(rng.integers(0, n, n), minlength=n).astype(np.float64)
        s = w @ cm
        for j, sel in enumerate(sels):
            v[i, j] = macro_sel(s, k, sel)
        sup = s.reshape(k, k + 1).sum(1)
        missing += bool((sup[common_idx] == 0).any())
    pt = [float(macro_sel(cm.sum(0), k, sel)) for sel in sels]
    ci = [(float(np.percentile(v[:, j], 2.5)), float(np.percentile(v[:, j], 97.5))) for j in range(len(sels))]
    return pt, ci, n, missing / b


def size_table(y, cl, classes, label_tag):
    """Per class: flows, clusters containing it, singleton clusters (cluster of exactly one flow in
    total), flows of the class per cluster (median, p90, max), share of class flows in the largest
    cluster and in singleton clusters."""
    t = pd.DataFrame({"y": y, "cl": cl})
    tot = t.groupby("cl").size()
    rows = []
    for c in classes + ["all classes"]:
        sub = t if c == "all classes" else t[t.y == c]
        if sub.empty:
            rows.append({**label_tag, "class": c, "flows": 0, "clusters with class": 0})
            continue
        g = sub.groupby("cl").size()
        single = tot.loc[g.index] == 1
        rows.append({**label_tag, "class": c, "flows": f"{len(sub):,}", "clusters with class": f"{len(g):,}",
                     "singleton clusters": f"{int(single.sum()):,}",
                     "share of class flows in singletons": round(float(g[single].sum() / len(sub)), 3),
                     "flows/cluster median": float(g.median()), "p90": float(g.quantile(0.9)),
                     "max": int(g.max()),
                     "share in largest cluster": round(float(g.max() / len(sub)), 3)})
    return rows


def fmt(ci):
    return f"[{ci[0]:.3f}, {ci[1]:.3f}]"


def main():
    df = pd.read_parquet(PROCESSED / "iot23_flows.parquet")
    classes = sorted(df.label.unique())
    k = len(classes)
    sel_c = [classes.index(c) for c in COMMON]
    sel_a = list(range(k))
    sel_cc = [classes.index("C&C")]
    parts = {s: fn(df) for s, fn in SPLITS.items()}
    preds = {}
    for split, (train, test) in parts.items():
        feats = feature_columns(train)
        m = DecisionTreeClassifier(**EDGE_TREE).fit(train[feats].to_numpy(np.float32), train.label)
        preds[split] = (test.label.to_numpy(), m.predict(test[feats].to_numpy(np.float32)))
    tests = [parts["temporal"][1], parts["stratified"][1]]

    marg, paired, sizes, counts = [], [], [], []
    for scheme in ("host pair", "capture", "originator", "local host"):
        (cl_t, cl_s), n_u = union_ids(tests, scheme)
        cls = {"temporal": cl_t, "stratified": cl_s}
        for split in ("temporal", "stratified"):
            y, p = preds[split]
            pt, ci, n, miss = own_boot(y, p, cls[split], classes, [sel_c, sel_a, sel_cc], sel_c)
            marg.append({"clusters": scheme, "split": split, "n clusters": f"{n:,}",
                         "common-class macro-F1": round(pt[0], 3), "common 95% CI": fmt(ci[0]),
                         "all-class macro-F1": round(pt[1], 3), "all-class 95% CI": fmt(ci[1]),
                         "C&C F1": round(pt[2], 3), "C&C 95% CI": fmt(ci[2]),
                         "resamples missing a common class": round(miss, 3)})
            print(marg[-1], flush=True)
            sizes += size_table(y, cls[split], classes, {"clusters": scheme, "split": split})
        for name, s in (("common classes", sel_c), ("all six classes", None), ("C&C F1", sel_cc)):
            r = paired_bootstrap((*preds["temporal"], cl_t, n_u), (*preds["stratified"], cl_s, n_u), classes, sel=s)
            paired.append({"clusters": scheme, "metric": name, "union clusters": f"{n_u:,}",
                           "temporal": round(r["A"], 3), "stratified": round(r["B"], 3),
                           "stratified - temporal": round(r["diff"], 3),
                           "paired 95% CI": fmt(r["diff_ci"]), "share diff <= 0": round(r["p_le0"], 3)})
            print(paired[-1], flush=True)
        counts.append({"clusters": scheme, "temporal test": f"{len(np.unique(cl_t)):,}",
                       "stratified test": f"{len(np.unique(cl_s)):,}", "union": f"{n_u:,}"})

    # sanity check against results/iot23/common_class_ci.md
    ref = {("temporal", "common 95% CI"): "[0.919, 0.983]", ("stratified", "common 95% CI"): "[0.904, 0.969]",
           ("temporal", "all-class 95% CI"): "[0.613, 0.655]", ("stratified", "all-class 95% CI"): "[0.638, 0.939]"}
    hp = {r["split"]: r for r in marg if r["clusters"] == "host pair"}
    check = all(hp[s][c] == v for (s, c), v in ref.items())
    check &= next(r for r in paired if r["clusters"] == "host pair" and r["metric"] == "common classes")["paired 95% CI"] == "[-0.039, -0.009]"

    # CIC-IoT2023 host-pair cluster sizes (no model needed)
    cic = pd.read_parquet(PROCESSED / "flows.parquet")
    cic_classes = sorted(cic.label.unique())
    ctests = {s: fn(cic)[1] for s, fn in SPLITS.items()}
    (ct, cs), cn = union_ids([ctests["temporal"], ctests["stratified"]], "host pair")
    cic_sizes = size_table(ctests["temporal"].label.to_numpy(), ct, cic_classes, {"split": "temporal"})
    cic_sizes += size_table(ctests["stratified"].label.to_numpy(), cs, cic_classes, {"split": "random"})
    print("CIC union clusters", cn, flush=True)

    md = ["# IoT-23: sensitivity of the bootstrap intervals to the cluster definition (review round 7)", "",
          f"Edge tree {EDGE_TREE}, Zeek labels, splits of src/train_baseline.py; {B} resamples, seed {SEED}, "
          "percentile intervals. Point estimates do not depend on the clustering.", "",
          "Cluster definitions (all within one capture):", "",
          "- **host pair**: (capture, unordered {src_ip, dst_ip}); the scheme used for the paper's intervals "
          "(results/iot23/common_class_ci.md, splits.md).",
          "- **capture**: the capture file; only 10 clusters, so this bootstrap is coarse: a resample of 10 "
          "captures with replacement omits each capture with probability 0.9^10 = 0.35, and Attack (scenario "
          "3-1 only), DDoS (34-1 only) and FileDownload (42-1 only) each sit in a single capture. Treat these "
          "intervals as a stress test, not as calibrated 95% intervals.",
          "- **originator**: (capture, src_ip), src_ip = NFStream flow source = sender of the flow's first "
          "packet. In the malware captures nearly all attack flows originate from the infected device (the "
          "attacker host); inbound flows (e.g. from a C&C server) form the remote host's cluster.",
          "- **local host**: (capture, local endpoint) with local endpoint = src_ip if private/link-local/"
          "unspecified, else dst_ip if that is, else src_ip. Folds inbound flows into the local (infected or "
          "benign IoT) device; for the benign captures it is the device or another LAN host.", "",
          f"Host-pair rows reproduce results/iot23/common_class_ci.md: **{'yes' if check else 'NO'}**.", "",
          "## Number of clusters", "", pd.DataFrame(counts).to_markdown(index=False), "",
          "## Marginal intervals (each split resamples its own clusters)", "",
          pd.DataFrame(marg).to_markdown(index=False), "",
          "'resamples missing a common class' = share of resamples in which at least one of Attack, Benign, "
          "C&C, PortScan has no test flow (its F1 is then 0).", "",
          "## Paired bootstrap of stratified minus temporal (union clusters, same draw for both splits)", "",
          pd.DataFrame(paired).to_markdown(index=False), "",
          "## Cluster-size distribution per class (IoT-23 test sets)", "",
          "Per class: clusters containing at least one flow of the class; singleton = cluster with exactly one "
          "test flow in total; flows/cluster = flows of that class per such cluster.", "",
          pd.DataFrame(sizes).to_markdown(index=False), "",
          "## CIC-IoT2023: host-pair cluster-size distribution per class (test sets)", "",
          f"Union of both test sets: {cn:,} host-pair clusters.", "",
          pd.DataFrame(cic_sizes).to_markdown(index=False)]
    (RESULTS / "iot23" / "cluster_sensitivity.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
