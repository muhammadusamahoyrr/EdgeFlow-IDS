"""CPU budget with the confounds removed (final review M7, plan item D1).

Old runs (run1*, edge100, edge50*) differ in CPU budget, achieved replay rate (tcpreplay shared
the CPU with the gateway), harness version (run1, edge100) and window set. The pinned runs
(pin_<budget>_r<i>, src/run_pinned.sh) use one harness and the same three windows. tcpreplay,
the keep-alive ping and the gateway run on disjoint cores (0 / 1 / 2-5), budgets none, 1 core and
1/2 core, three repeats each, interleaved.

Per run and window: achieved replay pps, replay/original rate, live/offline flows, same packets
and match rate (logic of final_fidelity.py), median verdict delay after flow end, gateway CPU,
catch-up wait after the gap, macro-F1 of the run. Then for each window: delay by budget (mean,
range); OLS delay ~ budget + replay pps on the old runs and on the pinned runs; Kruskal-Wallis
across budgets on the pinned runs.

Usage: python src/analysis/cpu_factorial.py
Output: results/final/cpu_factorial.md
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import kruskal  # noqa: E402

from analysis.final_fidelity import ATT, KEY, drop_continuing, in_window, label_flows, load_model, offline, with_occurrence  # noqa: E402
from config import FOLDER_TO_CLASS, RESULTS  # noqa: E402

OUT = RESULTS / "final"
OLD = ["run1", "run1_r2", "run1_r3", "edge100", "edge50", "edge50_r2", "edge50_r3"]
BUDGET = {None: "none", 100: "1 core", 50: "1/2 core"}


def run_rows(tag):
    run = RESULTS / "live" / tag
    meta = json.loads((run / "windows.json").read_text())
    lvo = json.loads((run / "live_vs_offline.json").read_text())
    per_w = {w["window"]: w for w in lvo["windows"]}
    mname, bundle = load_model(meta)
    live_all = pd.read_csv(run / "flows.csv")
    rows = []
    for w in meta["windows"]:
        off, span_s = offline(w, mname, bundle)
        keys = bundle.get("continuing_connections", {}).get(w["source_file"], [])
        lv, _ = drop_continuing(in_window(live_all, w), keys)
        lv = with_occurrence(label_flows(lv.copy(), FOLDER_TO_CLASS[w["folder"]], ATT.get(w["folder"], {})))
        m = off.merge(lv, on=KEY + ["occ"], how="inner", suffixes=("_off", "_live"))
        pw = per_w.get(w["folder"], {})
        orig_pps = w["packets"] / span_s if span_s > 0 else np.nan
        rows.append({"run": tag, "pinned": bool(meta.get("pinned")), "budget": BUDGET[meta.get("cpu_quota")],
                     "window": w["folder"], "replay pps": w.get("offered_pps"),
                     "replay / original": round(w.get("offered_pps", np.nan) / orig_pps, 3),
                     "live/offline flows": round(len(lv) / len(off), 4),
                     "match rate": round(len(m) / len(off), 4),
                     "same packets": round(float((m.bidirectional_packets_off == m.bidirectional_packets_live).mean()), 4),
                     "same verdict": round(float((m.pred_off == m.pred_live).mean()), 4),
                     "delay (s)": pw.get("median_verdict_after_flow_end_s"),
                     "CPU mean %": pw.get("cpu_percent_mean"), "CPU max %": pw.get("cpu_percent_max"),
                     "catch-up wait (s)": w.get("caught_up_after_gap_s"),
                     "run macro-F1": round(lvo["live"]["macro_f1"], 4),
                     "kernel drops": lvo["nfstream_counters"].get("packets_dropped_filtered_by_kernel")})
        print(rows[-1], flush=True)
    return rows


def ols(d):
    """delay ~ 1 + [1 core] + [1/2 core] + replay pps (per 1,000 pps). Returns coef table."""
    X = np.column_stack([np.ones(len(d)), (d.budget == "1 core").astype(float),
                         (d.budget == "1/2 core").astype(float), d["replay pps"] / 1000])
    keep = [0] + [i for i in (1, 2) if X[:, i].any()] + [3]
    X = X[:, keep]
    names = np.array(["intercept", "1 core vs none", "1/2 core vs none", "per +1,000 pps"])[keep]
    y = d["delay (s)"].to_numpy(float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    if dof <= 0:
        return pd.DataFrame({"term": names, "coef": beta.round(2), "s.e.": np.nan})
    s2 = resid @ resid / dof
    se = np.sqrt(np.diag(s2 * np.linalg.pinv(X.T @ X)))
    return pd.DataFrame({"term": names, "coef (s)": beta.round(2), "s.e.": se.round(2), "n": len(y), "dof": dof})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pinned = sorted(p.name for p in (RESULTS / "live").glob("pin_*") if (p / "live_vs_offline.json").exists())
    rows = []
    for tag in OLD + pinned:
        rows += run_rows(tag)
    t = pd.DataFrame(rows)
    t["set"] = np.where(t.pinned, "pinned", "old")
    md = ["# CPU budget without the confounds (final review M7, plan D1)", "",
          "Script: src/analysis/cpu_factorial.py. Pinned runs: src/run_pinned.sh (tcpreplay core 0, ping core 1, "
          "gateway cores 2-5 under the cgroup quota; one harness; windows DDoS-SYN_Flood, Mirai-udpplain, "
          "DoS-HTTP_Flood; budgets interleaved, 3 repeats). Old runs as in results/repeats.md. "
          "Delay = median verdict time after flow end in the window.", "",
          "## Every run and window", "",
          t.drop(columns=["pinned"]).sort_values(["window", "set", "budget", "run"]).to_markdown(index=False), ""]
    for win in ["DDoS-SYN_Flood", "DoS-HTTP_Flood", "Mirai-udpplain"]:
        d = t[t.window == win]
        md += [f"## {win}", ""]
        g = (d.groupby(["set", "budget"]).agg(runs=("run", "size"),
                                              pps_min=("replay pps", "min"), pps_max=("replay pps", "max"),
                                              delay_mean=("delay (s)", "mean"), delay_min=("delay (s)", "min"),
                                              delay_max=("delay (s)", "max"),
                                              flows_ratio_min=("live/offline flows", "min"),
                                              flows_ratio_max=("live/offline flows", "max"),
                                              same_pk_min=("same packets", "min"),
                                              catchup_max=("catch-up wait (s)", "max")).round(3))
        md += [g.to_markdown(), ""]
        for s in ("old", "pinned"):
            dd = d[d.set == s].dropna(subset=["delay (s)", "replay pps"])
            if len(dd) >= 4:
                md += [f"OLS delay ~ budget + replay rate, {s} runs:", "", ols(dd).to_markdown(index=False), ""]
        dp = d[d.set == "pinned"]
        groups = [g["delay (s)"].dropna().to_numpy() for _, g in dp.groupby("budget")]
        if len(groups) >= 2 and all(len(x) >= 2 for x in groups):
            h, p = kruskal(*groups)
            md += [f"Kruskal-Wallis across budgets (pinned): H = {h:.2f}, p = {p:.3f}; "
                   f"replay pps range in pinned runs {dp['replay pps'].min():,.0f}-{dp['replay pps'].max():,.0f}.", ""]
    (OUT / "cpu_factorial.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
