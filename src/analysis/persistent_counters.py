"""Blocking with persistent verdict counters (final review M5, plan item D3).

The live harness clears per-pair verdict counts after every 60 s window. This makes k = 10
unreachable for low-rate attackers by construction, and it also keeps benign pairs from building
up false votes. Both effects come from the harness, not the detector. Here the gateway's
blocking rule (block a host pair once it has >= k non-Benign verdicts, optionally ignoring
MITM-ARP verdicts) is replayed on the whole CIC-IoT2023 temporal test period. Each capture is
replayed separately (the captures reuse one lab subnet), using several counter horizons:

  reset 60 s   counts cleared every 60 s from the capture's first test flow (the harness rule)
  sliding H    block when >= k verdicts fall within any H seconds (H = 60, 300, 900)
  persistent   counts never cleared within a capture's test period

Verdicts: the deployed model (results/models/decision_tree.pkl), applied to the offline NFStream
flows of the temporal test split. Verdict time = flow end (bidirectional_last_seen_ms). Live
verdicts come later by the export delay, which shifts every policy alike. Host pair =
(capture, unordered IP pair). A block is false if the pair has no attack-labelled flow in that
capture's test period. Exposure = sum over captures of the test period's span (first flow start
to last flow end).

Usage: python src/analysis/persistent_counters.py [--corrected]
Output: results/final/persistent_counters.md (with --corrected: the labels corrected by the blind
audit, label_corrections.correct(); output persistent_counters_corrected.md)
"""
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from config import PROCESSED, RESULTS  # noqa: E402
from train_baseline import temporal_split  # noqa: E402

OUT = RESULTS / "final"
KS = [1, 2, 3, 5, 10, 20]
HORIZONS = [("reset 60 s", "reset", 60), ("sliding 60 s", "sliding", 60),
            ("sliding 300 s", "sliding", 300), ("sliding 900 s", "sliding", 900),
            ("persistent", "persistent", None)]


def block_times(v, k, mode, h_s):
    """v: attack verdicts sorted by (pair, t) with columns pair, t (ms), t0 (capture start, ms).
    Returns Series pair -> block time (ms)."""
    if mode == "reset":
        b = ((v.t - v.t0) // (h_s * 1000)).astype(np.int64)
        n = v.groupby([v.pair, b]).cumcount() + 1
        hit = v[n == k]
    elif mode == "persistent":
        hit = v[v.groupby("pair").cumcount() + 1 == k]
    else:
        if k == 1:
            hit = v
        else:
            prev = v.groupby("pair").t.shift(k - 1)
            hit = v[(v.t - prev) <= h_s * 1000]
    return hit.groupby("pair").t.min()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    corrected = "--corrected" in sys.argv
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    if corrected:
        from analysis.label_corrections import correct
        df.index = pd.RangeIndex(len(df))
        correct(df)
        df["label"] = df.pop("label_new")
    _, test = temporal_split(df)
    with open(RESULTS / "models" / "decision_tree.pkl", "rb") as f:
        bundle = pickle.load(f)
    test = test.assign(pred=bundle["model"].predict(test[bundle["features"]].to_numpy(np.float32)))
    s, d = test.src_ip.astype(str).to_numpy(), test.dst_ip.astype(str).to_numpy()
    lo, hi = np.where(s < d, s, d), np.where(s < d, d, s)
    test["pair"] = test.source_file.astype(str).to_numpy().astype(object) + "|" + lo.astype(object) + "|" + hi.astype(object)
    test["t"] = test.bidirectional_last_seen_ms.astype(np.int64)
    span = test.groupby("source_file").agg(a=("bidirectional_first_seen_ms", "min"), b=("bidirectional_last_seen_ms", "max"))
    test["t0"] = test.source_file.map(span.a).astype(np.int64)
    exposure_h = float((span.b - span.a).sum()) / 3.6e6
    per_cap_min = ((span.b - span.a) / 60000).describe()

    att = test[test.label != "Benign"]
    pair_cls = att.groupby("pair").label.agg(lambda x: x.mode().iloc[0])
    att_pairs = set(pair_cls.index)
    first_seen = test.groupby("pair").bidirectional_first_seen_ms.min()
    n_benign_pairs = test.pair.nunique() - len(att_pairs)
    cls_tot = pair_cls.value_counts().sort_index()

    rows = []
    for ignore in (True, False):
        mask = test.pred != "Benign"
        if ignore:
            mask &= test.pred != "MITM-ARP"
        v = test.loc[mask, ["pair", "t", "t0"]].sort_values(["pair", "t"]).reset_index(drop=True)
        for hname, mode, h_s in HORIZONS:
            for k in KS:
                bt = block_times(v, k, mode, h_s)
                blocked = set(bt.index)
                false = blocked - att_pairs
                hit = att_pairs & blocked
                bt_att = att.pair.map(bt)
                after = float((att.bidirectional_first_seen_ms > bt_att).mean())
                ttb = ((bt[list(hit)] - first_seen[list(hit)]) / 1000) if hit else pd.Series(dtype=float)
                by_cls = {c: sum(1 for p in pair_cls[pair_cls == c].index if p in blocked) for c in cls_tot.index}
                rows.append({"MITM-ARP verdicts": "ignored" if ignore else "counted", "horizon": hname, "k": k,
                             "attacker pairs blocked": f"{len(hit)}/{len(att_pairs)}",
                             **{c: f"{by_cls[c]}/{cls_tot[c]}" for c in cls_tot.index},
                             "attack flows after block": round(after, 4),
                             "median time to block (s)": round(float(ttb.median()), 1) if len(ttb) else None,
                             "false blocks": len(false),
                             "false blocks per hour": round(len(false) / exposure_h, 1),
                             "false / benign pairs": round(len(false) / n_benign_pairs, 4)})
                print(hname, k, ignore, rows[-1]["attacker pairs blocked"], len(false), flush=True)

    t = pd.DataFrame(rows)
    md = ["# Blocking with persistent verdict counters (final review M5, plan D3)"
          + (", labels corrected by the blind audit" if corrected else ""), "",
          "Script: src/analysis/persistent_counters.py. Deployed model on the offline flows of the CIC-IoT2023 "
          "temporal test period, one capture at a time; verdict time = flow end. Simulation, not an enforced run.", "",
          f"- Test-period flows: {len(test):,}, captures: {len(span)}, exposure {exposure_h * 60:.1f} min "
          f"(per capture: median {per_cap_min['50%']:.1f} min, min {per_cap_min['min']:.1f}, max {per_cap_min['max']:.1f}).",
          f"- Attacker host pairs: {len(att_pairs)} ({', '.join(f'{c} {n}' for c, n in cls_tot.items())}); "
          f"benign-only host pairs: {n_benign_pairs:,}.", "",
          "Horizons: 'reset 60 s' = counts cleared every 60 s from each capture's first test flow (the live "
          "harness rule); 'sliding H' = k verdicts within any H seconds; 'persistent' = never cleared.", ""]
    for ig in ("ignored", "counted"):
        md += [f"## MITM-ARP verdicts {ig}", "", t[t["MITM-ARP verdicts"] == ig].drop(columns="MITM-ARP verdicts").to_markdown(index=False), ""]
    (OUT / ("persistent_counters_corrected.md" if corrected else "persistent_counters.md")).write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
