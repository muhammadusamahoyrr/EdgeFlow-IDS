"""Settings shared by offline extraction and the live gateway, so features match."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"

# NFStream settings: identical offline and live.
STREAMER_KW = dict(
    idle_timeout=15,
    active_timeout=120,
    statistical_analysis=True,
    n_dissections=0,          # no nDPI application labels: keeps the feature set purely statistical
    accounting_mode=1,        # IP-level byte counts
)

# Columns never used as model inputs: identifiers, addresses, timestamps (label leakage, Arp et al. 2022).
ID_COLUMNS = {
    "id", "expiration_id", "src_ip", "src_mac", "src_oui", "src_port",
    "dst_ip", "dst_mac", "dst_oui", "dst_port", "protocol", "ip_version",
    "vlan_id", "tunnel_id",
    "bidirectional_first_seen_ms", "bidirectional_last_seen_ms",
    "src2dst_first_seen_ms", "src2dst_last_seen_ms",
    "dst2src_first_seen_ms", "dst2src_last_seen_ms",
    # bookkeeping added by extract_flows.py (would leak the label)
    "label", "label_rule", "source_file",
}

# File (CIC-IoT2023 folder) -> our merged class.
FOLDER_TO_CLASS = {
    "Benign_Final": "Benign",
    "DDoS-SYN_Flood": "DDoS-SYN",
    "DoS-HTTP_Flood": "DoS-HTTP",
    "Recon-PortScan": "Recon",
    "MITM-ArpSpoofing": "MITM-ARP",
    "DictionaryBruteForce": "BruteForce",
    "SqlInjection": "Web",
    "XSS": "Web",
    "CommandInjection": "Web",
    "Mirai-udpplain": "Mirai",
}

ATTACKERS_FILE = ROOT / "data" / "attackers.json"

# Size-limited decision tree used for the edge model and NSGA-II: a fully grown tree's node count
# mostly tracks label noise and training-set size, not feature choice. The limits are chosen on
# validation data by src/tune_edge_tree.py (results/edge_tree.json); this is the fallback.
EDGE_TREE = dict(max_depth=16, min_samples_leaf=10, class_weight="balanced", random_state=0)
_tuned = RESULTS / "edge_tree.json"
if _tuned.exists():
    import json as _json
    EDGE_TREE = _json.loads(_tuned.read_text())

# Management subnet of the emulated testbed (ping ticker): never scored or blocked.
MGMT_PREFIX = "10.0."


def feature_columns(df):
    """Numeric model inputs: everything except identifiers, string fields and constant columns."""
    return [c for c in df.columns
            if c not in ID_COLUMNS
            and pd.api.types.is_numeric_dtype(df[c])
            and df[c].nunique() > 1]
