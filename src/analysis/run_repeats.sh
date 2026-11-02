#!/usr/bin/env bash
# Repeat the live detection runs for run-to-run variation (paper revision, reviewer item M2).
# Two more no-limit runs and two more half-core runs with the final harness. Run as root in WSL.
set -eo pipefail
cd "$(dirname "$0")/.."
filt() { grep -vE "$1" || true; }
exec > >(tee ../results/run_repeats.log) 2>&1
PY=/opt/edgeflow/bin/python
echo "start $(date)"
$PY patch_nfstream.py
run() {
  local tag=$1; shift
  bash stop_live.sh > /dev/null 2>&1 || true
  rm -rf "../results/live/$tag"
  python3 ../topology/live_experiment.py --tag "$tag" "$@" 2>&1 | filt "bogus"
  $PY eval_live.py --tag "$tag" 2>&1 | filt "Warning" | grep -E "Macro-F1|NFStream counters|^\| DDoS" || true
  echo "DONE $tag $(date)"
}
run run1_r2
run run1_r3
run edge50_r2 --cpu-quota 50 --only DDoS-SYN_Flood Mirai-udpplain DoS-HTTP_Flood
run edge50_r3 --cpu-quota 50 --only DDoS-SYN_Flood Mirai-udpplain DoS-HTTP_Flood
echo "ALL_DONE $(date)"
