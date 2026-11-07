"""IoT-23: how many Zeek conn.log rows correspond to each NFStream flow, and do they agree on the class?

The labelled parquet keeps only the one Zeek row the join chose per flow (extract_label.join), so
the candidate rows are re-derived from conn.log.labeled with extract_label's own functions
(read_zeek, tuple_key, map_class, TOL_S). For each flow, a Zeek row "matches" if it has the same
unordered 5-tuple key (tuple_key: ICMP on addresses + protocol) and its interval
[ts, ts + duration] overlaps the flow's [first_seen - TOL_S, last_seen + TOL_S]. Every row the
join could choose ("start": ts within +-2 s of the flow start; "inside": flow start in
[ts, ts + duration + 2 s]) satisfies this, so each flow has >= 1 matching row. We count the
matching rows, how many distinct classes (map_class) they carry, and whether the joined label is
the majority class of those rows. Also, per Zeek row, how many flows it overlaps (rows with none
were never represented by a flow, e.g. the 34-1 DDoS case).

Counting is exact via sorted searches per key: #rows with ts <= last+TOL minus #rows with
end < first-TOL (the second set is a subset of the first). Times in integer ms.

Usage: python src/iot23/zeek_agreement.py
Output: results/iot23/zeek_agreement.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from config import PROCESSED, RAW, RESULTS  # noqa: E402
from iot23.extract_label import TOL_S, map_class, read_zeek, tuple_key  # noqa: E402

CLASSES = ["Attack", "Benign", "C&C", "DDoS", "FileDownload", "Other", "PortScan"]
S = np.int64(2) ** 40  # ms span per key (~34 years)
TOL = int(TOL_S * 1000)


def count_overlaps(q_key, q_lo, q_hi, r_key, r_start, r_end):
    """For each query interval [q_lo, q_hi] (key q_key), the number of reference intervals with the
    same key and r_start <= q_hi and r_end >= q_lo."""
    a = np.sort(r_key * S + r_start)
    e = np.sort(r_key * S + r_end)
    return (np.searchsorted(a, q_key * S + q_hi, side="right")
            - np.searchsorted(e, q_key * S + q_lo, side="left"))


def scenario(name, f):
    z = read_zeek(RAW / "iot23" / name / "conn.log.labeled")
    z["cls"] = [map_class(a, b) for a, b in zip(z.zlabel, z.zdetail)]
    zk = tuple_key(z.a.values, z.ap.values, z.b.values, z.bp.values, z.proto.values).values
    fk = tuple_key(f.src_ip.values, f.src_port.values, f.dst_ip.values, f.dst_port.values, f.protocol.values).values
    codes, _ = pd.factorize(np.concatenate([fk, zk]))
    fkey, zkey = codes[:len(fk)].astype(np.int64), codes[len(fk):].astype(np.int64)
    zs = np.round(z.ts.to_numpy() * 1000).astype(np.int64)
    ze = np.round((z.ts + z.duration).to_numpy() * 1000).astype(np.int64)
    fs = f.bidirectional_first_seen_ms.to_numpy().astype(np.int64)
    fe = f.bidirectional_last_seen_ms.to_numpy().astype(np.int64)
    t0 = min(zs.min(), fs.min()) - 10 * TOL
    zs, ze, fs, fe = zs - t0, ze - t0, fs - t0, fe - t0
    lo, hi = fs - TOL, fe + TOL
    per_cls = np.zeros((len(f), len(CLASSES)), dtype=np.int64)
    zc = z.cls.to_numpy()
    for j, c in enumerate(CLASSES):
        m = zc == c
        if m.any():
            per_cls[:, j] = count_overlaps(fkey, lo, hi, zkey[m], zs[m], ze[m])
    same_key = (np.searchsorted(np.sort(zkey), fkey, side="right") - np.searchsorted(np.sort(zkey), fkey, side="left"))
    # per Zeek row: number of flows it overlaps (same rule, roles swapped)
    flows_per_row = count_overlaps(zkey, zs, ze, fkey, lo, hi)
    out = pd.DataFrame({"scenario": name, "key": fkey, "label": f.label.to_numpy(), "rule": f.match_rule.to_numpy(),
                        "rows": per_cls.sum(1), "same_key_rows": same_key,
                        "n_classes": (per_cls > 0).sum(1),
                        "majority": np.array(CLASSES)[per_cls.argmax(1)],
                        "label_share": per_cls[np.arange(len(f)), [CLASSES.index(c) for c in f.label]] / np.maximum(per_cls.sum(1), 1)})
    for j, c in enumerate(CLASSES):
        out[f"rows_{c}"] = per_cls[:, j]
    zrows = pd.DataFrame({"scenario": name, "cls": zc, "flows": flows_per_row, "key": zkey})
    return out, zrows


def summarize(g):
    multi = g.n_classes > 1
    return pd.Series({
        "flows": len(g),
        "mean rows/flow": round(g.rows.mean(), 2),
        "median": int(g.rows.median()),
        "p99": int(np.percentile(g.rows, 99)),
        "max": int(g.rows.max()),
        "flows with >1 row": f"{(g.rows > 1).mean():.3f}",
        "flows whose rows carry >1 class": int(multi.sum()),
        "share >1 class": f"{multi.mean():.4f}",
        "joined label != majority of rows": int((g.label != g.majority).sum()),
        "mean share of rows with joined label": round(g.label_share.mean(), 4),
    })


def main():
    df = pd.read_parquet(PROCESSED / "iot23_flows.parquet",
                         columns=["src_ip", "src_port", "dst_ip", "dst_port", "protocol", "bidirectional_first_seen_ms",
                                  "bidirectional_last_seen_ms", "source_file", "label", "match_rule"])
    df["scenario"] = df.source_file.str.split("/").str[0]
    parts, zparts = [], []
    for name, f in df.groupby("scenario", sort=False):
        o, zr = scenario(name, f.reset_index(drop=True))
        assert (o.rows >= 1).all(), f"{name}: flow without matching Zeek row"
        parts.append(o)
        zparts.append(zr)
        print(name, len(o), int((o.n_classes > 1).sum()), flush=True)
    a = pd.concat(parts, ignore_index=True)
    z = pd.concat(zparts, ignore_index=True)
    by_class = a.groupby(a.label.to_numpy()).apply(summarize)
    by_scen = a.groupby(a.scenario.to_numpy()).apply(summarize)
    total = summarize(a).to_frame("all flows").T
    # which class combinations co-occur
    combos = a[a.n_classes > 1].apply(
        lambda r: "+".join(c for c in CLASSES if r[f"rows_{c}"] > 0), axis=1).value_counts().to_frame("flows")
    mix = a[a.n_classes > 1].groupby(["scenario", "label"]).size().to_frame("flows with >1 class")
    # Zeek-row side
    zs = z.groupby(["scenario", "cls"]).agg(zeek_rows=("flows", "size"),
                                            distinct_5tuples=("key", "nunique"),
                                            rows_overlapping_no_flow=("flows", lambda v: int((v == 0).sum())),
                                            rows_overlapping_1_flow=("flows", lambda v: int((v == 1).sum())),
                                            rows_overlapping_2plus=("flows", lambda v: int((v >= 2).sum())))
    zs = zs[zs.zeek_rows > 0]
    # DDoS case (34-1)
    dd = a[(a.scenario == "CTU-IoT-Malware-Capture-34-1")]
    ddf = dd[dd.label == "DDoS"]
    dz = z[(z.scenario == "CTU-IoT-Malware-Capture-34-1") & (z.cls == "DDoS")]
    dkeys = set(dz.key)
    ddos_md = [
        f"- Zeek DDoS rows in 34-1: {len(dz):,} on {dz.key.nunique():,} distinct 5-tuples; NFStream flows with joined "
        f"label DDoS: {len(ddf):,}.",
        f"- DDoS rows overlapping >= 1 NFStream flow: {int((dz.flows > 0).sum()):,}; overlapping none: "
        f"{int((dz.flows == 0).sum()):,}.",
        f"- Matching rows per DDoS flow: mean {ddf.rows.mean():.1f}, median {ddf.rows.median():.0f}, "
        f"max {ddf.rows.max():,}; sum over DDoS flows {int(ddf.rows.sum()):,} (rows can match several flows).",
        f"- DDoS flows whose matching rows carry >1 class: {int((ddf.n_classes > 1).sum())}; mean share of DDoS among "
        f"their rows {ddf.label_share.mean():.4f}.",
        f"- 34-1 flows of any joined label that overlap >= 1 DDoS row: {int((dd.rows_DDoS > 0).sum()):,} "
        f"(by joined label: {dd[dd.rows_DDoS > 0].label.value_counts().to_dict()}).",
        f"- 34-1 flows on a 5-tuple that carries DDoS rows (any time): {int(dd.key.isin(dkeys).sum()):,} "
        f"(by joined label: {dd[dd.key.isin(dkeys)].label.value_counts().to_dict()}); distinct such 5-tuples with "
        f">= 1 flow: {dd[dd.key.isin(dkeys)].key.nunique():,} of {len(dkeys):,}.",
    ]
    md = ["# IoT-23: Zeek rows per NFStream flow and their label agreement", "",
          "Matching rule: same unordered 5-tuple (extract_label.tuple_key) and Zeek interval [ts, ts+duration] "
          f"overlapping the flow's [first_seen - {TOL_S:g} s, last_seen + {TOL_S:g} s]. This includes every row the "
          "join could have chosen, so each flow has >= 1 row. Class per row = extract_label.map_class. "
          f"Flows: {len(a):,} (the labelled parquet; the 38 unmatched flows are not in it).", "",
          "## All flows", "", total.to_markdown(), "",
          "## By joined (Zeek) class", "", by_class.to_markdown(), "",
          "## By scenario", "", by_scen.to_markdown(), "",
          "## Class combinations among flows whose rows carry >1 class", "", combos.to_markdown(), "",
          mix.to_markdown(), "",
          "## Zeek-row side: rows per class and how many flows each overlaps", "",
          zs.reset_index().to_markdown(index=False), "",
          "## DDoS in CTU-IoT-Malware-Capture-34-1 (14,394 Zeek rows -> 211 flows)", "", *ddos_md, "",
          "Zeek splits a flood on one 5-tuple into many short connections (repeated SYNs / packets), NFStream "
          "merges them into one bidirectional flow until the 15 s idle or 120 s active timeout, so one flow "
          "overlaps many Zeek rows. Rows whose interval overlaps no flow lie in gaps the flows do not cover "
          "under the +-2 s tolerance (or belong to the unmatched flows)."]
    (RESULTS / "iot23" / "zeek_agreement.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))



if __name__ == "__main__":
    main()
