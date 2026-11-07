#!/usr/bin/env bash
# CPU-budget factorial with the confounds removed (final review M7). Run as root in WSL.
# Same harness, same three heavy windows, tcpreplay/ping/gateway pinned to disjoint cores.
# Budgets interleaved (none, 1 core, 1/2 core) x 3 repeats so drift does not align with budget.
set -eo pipefail
cd "$(dirname "$0")"
filt() { grep -vE "$1" || true; }
exec > >(tee ../results/run_pinned.log) 2>&1
PY=/opt/edgeflow/bin/python
W="DDoS-SYN_Flood Mirai-udpplain DoS-HTTP_Flood"
echo "start $(date)"
$PY patch_nfstream.py
run() {
  local tag=$1; shift
  bash stop_live.sh > /dev/null 2>&1 || true
  rm -rf "../results/live/$tag"
  python3 ../topology/live_experiment.py --tag "$tag" --pin --only $W "$@" 2>&1 | filt "bogus"
  $PY eval_live.py --tag "$tag" 2>&1 | filt "Warning" | grep -E "Macro-F1|NFStream counters|^\| DDoS" || true
  echo "DONE $tag $(date)"
}
for r in 1 2 3; do
  run pin_none_r$r
  run pin_q100_r$r --cpu-quota 100
  run pin_q50_r$r --cpu-quota 50
done
echo "ALL_DONE $(date)"
