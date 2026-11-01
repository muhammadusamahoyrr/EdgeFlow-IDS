"""Offline flow extraction + labelling for CIC-IoT2023 pcaps.

Labelling rules, per attack folder in data/attackers.json:
  IP-based (default): a flow gets the file's class only if one end is a confirmed attacker IP
    and the other end is a victim: one of "victims" if listed, otherwise any LAN host
    (excluding the router and broadcast), and on one of "victim_ports" if listed.
  MAC-based ("attacker_macs", for ARP spoofing): a flow gets the class if its first packet was
    sent from or to the attacker's MAC while neither endpoint is the attacker's own IP, i.e. a
    victim's traffic relayed through the attacker.
Every other flow in an attack file is Benign. Flows from Benign_Final are all Benign.
Attack folders without a confirmed entry are skipped, never labelled by file name.

Large pcaps are read from data/raw/trimmed/<Folder>/<file> when present (src/trim_pcaps.sh).

Usage: python src/extract_flows.py [--max-flows N]
Output: data/processed/flows.parquet
"""
import argparse
import json

import pandas as pd
from nfstream import NFStreamer

from config import ATTACKERS_FILE, FOLDER_TO_CLASS, PROCESSED, RAW, STREAMER_KW

LAN_PREFIX = "192.168.137."
NOT_VICTIMS = ["192.168.137.1", "192.168.137.255"]


def is_victim(ip, victims=None):
    if victims:
        return ip.isin(victims)
    return ip.str.startswith(LAN_PREFIX) & ~ip.isin(NOT_VICTIMS)


def attack_mask(df, info):
    attackers = set(info.get("attackers", []))
    macs = [m.lower() for m in info.get("attacker_macs", [])]
    if macs:
        via_attacker = df["src_mac"].str.lower().isin(macs) | df["dst_mac"].str.lower().isin(macs)
        not_own = ~df["src_ip"].isin(attackers) & ~df["dst_ip"].isin(attackers)
        return via_attacker & not_own
    victims, ports = info.get("victims"), info.get("victim_ports")
    fwd = df["src_ip"].isin(attackers) & is_victim(df["dst_ip"], victims)
    rev = df["dst_ip"].isin(attackers) & is_victim(df["src_ip"], victims)
    if ports:
        fwd &= df["dst_port"].isin(ports)
        rev &= df["src_port"].isin(ports)
    return fwd | rev


def label_flows(df, cls, info):
    if cls == "Benign":
        df["label"] = "Benign"
        df["label_rule"] = "benign_file"
        return df
    hit = attack_mask(df, info)
    df["label"] = cls
    df.loc[~hit, "label"] = "Benign"
    df["label_rule"] = "attacker_mac" if info.get("attacker_macs") else "attacker_victim"
    return df


def source_for(pcap):
    trimmed = RAW / "trimmed" / pcap.parent.name / pcap.name
    return trimmed if trimmed.exists() else pcap


def main(max_flows):
    attackers = json.loads(ATTACKERS_FILE.read_text()) if ATTACKERS_FILE.exists() else {}
    parts = []
    for pcap in sorted((RAW / "cic-iot2023").rglob("*.pcap")):
        folder = pcap.parent.name
        cls = FOLDER_TO_CLASS.get(folder)
        if cls is None:
            continue
        if cls != "Benign" and folder not in attackers:
            print(f"SKIP {folder}/{pcap.name}: attackers not confirmed yet in {ATTACKERS_FILE.name}")
            continue
        src = source_for(pcap)
        df = NFStreamer(source=str(src), **STREAMER_KW).to_pandas()
        if max_flows and len(df) > max_flows:
            df = df.sample(max_flows, random_state=0)
        df = label_flows(df, cls, attackers.get(folder, {}))
        df["source_file"] = f"{folder}/{pcap.name}"
        tag = " (trimmed)" if src != pcap else ""
        print(f"{folder}/{pcap.name}{tag}: {len(df):,} flows -> {df['label'].value_counts().to_dict()}")
        parts.append(df)
    out = pd.concat(parts, ignore_index=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out.to_parquet(PROCESSED / "flows.parquet", index=False)
    print(f"\nSaved {len(out):,} flows to {PROCESSED / 'flows.parquet'}")
    print(out["label"].value_counts().to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-flows", type=int, default=0, help="cap flows per pcap (0 = no cap)")
    main(ap.parse_args().max_flows)
