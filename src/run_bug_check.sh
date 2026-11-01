#!/usr/bin/env bash
# Measure the NFStream LRU bug: same two live windows with the original and the patched NFStream.
# Run in WSL as root. Output: results/nfstream_bug_check.md (the patch is re-applied at the end).
cd "$(dirname "$0")"
filt() { grep -vE "$1" || true; }  # drop noisy lines; never fail on empty output
PY=/opt/edgeflow/bin/python
trap '$PY patch_nfstream.py > /dev/null' EXIT   # always leave NFStream patched
for mode in unpatched patched; do
  if [[ $mode == unpatched ]]; then $PY patch_nfstream.py --revert; else $PY patch_nfstream.py; fi
  bash stop_live.sh > /dev/null 2>&1 || true
  rm -rf "../results/live/bugcheck_$mode"
  python3 ../topology/live_experiment.py --tag "bugcheck_$mode" --only SqlInjection XSS 2>&1 | filt "bogus"
  $PY eval_live.py --tag "bugcheck_$mode" | filt "Warning|^\|"
done
$PY patch_nfstream.py
$PY - <<'PYEOF'
import json
from pathlib import Path
R = Path("../results")
rows = []
for mode in ("unpatched", "patched"):
    j = json.loads((R / "live" / f"bugcheck_{mode}" / "live_vs_offline.json").read_text())
    for w in j["windows"]:
        rows.append(f"| {mode} | {w['window']} | {w['median_verdict_after_flow_end_s']} | {w['packet_ratio']} | {w['live_flows']} / {w['offline_flows']} |")
md = ["# NFStream 6.6.0 idle-expiry bug: before and after the patch",
      "", "Same two live windows (SQLi, XSS), idle_timeout 15 s, 200 packet/s ping ticker running throughout.",
      "", "| NFStream | Window | Median verdict after flow end (s) | Packet ratio live/offline | Flows live / offline |",
      "|---|---|---|---|---|", *rows]
(R / "nfstream_bug_check.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
PYEOF
