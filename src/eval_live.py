"""Compare the same unseen windows offline (NFStream on the pcap) vs live (gateway CSV).

Both sides are labelled with the same attackers.json rules and classified by the same model.
Live flows are assigned to a window by their start time (+-1 s around the replay). Management
flows (ping ticker) are never written by the gateway.

Reported per window: offered load (tcpreplay pps / Mbps), flows and packets offline vs live
("packet ratio" = packets in live flows / packets in offline flows; < 1 means packets were lost
before or inside the gateway), detection delays, ARP alerts, and gateway CPU / RSS.
Delays: "after flow end" = verdict time - flow's last packet (>= idle timeout, 15 s);
"first verdict per attacker pair" = first attack verdict for a pair - first packet of that pair.
Connections that a training flow was still part of after the train/test boundary are removed
from both sides (see train_edge_model.py); the count is reported per window.
Do not use this script for --enforce runs (blocking removes traffic): use eval_enforce.py.

Usage: python src/eval_live.py --tag run1
Output: results/live/<tag>/{live_vs_offline.json, live_vs_offline.md}
"""
import argparse
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from nfstream import NFStreamer
from sklearn.metrics import f1_score, precision_recall_fscore_support

from config import ATTACKERS_FILE, FOLDER_TO_CLASS, RAW, RESULTS, STREAMER_KW
from extract_flows import label_flows
from train_baseline import bootstrap_macro_f1


def macro(y, p, classes):
    return float(f1_score(y, p, labels=classes, average="macro", zero_division=0))


def per_class(y, p, classes):
    pr, rc, f1, sup = precision_recall_fscore_support(y, p, labels=classes, zero_division=0)
    return {c: {"precision": round(float(a), 3), "recall": round(float(b), 3),
                "f1": round(float(d), 3), "support": int(s)}
            for c, a, b, d, s in zip(classes, pr, rc, f1, sup)}


def in_window(df, w, col="bidirectional_first_seen_ms"):
    return df[(df[col] >= w["replay_start_ms"] - 1000) & (df[col] <= w["replay_end_ms"] + 1000)]


def drop_continuing(df, keys):
    """Remove connections that a training flow was still part of after the train/test boundary
    (matched on the 5-tuple in either direction). Returns (kept, n_removed)."""
    if df.empty or not keys:
        return df, 0
    both = set(map(tuple, keys)) | {(d, dp, s, sp, p) for s, sp, d, dp, p in keys}
    k = list(zip(df.src_ip, df.src_port.astype(int), df.dst_ip, df.dst_port.astype(int),
                 df.protocol.astype(int)))
    mask = np.array([t in both for t in k])
    return df[~mask], int(mask.sum())


def first_verdict_delay_s(lv):
    """Per attacker host pair: first attack verdict minus first packet of the pair."""
    att = lv[lv.label != "Benign"].copy()
    if att.empty:
        return None
    att["pair"] = [tuple(sorted(p)) for p in zip(att.src_ip, att.dst_ip)]
    first_pkt = att.groupby("pair").bidirectional_first_seen_ms.min()
    hits = att[att.pred != "Benign"]
    if hits.empty:
        return None
    first_hit = hits.groupby("pair").verdict_ms.min()
    d = (first_hit - first_pkt.loc[first_hit.index]) / 1000
    return round(float(d.median()), 1)


def main(tag):
    run = RESULTS / "live" / tag
    meta = json.loads((run / "windows.json").read_text())
    if meta.get("enforce"):
        raise SystemExit("enforce run: use eval_enforce.py (blocking removes traffic)")
    # Trusted input: the model file is produced locally by train_edge_model.py.
    model_path = Path(meta["model"])
    if not model_path.exists():  # results copied from another machine: use the local models folder
        model_path = RESULTS / "models" / model_path.name
    with open(model_path, "rb") as f:
        bundle = pickle.load(f)
    model, feats = bundle["model"], bundle["features"]
    attackers = json.loads(ATTACKERS_FILE.read_text())
    live = pd.read_csv(run / "flows.csv")
    res_use = pd.read_csv(run / "resources.csv")
    alerts_path = run / "arp_alerts.jsonl"
    alerts = pd.read_json(alerts_path, lines=True) if alerts_path.exists() and alerts_path.stat().st_size else pd.DataFrame(columns=["time_ms", "kind", "mac", "detail"])

    off_parts, live_parts, rows = [], [], []
    for w in meta["windows"]:
        folder = w["folder"]
        cls, info = FOLDER_TO_CLASS[folder], attackers.get(folder, {})
        off = NFStreamer(source=str(RAW / "live" / w["pcap"]), **STREAMER_KW).to_pandas()
        keys = bundle.get("continuing_connections", {}).get(w["source_file"], [])
        off, off_removed = drop_continuing(off, keys)
        off = label_flows(off.copy(), cls, info)
        off["pred"] = model.predict(off[feats].to_numpy(np.float32)) if len(off) else []
        lv, lv_removed = drop_continuing(in_window(live, w), keys)
        lv = label_flows(lv.copy(), cls, info)
        att = lv[lv.label != "Benign"]
        cpu = res_use[(res_use.time_ms >= w["replay_start_ms"]) & (res_use.time_ms <= w["replay_end_ms"])]
        al = alerts[(alerts.time_ms >= w["replay_start_ms"] - 1000) & (alerts.time_ms <= w["replay_end_ms"] + 1000)]
        off_pk, lv_pk = int(off.bidirectional_packets.sum()), int(lv.bidirectional_packets.sum())
        rows.append({
            "window": folder, "offered_pps": w.get("offered_pps"), "offered_mbps": w.get("offered_mbps"),
            "offline_flows": len(off), "live_flows": len(lv),
            "removed_training_connections_off_live": f"{off_removed}/{lv_removed}",
            "offline_packets": off_pk, "live_packets": lv_pk,
            "packet_ratio": round(lv_pk / off_pk, 4) if off_pk else None,
            "attack_flows_offline": int((off.label != "Benign").sum()), "attack_flows_live": len(att),
            "attack_recall_offline": round(float((off[off.label != "Benign"].pred != "Benign").mean()), 3) if (off.label != "Benign").any() else None,
            "attack_recall_live": round(float((att.pred != "Benign").mean()), 3) if len(att) else None,
            "benign_fpr_live": round(float((lv[lv.label == "Benign"].pred != "Benign").mean()), 4) if (lv.label == "Benign").any() else None,
            "median_verdict_after_flow_end_s": round(float(((lv.verdict_ms - lv.bidirectional_last_seen_ms) / 1000).median()), 1) if len(lv) else None,
            "first_verdict_per_attacker_pair_s": first_verdict_delay_s(lv),
            "arp_alerts": len(al),
            "cpu_percent_mean": round(float(cpu.cpu_percent.mean()), 1) if len(cpu) else None,
            "cpu_percent_max": round(float(cpu.cpu_percent.max()), 1) if len(cpu) else None,
            "rss_mb_max": round(float(cpu.rss_mb.max()), 1) if len(cpu) else None,
        })
        off_parts.append(off.assign(window=folder))
        live_parts.append(lv.assign(window=folder))

    off, lv = pd.concat(off_parts), pd.concat(live_parts)
    classes = sorted(set(off.label) | set(lv.label))
    batches = lv.drop_duplicates(["verdict_ms", "batch_ms"])
    nf_stats = {}
    for line in (run / "gateway.log").read_text().splitlines()[::-1]:
        if line.startswith("{") and "packets_processed" in line:
            nf_stats = json.loads(line)
            break
    res = {
        "model": meta["model"], "cpu_quota": meta.get("cpu_quota"), "speed": meta.get("speed"),
        "windows": rows,
        "offline": {"flows": len(off), "macro_f1": macro(off.label, off.pred, classes),
                    "macro_f1_ci95": bootstrap_macro_f1(off.label.to_numpy(), off.pred.to_numpy(), classes),
                    "per_class": per_class(off.label, off.pred, classes)},
        "live": {"flows": len(lv), "macro_f1": macro(lv.label, lv.pred, classes),
                 "macro_f1_ci95": bootstrap_macro_f1(lv.label.to_numpy(), lv.pred.to_numpy(), classes),
                 "per_class": per_class(lv.label, lv.pred, classes),
                 "batch_ms_p50": float(batches.batch_ms.median()),
                 "batch_ms_p95": float(batches.batch_ms.quantile(0.95)),
                 "batch_size_p50": float(batches.batch_size.median()),
                 "amortised_ms_per_flow": float((batches.batch_ms / batches.batch_size).median())},
        "arp_alerts": alerts.to_dict(orient="records"),
        "nfstream_counters": nf_stats,
    }
    (run / "live_vs_offline.json").write_text(json.dumps(res, indent=2, default=str))

    lo_o, hi_o = res["offline"]["macro_f1_ci95"]
    lo_l, hi_l = res["live"]["macro_f1_ci95"]
    md = [f"# Live vs offline on unseen windows ({tag})", "",
          f"Model `{meta['model'].split('/')[-1]}` · CPU quota {meta.get('cpu_quota') or 'none'} · replay speed x{meta.get('speed')}",
          f"Macro-F1 offline **{res['offline']['macro_f1']:.3f}** [{lo_o:.3f}, {hi_o:.3f}] vs live "
          f"**{res['live']['macro_f1']:.3f}** [{lo_l:.3f}, {hi_l:.3f}] ({len(off):,} / {len(lv):,} flows)",
          f"Inference: batch p50 {res['live']['batch_ms_p50']:.2f} ms (p95 {res['live']['batch_ms_p95']:.2f} ms), "
          f"median batch size {res['live']['batch_size_p50']:.0f}, amortised {res['live']['amortised_ms_per_flow']:.4f} ms/flow",
          f"NFStream counters (whole run): processed {nf_stats.get('packets_processed')}, "
          f"dropped by kernel {nf_stats.get('packets_dropped_filtered_by_kernel')}, ignored {nf_stats.get('packets_ignored')}", "",
          "| Window | Offered pps / Mbps | Flows off/live | Packet ratio | Attack flows off/live | "
          "Attack recall off/live | Benign FPR live | Verdict after flow end (s) | First verdict per attacker pair (s) | ARP alerts | CPU % mean/max | RSS MB |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['window']} | {r['offered_pps']} / {r['offered_mbps']} | {r['offline_flows']:,} / {r['live_flows']:,} | "
                  f"{r['packet_ratio']} | {r['attack_flows_offline']:,} / {r['attack_flows_live']:,} | "
                  f"{r['attack_recall_offline']} / {r['attack_recall_live']} | {r['benign_fpr_live']} | "
                  f"{r['median_verdict_after_flow_end_s']} | {r['first_verdict_per_attacker_pair_s']} | {r['arp_alerts']} | "
                  f"{r['cpu_percent_mean']} / {r['cpu_percent_max']} | {r['rss_mb_max']} |")
    md += ["", "| Class | Offline P / R / F1 (n) | Live P / R / F1 (n) |", "|---|---|---|"]
    for c in classes:
        o, l = res["offline"]["per_class"][c], res["live"]["per_class"][c]
        md.append(f"| {c} | {o['precision']} / {o['recall']} / {o['f1']} ({o['support']}) | "
                  f"{l['precision']} / {l['recall']} / {l['f1']} ({l['support']}) |")
    if len(alerts):
        md += ["", "ARP alerts:", ""] + [f"- {a['kind']} {a['mac']} {a['detail']}" for a in res["arp_alerts"]]
    (run / "live_vs_offline.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    main(ap.parse_args().tag)
