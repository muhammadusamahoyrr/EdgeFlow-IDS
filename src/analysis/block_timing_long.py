"""Late blocks over the long horizon (round 18): the verdict-time comparison of block_timing.py,
replayed over each capture's whole temporal test period (5.9 h) as in persistent_counters.py.

Verdicts: deployed tree on the offline temporal test flows; labels corrected by the blind audit
(label_corrections.correct, as in persistent_counters.py --corrected). Verdict time:
  (a) flow end                 bidirectional_last_seen_ms
  (b) flow end + 15 s          the idle timeout (live verdicts are not available offline)
Horizons: counters reset every 60 s (the harness rule) and persistent (never cleared).
Metric: share of attack flows (by flow start) that start after their pair's block.

Usage: python src/analysis/block_timing_long.py
Output: results/final/block_timing_long.md
"""
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analysis.label_corrections import correct  # noqa: E402
from analysis.persistent_counters import block_times  # noqa: E402
from config import PROCESSED, RESULTS  # noqa: E402
from train_baseline import temporal_split  # noqa: E402

KS = [1, 3, 10]


def main():
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    df.index = pd.RangeIndex(len(df))
    correct(df)
    df["label"] = df.pop("label_new")
    _, test = temporal_split(df)
    del df
    with open(RESULTS / "models" / "decision_tree.pkl", "rb") as f:  # project's own model file
        bundle = pickle.load(f)
    test = test.assign(pred=bundle["model"].predict(test[bundle["features"]].to_numpy(np.float32)))
    s, d = test.src_ip.astype(str).to_numpy(), test.dst_ip.astype(str).to_numpy()
    lo, hi = np.where(s < d, s, d), np.where(s < d, d, s)
    test["pair"] = test.source_file.astype(str).to_numpy().astype(object) + "|" + lo.astype(object) + "|" + hi.astype(object)
    span = test.groupby("source_file").bidirectional_first_seen_ms.min()
    test["t0"] = test.source_file.map(span).astype(np.int64)
    att = test[test.label != "Benign"]
    rows = []
    for ignore in (False, True):
        mask = test.pred != "Benign"
        if ignore:
            mask &= test.pred != "MITM-ARP"
        for tname, shift in (("(a) flow end", 0), ("(b) flow end + 15 s", 15000)):
            v = test.loc[mask, ["pair", "t0"]].assign(t=test.loc[mask, "bidirectional_last_seen_ms"].astype(np.int64) + shift)
            v = v.sort_values(["pair", "t"]).reset_index(drop=True)
            for hname, mode in (("reset 60 s", "reset"), ("persistent", "persistent")):
                for k in KS:
                    bt = block_times(v, k, mode, 60)
                    hit = att.bidirectional_first_seen_ms > att.pair.map(bt)
                    after = float(hit.mean())
                    per = hit.groupby(att.label).mean().round(3).to_dict()
                    rows.append({"MITM-ARP verdicts": "ignored" if ignore else "counted", "verdict time": tname,
                                 "horizon": hname, "k": k, "attack flows after block": round(after, 4),
                                 **{f"{c}": per.get(c) for c in sorted(att.label.unique())}})
                    print(rows[-1], flush=True)
    md = ["# Late blocks over the 5.9 h test periods (round 18)", "",
          f"Script: src/analysis/block_timing_long.py. Attack flows: {len(att):,} (audit-corrected labels); "
          "per-class columns give the share for that class's attack flows.", "",
          "Test-period span per capture (s): " + ", ".join(f"{c.split('/')[0]} {v:.0f}" for c, v in
              ((test.groupby('source_file').bidirectional_last_seen_ms.max() - span) / 1000).items()) + "; attack flows per class: "
          + ", ".join(f"{c} {n:,}" for c, n in att.label.value_counts().sort_index().items()), "",
          pd.DataFrame(rows).to_markdown(index=False)]
    (RESULTS / "final" / "block_timing_long.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
