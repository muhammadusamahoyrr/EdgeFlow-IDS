"""Blocking details for review round 6 (extends results/blocking_accounting.md; no new experiments).

(a) Definition of an "eligible" benign host-pair window, as computed in blocking_accounting.py
    (denominators()): per run and per replay window, the flows are the run's own live flows.csv
    rows with eval_live.in_window; a host pair is the unordered (src_ip, dst_ip) pair; a pair is
    an attacker pair if >= 1 of its flows in that window is labelled as attack
    (extract_flows.label_flows + data/attackers.json); every other pair seen in the window is an
    eligible benign pair. Counts are summed over the ten windows (host-pair-windows: a pair seen
    in two windows counts twice).
(b) Why 1,674 (enforce_k1) vs 1,675 (enforce_policy): per-window comparison of the two runs'
    pair sets; the pairs present in only one run and their flows.
(c) The window of each MITM-ARP-triggered false block of enforce_k1, with the host roles.
(d) Run-1 simulation (block_curve.py): per attack class, the attack flows, the attack flows that
    start after their pair was blocked, and attacker pairs blocked, at every k; the class shares
    behind the constant 0.111 share of attack flows after block.

Usage: python src/analysis/blocking_r6.py
Output: results/blocking_accounting_r6.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import pandas as pd  # noqa: E402

from analysis.block_curve import KS, simulate  # noqa: E402
from analysis.blocking_accounting import enforced, windows  # noqa: E402
from config import RESULTS  # noqa: E402


def eligible_table(tags):
    rows = []
    per = {}
    for tag in tags:
        per[tag] = {}
        for folder, d in windows(tag):
            att = set(d[d.label != "Benign"].pair)
            pairs = set(d.pair)
            per[tag][folder] = (pairs, att, d)
            rows.append({"run": tag, "window": folder, "flows": len(d), "host pairs": len(pairs),
                         "attacker pairs": len(att), "eligible benign pairs": len(pairs - att)})
    return pd.DataFrame(rows), per


def diff_pairs(per, a, b):
    rows = []
    for folder in per[a]:
        pa, atta, da = per[a][folder]
        pb, attb, db = per[b][folder]
        for tag, only, d, att in ((a, pa - pb, da, atta), (b, pb - pa, db, attb)):
            for p in sorted(only):
                f = d[d.pair == p]
                rows.append({"window": folder, "only in run": tag, "pair": f"{p[0]} - {p[1]}",
                             "attacker pair": p in att, "flows": len(f),
                             "dst ports": ", ".join(str(int(x)) for x in sorted(set(f.dst_port))),
                             "protocols": ", ".join(str(int(x)) for x in sorted(set(f.protocol))),
                             "packets": int(f.bidirectional_packets.sum()) if "bidirectional_packets" in f else None,
                             "verdicts": ", ".join(sorted(set(f.pred)))})
    return pd.DataFrame(rows)


def rs_sources(tags=("run1", "run1_r2", "run1_r3", "edge100", "enforce_k1", "enforce_policy")):
    """IPv6 link-local sources sending to ff02::2 (all-routers) in each run's whole live flow log."""
    srcs = {}
    for tag in tags:
        live = pd.read_csv(RESULTS / "live" / tag / "flows.csv", usecols=["src_ip", "dst_ip"])
        srcs[tag] = set(live[(live.dst_ip == "ff02::2") & live.src_ip.str.startswith("fe80:")].src_ip)
    common = set.intersection(*srcs.values())
    rows = [{"run": t, "link-local sources to ff02::2": len(s), "in every run": len(s & common),
             "run-specific": ", ".join(sorted(s - common))} for t, s in srcs.items()]
    return pd.DataFrame(rows)


def per_class_after(tag="run1"):
    ws = windows(tag)
    rows = []
    for ignore in (False, True):
        for k in KS:
            stats, total_att, total_after = {}, 0, 0
            for folder, d in ws:
                blocked = simulate(d, k, ignore)
                att = d[d.label != "Benign"]
                pair_cls = att.groupby("pair").label.first().to_dict()
                for c, g in att.groupby("label"):
                    after = sum(1 for p, s in zip(g.pair, g.bidirectional_first_seen_ms)
                                if p in blocked and s > blocked[p])
                    pairs = set(g.pair)
                    s = stats.setdefault(c, [0, 0, 0, 0])
                    s[0] += len(g)
                    s[1] += after
                    s[2] += sum(1 for p in pairs if pair_cls[p] == c)
                    s[3] += sum(1 for p in pairs if pair_cls[p] == c and p in blocked)
                    total_att += len(g)
                    total_after += after
            for c, (n, after, npairs, nblk) in sorted(stats.items()):
                rows.append({"k": k, "MITM-ARP ignored": ignore, "class": c, "attack flows": n,
                             "share of attack flows": round(n / total_att, 4),
                             "flows after block": after,
                             "class share after block": round(after / n, 4) if n else None,
                             "contribution to overall share": round(after / total_att, 4),
                             "attacker pairs blocked": f"{nblk}/{npairs}"})
            rows.append({"k": k, "MITM-ARP ignored": ignore, "class": "ALL", "attack flows": total_att,
                         "share of attack flows": 1.0, "flows after block": total_after,
                         "class share after block": round(total_after / total_att, 4),
                         "contribution to overall share": round(total_after / total_att, 4),
                         "attacker pairs blocked": ""})
            print(rows[-1])
    return pd.DataFrame(rows)


def main():
    tags = ("run1", "enforce_k1", "enforce_policy")
    elig, per = eligible_table(tags)
    tot = elig.groupby("run")[["flows", "host pairs", "attacker pairs", "eligible benign pairs"]].sum()
    wide = elig.pivot(index="window", columns="run", values="eligible benign pairs")
    wide["k1 - policy"] = wide["enforce_k1"] - wide["enforce_policy"]
    diff = diff_pairs(per, "enforce_k1", "enforce_policy")

    _, det, _ = enforced("enforce_k1")
    mitm = det[det["trigger verdict"] == "MITM-ARP"]
    mitm_by_window = mitm.groupby("window").size().rename("MITM-ARP-triggered false blocks")
    curve = per_class_after()
    rs = rs_sources()
    c1 = curve[(curve.k == 1) & (~curve["MITM-ARP ignored"])].set_index("class")

    md = ["# Blocking details, review round 6 (extends results/blocking_accounting.md)", "",
          "## (a) Definition of an eligible benign host-pair window", "",
          "Computed as in src/analysis/blocking_accounting.py (denominators()). For each run and each of the ten "
          "replay windows: the flows are that run's own live flow records (results/live/<run>/flows.csv) whose "
          "first-seen time lies in the window's replay interval +-1 s (eval_live.in_window); a host pair is the "
          "unordered pair of IP addresses of a flow; a pair is an attacker pair if at least one of its flows in "
          "that window is labelled as attack (extract_flows.label_flows with data/attackers.json); every other "
          "pair seen in the window is an eligible benign pair, i.e. one that can only be blocked falsely. Counts "
          "are per window and summed over windows (a pair seen in two windows counts twice); blocks reset "
          "between windows.", "",
          "Totals per run:", "", tot.to_markdown(), "",
          "Per window:", "", wide.to_markdown(), "",
          "## (b) Why 1,674 (enforce_k1) and 1,675 (enforce_policy)", "",
          "Each enforced run is a separate replay with its own live flow export, so the set of host pairs that "
          "appear in a window can differ by a pair or two between runs. Pairs present in a window of one run "
          "but not the other:", "",
          diff.to_markdown(index=False) if len(diff) else "(none)", "",
          "All differing pairs are IPv6 link-local sources sending ICMPv6 (protocol 58) to ff02::2 (all-routers). "
          "Link-local sources to ff02::2 in each run's whole live flow log (results/live/<run>/flows.csv):", "",
          rs.to_markdown(index=False), "",
          "The run-specific addresses change from run to run, unlike the addresses from the replayed captures, "
          "so they are not in the pcaps; whether such a pair falls in a window (and in which) differs per run.", "",
          "## (c) Window of each MITM-ARP-triggered false block (enforce_k1)", "",
          mitm_by_window.to_frame().to_markdown(), "",
          f"Total: {len(mitm)}; in the MITM-ArpSpoofing window: {int((mitm.window == 'MITM-ArpSpoofing').sum())}; "
          f"in other windows: {int((mitm.window != 'MITM-ArpSpoofing').sum())}. Roles: "
          + ", ".join(f"{r} {n}" for r, n in mitm.role.value_counts().items()) + ".", "",
          mitm.to_markdown(index=False), "",
          "## (d) Per-class basis of the share of attack flows after block (run1 simulation)", "",
          "Attack flows = live flows labelled as attack in the ten windows; after block = the flow starts "
          "(bidirectional_first_seen_ms) after its pair was blocked (block_curve.py). Contribution = class "
          "flows after block / all attack flows; contributions sum to the overall share.", "",
          curve.to_markdown(index=False), "",
          f"Summary (k = 1, MITM-ARP counted): DDoS-SYN is {c1.loc['DDoS-SYN', 'share of attack flows']:.4f} of "
          f"{int(c1.loc['ALL', 'attack flows']):,} attack flows; {c1.loc['DDoS-SYN', 'class share after block']:.4f} "
          f"of its flows start after block, contributing {c1.loc['DDoS-SYN', 'contribution to overall share']:.4f} "
          f"of the overall {c1.loc['ALL', 'class share after block']:.4f}; DoS-HTTP contributes "
          f"{c1.loc['DoS-HTTP', 'contribution to overall share']:.4f}. The six DDoS-SYN pairs are blocked at every k "
          "(column 'attacker pairs blocked'), so the overall share hardly changes with k.", ""]
    (RESULTS / "blocking_accounting_r6.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
