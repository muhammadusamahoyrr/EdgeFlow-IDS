"""CIC-IoT2023: sensitivity of the random-minus-temporal macro-F1 difference (and of the marginal
macro-F1 intervals) to the bootstrap cluster unit (review round 8).

The paper's intervals resample (capture, unordered host pair) clusters (results/cluster_ci.md,
results/paired_diff.md). Here the same models, splits and bootstrap code are rerun with coarser
cluster units:

  host pair            : (capture, unordered {src_ip, dst_ip}) -- the paper's scheme; must reproduce
                         results/paired_diff.md and results/cluster_ci.md (checked in the output).
  attacker host        : a flow that involves one of its capture's confirmed attackers
                         (data/attackers.json) is assigned to that attacker:
                           - IP rule: src_ip or dst_ip is a listed attacker IP of the capture
                             (src_ip checked first; a flow between two attacker IPs goes to its source);
                           - MAC rule (ARP-spoofing capture): src_mac or dst_mac is the attacker MAC,
                             i.e. victim traffic relayed through the attacker -> that attacker.
                         Cluster key = (capture, attacker IP). All other flows (they involve no attacker:
                         benign traffic, also in attack captures) keep their benign host-pair cluster.
                         Justification: everything an attacker sends is one correlated unit (one tool
                         run, one device), whichever victim it hits; benign hosts stay at host-pair level
                         because no stronger grouping is documented for them. The flow's label is NOT
                         used to build the key (an attacker's benign-labelled flows, e.g. the brute-force
                         host's Chromecast traffic, join its cluster), so the clustering does not depend
                         on the outcome.
  attacker device      : as attacker host but keyed by the attacker IP across captures (all captures
                         share one lab subnet; an IP listed as attacker in several captures, e.g. .65,
                         .147, .178, becomes one cluster). Assumes IP identity = device identity across
                         captures, which the dataset does not document -> supplementary, coarser.
  capture              : the pcap (10 clusters). Every attack class except Web sits in exactly one
                         capture, so most resamples miss at least one class (F1 = 0 for it); reported
                         as a stress test with the share of resamples missing a class, not as a
                         calibrated 95% interval.

Models: unconstrained decision tree (class_weight balanced, random_state 0) and the deployed edge tree
(config.EDGE_TREE), splits of src/train_baseline.py (temporal; random = stratified 70/30 seed 0),
macro-F1 over all 8 classes. Paired difference: analysis/paired_diff.paired_bootstrap (union keying,
same draw for both splits). Marginal CIs: each split resamples its own clusters
(iot23/cluster_sensitivity.own_boot, same draws as analysis/cluster_ci.py). 1000 resamples, seed 0.

Usage: python src/analysis/cluster_sensitivity_cic.py
Output: results/cluster_sensitivity_cic.md
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from analysis.paired_diff import B, SEED, paired_bootstrap  # noqa: E402
from config import ATTACKERS_FILE, EDGE_TREE, PROCESSED, RESULTS, feature_columns  # noqa: E402
from iot23.cluster_sensitivity import own_boot  # noqa: E402
from train_baseline import SPLITS  # noqa: E402

ATT = json.loads(ATTACKERS_FILE.read_text())
SCHEMES = ("host pair", "attacker host", "attacker device", "capture")


def attacker_of(t):
    """Per flow: the capture's attacker IP the flow involves, or '' if none."""
    folder = t.source_file.astype(str).str.split("/").str[0].to_numpy()
    s, d = t.src_ip.astype(str).to_numpy(), t.dst_ip.astype(str).to_numpy()
    sm = t.src_mac.astype(str).str.lower().to_numpy()
    dm = t.dst_mac.astype(str).str.lower().to_numpy()
    out = np.full(len(t), "", dtype=object)
    for f in np.unique(folder):
        info = ATT.get(f)
        if not isinstance(info, dict):
            continue
        rows = folder == f
        ips = set(info.get("attackers", []))
        hit_s = rows & np.isin(s, list(ips))
        hit_d = rows & ~hit_s & np.isin(d, list(ips))
        out[hit_s] = s[hit_s]
        out[hit_d] = d[hit_d]
        macs = [m.lower() for m in info.get("attacker_macs", [])]
        if macs:
            assert len(ips) == 1, f
            via = rows & (out == "") & (np.isin(sm, macs) | np.isin(dm, macs))
            out[via] = next(iter(ips))
    return out


def keys(t, scheme):
    f = t.source_file.astype(str).to_numpy().astype(object)
    s, d = t.src_ip.astype(str).to_numpy(), t.dst_ip.astype(str).to_numpy()
    a, b = np.where(s < d, s, d), np.where(s < d, d, s)
    hp = f + "|" + a.astype(object) + "|" + b.astype(object)
    if scheme == "host pair":
        return hp
    if scheme == "capture":
        return f
    att = attacker_of(t)
    has = att != ""
    if scheme == "attacker host":
        return np.where(has, "att|" + f + "|" + att, hp)
    if scheme == "attacker device":
        return np.where(has, "att|" + att, hp)
    raise ValueError(scheme)


def union_ids(tests, scheme):
    ks = [keys(t, scheme) for t in tests]
    codes, uniq = pd.factorize(np.concatenate(ks))
    out, i = [], 0
    for k in ks:
        out.append(codes[i:i + len(k)])
        i += len(k)
    return out, len(uniq)


def paired_missing(a, b, classes, n_cl, b_res=B, seed=SEED):
    """Share of paired (union) resamples in which some class has no test flow in a split (same draws
    as paired_bootstrap)."""
    from analysis.paired_diff import per_cluster_cm
    k = len(classes)
    sup = []
    for y, p, c in (a, b):
        cm = per_cluster_cm(y, p, c, classes, n_cl).reshape(n_cl, k, k + 1).sum(-1)  # (n_cl, k) support
        sup.append(cm)
    rng = np.random.default_rng(seed)
    miss = np.zeros(2)
    for _ in range(b_res):
        w = np.bincount(rng.integers(0, n_cl, n_cl), minlength=n_cl).astype(np.float64)
        for j in range(2):
            miss[j] += bool(((w @ sup[j]) == 0).any())
    return miss / b_res


def fmt(ci):
    return f"[{ci[0]:.3f}, {ci[1]:.3f}]"


def main():
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    classes = sorted(df.label.unique())
    k = len(classes)
    sel_all = list(range(k))
    parts = {s: fn(df) for s, fn in SPLITS.items()}
    tests = [parts["temporal"][1], parts["stratified"][1]]
    preds = {}
    for name, params in (("decision tree", dict(class_weight="balanced", random_state=0)),
                         ("edge tree (deployed)", EDGE_TREE)):
        for split, (train, test) in parts.items():
            feats = feature_columns(train)
            m = DecisionTreeClassifier(**params).fit(train[feats].to_numpy(np.float32), train.label)
            preds[name, split] = (test.label.to_numpy(), m.predict(test[feats].to_numpy(np.float32)))

    # attacker assignment summary (test sets)
    asum = []
    for split, t in (("temporal", tests[0]), ("random", tests[1])):
        att = attacker_of(t)
        lab = t.label.to_numpy()
        asum.append({"split": split, "test flows": f"{len(t):,}",
                     "flows assigned to an attacker": f"{int((att != '').sum()):,}",
                     "attack-labelled flows assigned": f"{int(((att != '') & (lab != 'Benign')).sum()):,}"
                                                       f" / {int((lab != 'Benign').sum()):,}",
                     "benign-labelled flows assigned": f"{int(((att != '') & (lab == 'Benign')).sum()):,}"})
        assert ((att != "") | (lab == "Benign")).all(), "attack flow without attacker"

    marg, paired, counts = [], [], []
    for scheme in SCHEMES:
        (cl_t, cl_s), n_u = union_ids(tests, scheme)
        cls = {"temporal": cl_t, "stratified": cl_s}
        counts.append({"clusters": scheme, "temporal test": f"{len(np.unique(cl_t)):,}",
                       "random test": f"{len(np.unique(cl_s)):,}", "union": f"{n_u:,}"})
        for name in ("decision tree", "edge tree (deployed)"):
            for split in ("temporal", "stratified"):
                y, p = preds[name, split]
                pt, ci, n, miss = own_boot(y, p, cls[split], classes, [sel_all], sel_all)
                marg.append({"clusters": scheme, "model": name,
                             "split": "random" if split == "stratified" else split, "n clusters": f"{n:,}",
                             "macro-F1": round(pt[0], 3), "95% CI": fmt(ci[0]),
                             "resamples missing a class": round(miss, 3)})
                print(marg[-1], flush=True)
            a = (*preds[name, "temporal"], cl_t, n_u)
            b = (*preds[name, "stratified"], cl_s, n_u)
            r = paired_bootstrap(a, b, classes)
            mt, ms = paired_missing(preds[name, "temporal"][:2] + (cl_t,), preds[name, "stratified"][:2] + (cl_s,),
                                    classes, n_u)
            paired.append({"clusters": scheme, "model": name, "union clusters": f"{n_u:,}",
                           "temporal": round(r["A"], 3), "random": round(r["B"], 3),
                           "random - temporal": round(r["diff"], 3), "paired 95% CI": fmt(r["diff_ci"]),
                           "share diff <= 0": round(r["p_le0"], 3),
                           "temporal CI (union)": fmt(r["A_ci"]), "random CI (union)": fmt(r["B_ci"]),
                           "resamples missing a class (temporal / random)": f"{mt:.3f} / {ms:.3f}"})
            print(paired[-1], flush=True)

    ref_pd = {"decision tree": "[0.024, 0.278]", "edge tree (deployed)": "[0.025, 0.287]"}
    ref_m = {("decision tree", "temporal"): "[0.577, 0.823]", ("decision tree", "random"): "[0.735, 0.877]",
             ("edge tree (deployed)", "temporal"): "[0.568, 0.822]",
             ("edge tree (deployed)", "random"): "[0.733, 0.875]"}
    check = all(r["paired 95% CI"] == ref_pd[r["model"]] for r in paired if r["clusters"] == "host pair")
    check &= all(r["95% CI"] == ref_m[r["model"], r["split"]] for r in marg if r["clusters"] == "host pair")

    md = ["# CIC-IoT2023: cluster-unit sensitivity of the random-minus-temporal difference (review round 8)", "",
          f"Models: unconstrained decision tree and deployed edge tree {EDGE_TREE}; splits of "
          "src/train_baseline.py (temporal per capture; random = stratified 70/30, seed 0); macro-F1 over all "
          f"{k} classes ({', '.join(classes)}). {B} resamples, seed {SEED}, percentile intervals. Point "
          "estimates do not depend on the clustering. Script: src/analysis/cluster_sensitivity_cic.py.", "",
          "Cluster units:", "",
          "- **host pair**: (capture, unordered host pair), the paper's scheme (results/cluster_ci.md, "
          "results/paired_diff.md).",
          "- **attacker host**: a flow involving one of its capture's confirmed attackers (data/attackers.json; "
          "IP rule: src or dst IP is a listed attacker; MAC rule for ARP spoofing: src/dst MAC is the attacker "
          "MAC) belongs to the cluster (capture, attacker IP); every other flow keeps its host-pair cluster. The "
          "label is not used to build the key.",
          "- **attacker device**: as attacker host, but one cluster per attacker IP across captures (assumes the "
          "same IP is the same device in different captures; not documented by the dataset; supplementary).",
          "- **capture**: the pcap (10 clusters). All attack classes except Web (3 captures) sit in one capture "
          "each, so most resamples miss at least one class, whose F1 is then 0: a stress test, not a calibrated "
          "interval.", "",
          f"Host-pair rows reproduce results/paired_diff.md and results/cluster_ci.md: **{'yes' if check else 'NO'}**.", "",
          "## Attacker assignment (test sets)", "", pd.DataFrame(asum).to_markdown(index=False), "",
          "## Number of clusters", "", pd.DataFrame(counts).to_markdown(index=False), "",
          "## Paired bootstrap of random minus temporal (union clusters, same draw for both splits)", "",
          pd.DataFrame(paired).to_markdown(index=False), "",
          "## Marginal intervals (each split resamples its own clusters)", "",
          pd.DataFrame(marg).to_markdown(index=False), "",
          "'resamples missing a class' = share of resamples in which at least one of the 8 classes has no test "
          "flow in that split."]
    (RESULTS / "cluster_sensitivity_cic.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
