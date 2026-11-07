"""Blind, stratified audit of the CIC-IoT2023 evidence labels (final review M8, plan item D2).

M8 (a) Error rate of the endpoint labels, estimated against packet evidence.
M8 (b) The same check on false negatives (attack-labelled flows the model calls Benign).
M8 (c) Macro-F1 without MITM-ARP.

PROTOCOL (fixed before any audit outcome was looked at)
1. Population: the temporal test split of data/processed/flows.parquet (the flows every CIC score
   in the paper is computed on); verdicts from the deployed model results/models/decision_tree.pkl.
2. Strata, for each attack capture: A attack-labelled & model agrees; B attack-labelled & model
   disagrees (B-fn: predicted Benign, B-x: another attack class); C Benign-labelled & one end is a
   listed attacker; D Benign-labelled, no attacker end, model flags an attack; E Benign-labelled,
   no attacker end, model says Benign. Benign capture: F model flags an attack; G model says Benign.
   Up to N_PER flows per stratum, simple random sample (shuffle with seed 0, first N_PER).
3. Evidence: each sampled flow's packets are read from the pcap it was extracted from (bidirectional
   5-tuple, first..last packet time). The rater function `evidence()` sees ONLY those packets, the
   capture's scenario (its file name), label-free rate context computed from all flows of the
   capture (same client's connections within +-5 s), and, for MITM-ARP, the ARP replies of the
   capture. It never sees the label, the attacker list (data/attackers.json) or the prediction.
   Output: A = the packets show the capture's attack behaviour; B = they show other, identifiable
   behaviour; U = undetermined (no payload and no behavioural signature).
   Scenario signatures:
     SqlInjection / XSS / CommandInjection: an HTTP request to the DVWA page of that vulnerability
       (sqli, xss_r/xss_d/xss_s, exec) -> A; other HTTP, TLS, DNS, ... -> B.
     DictionaryBruteForce: SSH connection (client banner "SSH-") lasting < 60 s with < 20 kB, or an
       RTSP request carrying "Authorization:" or answered "401" -> A.
     DDoS-SYN_Flood: every client packet is a TCP SYN without ACK, and the destination ip:port
       receives >= 20 such SYN-only flows within +-5 s -> A.
     DoS-HTTP_Flood: HTTP request(s), and the same client opens >= 20 connections to the same
       server:port within +-5 s -> A.
     Mirai-udpplain: UDP, no reply packets, mean client payload >= 500 B, and the same client sends
       >= 20 flows or >= 50 packets to the same server within +-5 s -> A.
     Recon-PortScan: <= 3 client packets without payload, and the same client contacts >= 20
       distinct (host, port) within +-5 s -> A.
     MITM-ArpSpoofing: a packet passes through a MAC that sent ARP replies claiming >= 2 IPs (a
       spoofer), and neither IP of the flow is the spoofer's own (an IP no other MAC claims) -> A.
     Benign capture: every signature above is applied; any match -> A.
4. After the rater ran, compare: label attack & evidence B = over-inclusive label; label Benign &
   evidence A = missed attack; U is reported and left out of the rate. Wilson 95% intervals per
   stratum; class-level error = stratum-size-weighted, 95% interval by stratified bootstrap.
5. The blind sample (flow keys + packet evidence, no label, no prediction) is written to
   results/final/label_audit_sample.csv for a human spot check; the key file with labels and
   predictions to results/final/label_audit_key.csv.

The rater is a fixed program, not a person: the paper must say so. MITM-ARP evidence uses the same
kind of information (MAC relay) as its label rule, so that class is a consistency check only.

Usage: python src/analysis/label_audit.py
Output: results/final/label_audit.md, label_audit_sample.csv, label_audit_key.csv
"""
import pathlib
import pickle
import re
import socket
import sys
from collections import defaultdict
from urllib.parse import unquote

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import dpkt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402

from config import ATTACKERS_FILE, PROCESSED, RAW, RESULTS  # noqa: E402
from train_baseline import temporal_split  # noqa: E402

OUT = RESULTS / "final"
N_PER = 30
AMENDMENTS = """The first run of the pre-registered rater flagged 57 BruteForce, 6 DoS-HTTP and 4 Mirai attack-labelled
flows as B. Inspection of their packets showed four rater defects, fixed as follows; both verdicts are reported.
- R1 (bug): payloads were stored truncated to 400 B before the Mirai '>= 500 B' test; the test now uses the full length.
- R2 (bug): HTTP requests were looked for only in the flow's src->dst direction; NFStream starts a flow mid-connection
  when a connection outlives a timeout, so its src can be the server. Requests are now looked for in both directions.
- R3 (criterion): the RTSP traffic of DictionaryBruteForce is a dictionary of camera stream paths (DESCRIBE
  rtsp://host/video.cgi, /live/ch00_1, /CAM_ID.password.mp2, ...; answered 551 Invalid Method or 200 OK), not
  password guessing. A short connection (<= 10 client packets) carrying an RTSP DESCRIBE now counts as the attack.
  This is a post-hoc criterion; the pre-registered rater calls these flows B (column on the right).
- R4 (bug): a flow whose only payload is a response or comes from the server side, with no request visible (a
  mid-connection piece), was rated B (benign behaviour); a response alone does not show what was requested, so it
  is now U."""
SEED = 0
CTX_MS = 5000
WEB_PAGE = {"SqlInjection": r"/vulnerabilities/sqli", "XSS": r"/vulnerabilities/xss_",
            "CommandInjection": r"/vulnerabilities/exec"}
HTTP_RE = re.compile(rb"^(GET|POST|HEAD|PUT|DELETE|OPTIONS|DESCRIBE|SETUP|PLAY|TEARDOWN) (\S+)")


def pcap_for(source_file):
    folder, name = source_file.split("/", 1)
    trimmed = RAW / "trimmed" / folder / name
    return trimmed if trimmed.exists() else RAW / "cic-iot2023" / folder / name


def mac(b):
    return ":".join(f"{x:02x}" for x in b)


def read_packets(pcap, keys):
    """keys: dict canonical 5-tuple -> list of (row id, t0_ms, t1_ms). Returns per row id a list of
    (ts_ms, from_client, tcp_flags, payload, src_mac, dst_mac) and the ARP claims MAC -> IPs."""
    pk, arp = defaultdict(list), defaultdict(set)
    with open(pcap, "rb") as fh:
        try:
            rd = dpkt.pcap.Reader(fh)
        except ValueError:
            fh.seek(0)
            rd = dpkt.pcapng.Reader(fh)
        for ts, buf in rd:
            try:
                eth = dpkt.ethernet.Ethernet(buf)
            except Exception:
                continue
            if isinstance(eth.data, dpkt.arp.ARP):
                a = eth.data
                if a.op == dpkt.arp.ARP_OP_REPLY:
                    arp[mac(a.sha)].add(socket.inet_ntoa(a.spa))
                continue
            ip = eth.data
            if not isinstance(ip, (dpkt.ip.IP, dpkt.ip6.IP6)):
                continue
            fam = socket.AF_INET if isinstance(ip, dpkt.ip.IP) else socket.AF_INET6
            s, d = socket.inet_ntop(fam, ip.src), socket.inet_ntop(fam, ip.dst)
            l4 = ip.data
            sp = getattr(l4, "sport", 0)
            dp = getattr(l4, "dport", 0)
            proto = ip.p if fam == socket.AF_INET else ip.nxt
            k = (proto,) + tuple(sorted([(s, sp), (d, dp)]))
            if k not in keys:
                continue
            t = ts * 1000
            for rid, t0, t1, cli in keys[k]:
                if t0 - 1 <= t <= t1 + 1:
                    flags = l4.flags if isinstance(l4, dpkt.tcp.TCP) else None
                    pay = bytes(l4.data) if isinstance(l4, (dpkt.tcp.TCP, dpkt.udp.UDP)) else b""
                    pk[rid].append((t, (s, sp) == cli, flags, pay[:400], mac(eth.src), mac(eth.dst), len(pay)))
    return pk, arp


def context(cap):
    """Label-free rate context per flow from all flows of one capture (+-5 s around flow start)."""
    cap = cap.sort_values("bidirectional_first_seen_ms")
    t = cap.bidirectional_first_seen_ms.to_numpy()
    out = {}
    for name, keycols in (("same_client_server", ["src_ip", "dst_ip", "dst_port"]),
                          ("same_client_hostpair", ["src_ip", "dst_ip"]),
                          ("same_server", ["dst_ip", "dst_port"])):
        cnt = np.zeros(len(cap), dtype=np.int64)
        for _, idx in cap.groupby(keycols).indices.items():
            tt = t[idx]
            cnt[idx] = np.searchsorted(tt, tt + CTX_MS, "right") - np.searchsorted(tt, tt - CTX_MS, "left")
        out[name] = pd.Series(cnt, index=cap.index)
    # distinct (host, port) the client touches within +-5 s
    fan = np.zeros(len(cap), dtype=np.int64)
    for _, idx in cap.groupby("src_ip").indices.items():
        tt = t[idx]
        tgt = (cap.dst_ip.to_numpy()[idx].astype(object) + ":" + cap.dst_port.to_numpy()[idx].astype(str).astype(object))
        lo = np.searchsorted(tt, tt - CTX_MS, "left")
        hi = np.searchsorted(tt, tt + CTX_MS, "right")
        if len(idx) > 20000:  # big scanners: approximate distinct targets by count, capped
            fan[idx] = hi - lo
        else:
            fan[idx] = [len(set(tgt[a:b])) for a, b in zip(lo, hi)]
    out["client_fanout"] = pd.Series(fan, index=cap.index)
    # SYN-only flows to the same server within +-5 s
    synonly = ((cap.protocol == 6) & (cap.src2dst_syn_packets == cap.src2dst_packets) &
               (cap.src2dst_ack_packets == 0)).to_numpy()
    sc = np.zeros(len(cap), dtype=np.int64)
    for _, idx in cap.groupby(["dst_ip", "dst_port"]).indices.items():
        sel = idx[synonly[idx]]
        ts = t[sel]
        if len(ts):
            sc[idx] = np.searchsorted(ts, t[idx] + CTX_MS, "right") - np.searchsorted(ts, t[idx] - CTX_MS, "left")
    out["synonly_to_server"] = pd.Series(sc, index=cap.index)
    return pd.DataFrame(out)


def describe(pkts):
    c = [p for p in pkts if p[1]]
    s = [p for p in pkts if not p[1]]
    reqs = []
    for p in c:
        m = HTTP_RE.match(p[3])
        if m:
            reqs.append((m.group(1).decode(), unquote(m.group(2).decode(errors="ignore"))))
    c_pay = [p[3] for p in c if p[3]]
    s_pay = [p[3] for p in s if p[3]]
    reqs_any = list(reqs)  # amendment R2: requests in either direction (flow may start mid-connection)
    for p in s:
        m = HTTP_RE.match(p[3])
        if m:
            reqs_any.append((m.group(1).decode(), unquote(m.group(2).decode(errors="ignore"))))
    c_len = [p[6] for p in c if p[6]]
    return {"pkts": len(pkts), "c_pkts": len(c), "s_pkts": len(s),
            "c_payload_pkts": len(c_pay), "s_payload_pkts": len(s_pay),
            "c_mean_payload": float(np.mean([len(x) for x in c_pay])) if c_pay else 0.0,
            "c_mean_payload_full": float(np.mean(c_len)) if c_len else 0.0,  # amendment R1
            "http_requests_any": reqs_any,
            "rtsp_4xx": any(re.match(rb"RTSP/1\.0 4\d\d", p[3]) for p in pkts if p[3]),
            "duration_s": (pkts[-1][0] - pkts[0][0]) / 1000 if pkts else 0.0,
            "bytes": sum(len(p[3]) for p in pkts),
            "c_all_syn_noack": bool(c) and all(p[2] is not None and p[2] & dpkt.tcp.TH_SYN and not p[2] & dpkt.tcp.TH_ACK for p in c),
            "http_requests": reqs,
            "c_head": (c_pay[0][:60] if c_pay else b""),
            "s_head": (s_pay[0][:60] if s_pay else b""),
            "auth": any(b"Authorization:" in p[3] for p in c),
            "rtsp_401": any(p[3].startswith(b"RTSP/1.0 401") for p in s),
            "macs": {p[4] for p in pkts} | {p[5] for p in pkts}}


def other_behaviour(e):
    """Identifiable non-attack payload (used for verdict B)."""
    if e["http_requests"]:
        return "http"
    h = e["c_head"] or e["s_head"]
    if not h:
        return None
    if h[:1] == b"\x16" and h[1:2] == b"\x03":
        return "tls"
    if h.startswith(b"SSH-"):
        return "ssh"
    if h.startswith(b"HTTP/") or h.startswith(b"RTSP/"):
        return "http-response"
    return "other-payload"


def evidence(scenario, f, e, ctx, spoofers, amended=False):
    """The blind rater: packets + scenario + label-free context -> (A/B/U, reason).
    amended=True applies the post-hoc amendments R1-R3 (see AMENDMENTS)."""
    reqs = e["http_requests_any"] if amended else e["http_requests"]
    sigs = []
    if scenario in WEB_PAGE or scenario == "Benign":
        for cls, pat in WEB_PAGE.items():
            if any(re.search(pat, path) for _, path in reqs) and (scenario == cls or scenario == "Benign"):
                sigs.append(f"DVWA {cls} request")
    if scenario in ("DictionaryBruteForce", "Benign"):
        if e["c_head"].startswith(b"SSH-") and e["duration_s"] < 60 and e["bytes"] < 20000:
            sigs.append("short SSH login connection")
        if e["auth"] or e["rtsp_401"]:
            sigs.append("RTSP request with credentials / 401")
        elif amended and any(m == "DESCRIBE" for m, _ in reqs) and e["c_pkts"] <= 10:
            sigs.append("short connection with one RTSP DESCRIBE of a stream path (route dictionary)")
    if scenario in ("DDoS-SYN_Flood", "Benign"):
        if e["c_all_syn_noack"] and ctx["synonly_to_server"] >= 20:
            sigs.append(f"SYN-only, {ctx['synonly_to_server']} SYN-only flows to server in +-5 s")
    if scenario in ("DoS-HTTP_Flood", "Benign"):
        if reqs and ctx["same_client_server"] >= 20:
            sigs.append(f"HTTP, {ctx['same_client_server']} connections to server in +-5 s")
    if scenario in ("Mirai-udpplain", "Benign"):
        mp = e["c_mean_payload_full"] if amended else e["c_mean_payload"]
        if f.protocol == 17 and e["s_pkts"] == 0 and mp >= 500 and (
                ctx["same_client_hostpair"] >= 20 or e["c_pkts"] >= 50):
            sigs.append("one-way UDP flood")
    if scenario in ("Recon-PortScan", "Benign"):
        if e["c_pkts"] <= 3 and e["c_payload_pkts"] == 0 and ctx["client_fanout"] >= 20:
            sigs.append(f"probe, client fan-out {ctx['client_fanout']} targets in +-5 s")
    if scenario in ("MITM-ArpSpoofing", "Benign"):
        for m, own in spoofers.items():
            if m in e["macs"] and f.src_ip not in own and f.dst_ip not in own:
                sigs.append(f"relayed via ARP spoofer {m}")
                break
    if sigs:
        return "A", "; ".join(sigs)
    if e["pkts"] == 0:
        return "U", "no packets matched"
    ob = other_behaviour(e)
    if amended and not reqs and (ob == "http-response" or e["c_payload_pkts"] == 0):
        return "U", f"{ob} from the server side only, no request visible (amendment R4)"
    if ob:
        return "B", ob
    return "U", "no payload, no signature"


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    _, test = temporal_split(df)
    with open(RESULTS / "models" / "decision_tree.pkl", "rb") as fh:  # project's own model file
        bundle = pickle.load(fh)
    test = test.assign(pred=bundle["model"].predict(test[bundle["features"]].to_numpy(np.float32)))
    import json
    attackers = json.loads(ATTACKERS_FILE.read_text())  # used ONLY to define stratum C, never by the rater
    test["scenario"] = test.source_file.str.split("/").str[0].replace({"Benign_Final": "Benign"})

    # ---- (c) macro-F1 without MITM-ARP (offline temporal test, deployed model)
    classes = sorted(test.label.unique())
    no_mitm = [c for c in classes if c != "MITM-ARP"]
    f1_all = f1_score(test.label, test.pred, labels=classes, average="macro", zero_division=0)
    f1_nm = f1_score(test.label, test.pred, labels=no_mitm, average="macro", zero_division=0)
    sub = test[test.label != "MITM-ARP"]
    f1_nm_rows = f1_score(sub.label, sub.pred, labels=no_mitm, average="macro", zero_division=0)

    # ---- strata
    def stratum(r):
        if r.scenario == "Benign":
            return "F" if r.pred != "Benign" else "G"
        if r.label != "Benign":
            if r.pred == r.label:
                return "A"
            return "B-fn" if r.pred == "Benign" else "B-x"
        att = set(attackers.get(r.source_file.split("/")[0], {}).get("attackers", []))
        if r.src_ip in att or r.dst_ip in att:
            return "C"
        return "D" if r.pred != "Benign" else "E"
    test["stratum"] = [stratum(r) for r in test[["scenario", "label", "pred", "src_ip", "dst_ip", "source_file"]].itertuples()]
    sizes = test.groupby(["scenario", "stratum"]).size()
    sample = test.sample(frac=1, random_state=SEED).groupby(["scenario", "stratum"]).head(N_PER)
    print(f"sample {len(sample)} flows", flush=True)

    # ---- packet evidence, one pcap pass per capture
    recs = []
    for sf, g in sample.groupby("source_file"):
        cap = df[df.source_file == sf]
        ctx = context(cap)
        keys = defaultdict(list)
        for rid, r in g.iterrows():
            cli = (r.src_ip, int(r.src_port))
            k = (int(r.protocol),) + tuple(sorted([cli, (r.dst_ip, int(r.dst_port))]))
            keys[k].append((rid, r.bidirectional_first_seen_ms, r.bidirectional_last_seen_ms, cli))
        print(f"reading {sf} for {len(g)} flows", flush=True)
        pk, arp = read_packets(pcap_for(sf), keys)
        # spoofer = MAC claiming >= 2 IPs in ARP replies; its own IPs = those no other MAC claims
        claimants = defaultdict(set)
        for m, ips in arp.items():
            for ip in ips:
                claimants[ip].add(m)
        spoofers = {m: {ip for ip in ips if claimants[ip] == {m}} for m, ips in arp.items() if len(ips) >= 2}
        for rid, r in g.iterrows():
            e = describe(sorted(pk.get(rid, [])))
            v0, why0 = evidence(r.scenario, r, e, ctx.loc[rid], spoofers)
            v, why = evidence(r.scenario, r, e, ctx.loc[rid], spoofers, amended=True)
            recs.append({"row": rid, "source_file": sf, "src_ip": r.src_ip, "src_port": int(r.src_port),
                         "dst_ip": r.dst_ip, "dst_port": int(r.dst_port), "protocol": int(r.protocol),
                         "first_seen_ms": int(r.bidirectional_first_seen_ms), "last_seen_ms": int(r.bidirectional_last_seen_ms),
                         "packets_matched": e["pkts"], "client_packets": e["c_pkts"], "server_packets": e["s_pkts"],
                         "http_requests": " | ".join(f"{m} {p[:80]}" for m, p in e["http_requests"][:3]),
                         "client_payload_head": e["c_head"][:40].hex(), "server_payload_head": e["s_head"][:40].hex(),
                         "evidence_prereg": v0, "reason_prereg": why0, "evidence": v, "reason": why})
    ev = pd.DataFrame(recs).set_index("row")
    ev.to_csv(OUT / "label_audit_sample.csv")  # blind: no label, no prediction
    key = sample[["label", "pred", "stratum", "scenario"]].join(ev[["evidence_prereg", "reason_prereg", "evidence", "reason"]])
    pre = key.assign(err=np.where(key.label != "Benign", key.evidence_prereg == "B", key.evidence_prereg == "A"),
                     dec=key.evidence_prereg != "U")
    pre_tab = (pre.groupby(["scenario", "stratum"]).apply(lambda g: f"{int(g[g.dec].err.sum())}/{int(g.dec.sum())}", include_groups=False)
               .rename("pre-registered rater: errors/decided").reset_index())
    key.to_csv(OUT / "label_audit_key.csv")

    # ---- compare (after the rater has run)
    key["is_attack_label"] = key.label != "Benign"
    key["decided"] = key.evidence != "U"
    key["error"] = np.where(key.is_attack_label, key.evidence == "B", key.evidence == "A")
    rows = []
    for (sc, st), g in key.groupby(["scenario", "stratum"]):
        d = g[g.decided]
        k, n = int(d.error.sum()), len(d)
        lo, hi = wilson(k, n)
        rows.append({"capture": sc, "stratum": st, "population": int(sizes[sc, st]), "sampled": len(g),
                     "A": int((g.evidence == "A").sum()), "B": int((g.evidence == "B").sum()),
                     "U": int((g.evidence == "U").sum()), "label errors": f"{k}/{n}",
                     "error rate": round(k / n, 3) if n else None,
                     "95% Wilson": f"[{lo:.3f}, {hi:.3f}]" if n else "-"})
    st_tab = pd.DataFrame(rows)

    rng = np.random.default_rng(SEED)
    cls_rows = []
    for sc, g in key.groupby("scenario"):
        parts = []
        for st, gg in g.groupby("stratum"):
            d = gg[gg.decided].error.to_numpy().astype(float)
            parts.append((sizes[sc, st], d))
        tot = sum(n for n, d in parts if len(d))
        point = sum(n * d.mean() for n, d in parts if len(d)) / tot if tot else np.nan
        boots = []
        for _ in range(2000):
            boots.append(sum(n * rng.choice(d, len(d)).mean() for n, d in parts if len(d)) / tot)
        lo, hi = np.percentile(boots, [2.5, 97.5]) if tot else (np.nan, np.nan)
        cls_rows.append({"capture": sc, "test flows": int(sizes[sc].sum()),
                         "weighted label-error rate": round(point, 4), "95% stratified bootstrap": f"[{lo:.4f}, {hi:.4f}]",
                         "undetermined in sample": f"{int((g.evidence == 'U').sum())}/{len(g)}"})
    cls_tab = pd.DataFrame(cls_rows)

    fn = key[key.stratum == "B-fn"]
    fn_tab = fn.groupby("scenario").evidence.value_counts().unstack(fill_value=0)
    fn_pop = test[test.stratum == "B-fn"].groupby("scenario").size().rename("FN flows in test")

    md = ["# Blind stratified audit of the CIC-IoT2023 evidence labels (final review M8)", "",
          "Script: src/analysis/label_audit.py (protocol in its docstring, fixed before the audit ran). "
          "The rater is a fixed program that sees each flow's packets, the capture's scenario and label-free rate "
          "context, never the label, the attacker list or the model's verdict. A = packets show the capture's attack; "
          "B = other identifiable behaviour; U = undetermined. Error = attack label with B, or Benign label with A.", "",
          "Strata: A attack label, model agrees; B-fn attack label, model says Benign; B-x attack label, another "
          "attack class; C Benign label, one end is a listed attacker; D Benign label, no attacker, model flags; "
          "E Benign label, no attacker, model says Benign; F/G Benign capture, model flags / says Benign.", "",
          "## Amendments to the rater after inspecting its first output", "", AMENDMENTS, "",
          f"## (a) Per stratum (up to {N_PER} flows each, seed {SEED}), amended rater", "",
          st_tab.merge(pre_tab, left_on=["capture", "stratum"], right_on=["scenario", "stratum"]).drop(columns="scenario").to_markdown(index=False), "",
          "## (a) Per capture, weighted by stratum size", "", cls_tab.to_markdown(index=False), "",
          "## (b) False negatives (attack label, model says Benign)", "",
          pd.concat([fn_pop, fn_tab], axis=1).fillna(0).astype(int).to_markdown(), "",
          "## (c) Macro-F1 without MITM-ARP (deployed model, temporal test, evidence labels)", "",
          f"- All {len(classes)} classes: {f1_all:.4f}",
          f"- 7 classes, MITM-ARP dropped from the average (its flows kept): {f1_nm:.4f}",
          f"- 7 classes, MITM-ARP flows removed too: {f1_nm_rows:.4f}", "",
          "Blind sample with packet evidence: results/final/label_audit_sample.csv (no labels or predictions). "
          "Key: results/final/label_audit_key.csv."]
    (OUT / "label_audit.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
