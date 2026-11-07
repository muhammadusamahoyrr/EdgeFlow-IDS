"""Offline flow extraction for IoT-23, labelled by joining NFStream flows to Zeek conn.log.labeled.

Flows come from NFStream with the same settings as the CIC-IoT2023 pipeline (config.STREAMER_KW).
Each flow is joined to the scenario's Zeek connections on the unordered 5-tuple (so both
directions match; ICMP on addresses + protocol only, since Zeek stores type/code as ports):
  1. "start": the Zeek connection with the nearest start time within +-2 s;
  2. "inside": otherwise, the latest Zeek connection that started before the flow and was still
     open when it started (ts <= start <= ts + duration + 2 s). NFStream cuts connections after
     15 s idle / 120 s active, Zeek only after 1-5 min idle, so later pieces of a long Zeek
     connection start well after the Zeek ts.
Flows without a Zeek match are dropped and counted.

Zeek detailed labels -> class (CLASS_MAP); label "Benign" or detailed label "-" -> Benign:
  PartOfAHorizontalPortScan -> PortScan; C&C, C&C-Torii, C&C-HeartBeat, ... -> C&C;
  DDoS -> DDoS; Attack, Okiru, Okiru-Attack -> Attack; FileDownload, C&C-FileDownload ->
  FileDownload; anything else -> Other.
file_label = what labelling by capture would assign: Benign for honeypot captures, otherwise
the scenario's malware family mapped to its main malicious behaviour (FAMILY_CLASS, see there).

Usage: python src/iot23/extract_label.py
Output: data/processed/iot23_flows.parquet, results/iot23/match_rates.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from nfstream import NFStreamer  # noqa: E402

from config import PROCESSED, RAW, RESULTS, STREAMER_KW  # noqa: E402
from iot23.download import SCENARIOS  # noqa: E402

TOL_S = 2.0
PROTO = {"tcp": 6, "udp": 17, "icmp": 1}
ICMP = (1, 58)

# Malware family -> the class a "label by capture" study would give every flow of that capture:
# the family's main malicious behaviour in IoT-23 (Hide&Seek, Muhstik: horizontal port scans;
# Hakai, Torii: C&C; Mirai 34-1: DDoS; Trojan 42-1: file download).
FAMILY_CLASS = {"Benign": "Benign", "Hide&Seek": "PortScan", "Muhstik": "PortScan", "Hakai": "C&C",
                "Torii": "C&C", "Mirai": "DDoS", "Trojan": "FileDownload"}


def map_class(label, detailed):
    if label.lower() == "benign" or detailed == "-":
        return "Benign"
    if detailed == "PartOfAHorizontalPortScan":
        return "PortScan"
    if "FileDownload" in detailed:
        return "FileDownload"
    if detailed.startswith("C&C"):
        return "C&C"
    if detailed == "DDoS":
        return "DDoS"
    if detailed in ("Attack", "Okiru", "Okiru-Attack"):
        return "Attack"
    return "Other"


def read_zeek(path):
    """conn.log.labeled -> DataFrame. The label columns are tab- or space-separated depending on
    the file version, so the tail after the 20 standard fields is split on any whitespace."""
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            tail = " ".join(p[20:]).split()
            rows.append((p[0], p[2], p[3], p[4], p[5], p[6], p[8], tail[-2], tail[-1]))
    z = pd.DataFrame(rows, columns=["ts", "a", "ap", "b", "bp", "proto", "duration", "zlabel", "zdetail"])
    z["ts"] = z.ts.astype(float)
    z["duration"] = pd.to_numeric(z.duration, errors="coerce").fillna(0.0)
    z["proto"] = z.proto.map(PROTO).fillna(-1).astype(int)
    z.loc[(z.proto == 1) & z.a.str.contains(":"), "proto"] = 58  # Zeek logs ICMPv6 as "icmp"
    z["ap"] = z.ap.astype(int)
    z["bp"] = z.bp.astype(int)
    return z


def tuple_key(a, ap, b, bp, proto):
    """Unordered 5-tuple as a string; ports ignored for ICMP."""
    icmp = np.isin(proto, ICMP)
    ap = np.where(icmp, 0, ap)
    bp = np.where(icmp, 0, bp)
    ea = pd.Series(a).astype(str) + ":" + pd.Series(ap).astype(str)
    eb = pd.Series(b).astype(str) + ":" + pd.Series(bp).astype(str)
    lo, hi = np.where(ea < eb, ea, eb), np.where(ea < eb, eb, ea)
    return pd.Series(lo) + "|" + pd.Series(hi) + "|" + pd.Series(proto).astype(str)


def join(flows, z):
    """Index of the matched Zeek row per flow (-1 if none) and the match rule."""
    f = pd.DataFrame({"key": tuple_key(flows.src_ip.values, flows.src_port.values, flows.dst_ip.values,
                                       flows.dst_port.values, flows.protocol.values).values,
                      "t": flows.bidirectional_first_seen_ms.values / 1000.0,
                      "i": np.arange(len(flows))})
    zz = z.assign(key=tuple_key(z.a.values, z.ap.values, z.b.values, z.bp.values, z.proto.values).values,
                  t=z.ts, end=z.ts + z.duration, zi=np.arange(len(z)))[["key", "t", "end", "zi"]]
    f, zz = f.sort_values("t"), zz.sort_values("t")
    near = pd.merge_asof(f, zz, on="t", by="key", direction="nearest", tolerance=TOL_S)
    before = pd.merge_asof(f, zz, on="t", by="key", direction="backward")
    inside = before.zi.notna() & (before.t <= before.end + TOL_S)
    zi = np.full(len(flows), -1)
    rule = np.full(len(flows), "none", dtype=object)
    zi[before.i[inside]] = before.zi[inside]
    rule[before.i[inside]] = "inside"
    ok = near.zi.notna()
    zi[near.i[ok]] = near.zi[ok]
    rule[near.i[ok]] = "start"
    return zi, rule


def main():
    parts, rates = [], []
    for name, (_, pcap, family) in SCENARIOS.items():
        d = RAW / "iot23" / name
        src = d / pcap.removesuffix(".xz")
        flows = NFStreamer(source=str(src), **STREAMER_KW).to_pandas()
        z = read_zeek(d / "conn.log.labeled")
        zi, rule = join(flows, z)
        hit = zi >= 0
        zl = z.iloc[zi[hit]]
        flows = flows[hit].copy()
        flows["zeek_label"], flows["zeek_detailed"] = zl.zlabel.values, zl.zdetail.values
        flows["label"] = [map_class(a, b) for a, b in zip(zl.zlabel, zl.zdetail)]
        flows["match_rule"] = rule[hit]
        flows["family"] = family
        flows["file_label"] = FAMILY_CLASS[family]
        flows["source_file"] = f"{name}/{src.name}"
        n = len(hit)
        rates.append({"scenario": name, "NFStream flows": n, "Zeek conns": len(z),
                      "matched (start +-2 s)": int((rule == "start").sum()),
                      "matched (inside Zeek conn)": int((rule == "inside").sum()),
                      "unmatched (dropped)": int((~hit).sum()),
                      "match rate": round(hit.mean(), 4) if n else float("nan"),
                      "start-only rate": round((rule == "start").mean(), 4) if n else float("nan")})
        print(rates[-1], flows.label.value_counts().to_dict())
        parts.append(flows)
    out = pd.concat(parts, ignore_index=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out.to_parquet(PROCESSED / "iot23_flows.parquet", index=False)
    r = pd.DataFrame(rates)
    tot = r.drop(columns="scenario").sum(numeric_only=True)
    md = ["# IoT-23: NFStream flows joined to Zeek conn.log.labeled", "",
          f"Join: unordered 5-tuple + nearest start within +-{TOL_S:g} s; otherwise the flow's start "
          "inside a Zeek connection with the same 5-tuple (NFStream splits long connections; Zeek does not).", "",
          r.to_markdown(index=False), "",
          f"Total: {int(tot['NFStream flows']):,} flows, matched "
          f"{1 - tot['unmatched (dropped)'] / tot['NFStream flows']:.2%} "
          f"(start rule alone {tot['matched (start +-2 s)'] / tot['NFStream flows']:.2%}); "
          f"{int(tot['unmatched (dropped)']):,} unmatched flows dropped.", "",
          "Zeek connections can outnumber flows: Zeek logs repeated SYNs and flood packets on one 5-tuple "
          "as many short connections, which NFStream merges into one flow (e.g. 34-1: 14,394 Zeek DDoS "
          "connections on 317 distinct 5-tuples). Zeek and pcap time ranges agree to the millisecond, "
          "so no clock offset was applied.", "",
          "Class counts after the join:", "", out.label.value_counts().to_frame("flows").to_markdown(), "",
          "Zeek (label, detailed-label) -> class:", "",
          out.groupby(["zeek_label", "zeek_detailed", "label"]).size().to_frame("flows").to_markdown()]
    (RESULTS / "iot23").mkdir(parents=True, exist_ok=True)
    (RESULTS / "iot23" / "match_rates.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
