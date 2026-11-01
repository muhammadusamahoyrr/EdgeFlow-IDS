#!/usr/bin/env bash
# Re-run the runs affected by the final review (per-window reset, per-capture policy tuning,
# gateway readiness): blocking policy, enforce_k1, enforce_policy, edge50. Run as root in WSL.
set -eo pipefail
cd "$(dirname "$0")"
filt() { grep -vE "$1" || true; }
exec > >(tee ../results/run_final_live.log) 2>&1
PY=/opt/edgeflow/bin/python
echo "start $(date)"
$PY patch_nfstream.py
$PY tune_block_policy.py 2>&1 | filt "Warning"
run() {  # tag, args...
  local tag=$1; shift
  bash stop_live.sh > /dev/null 2>&1 || true
  rm -rf "../results/live/$tag"
  python3 ../topology/live_experiment.py --tag "$tag" "$@" 2>&1 | filt "bogus"
  if [[ " $* " == *" --enforce "* ]]; then $PY eval_enforce.py --tag "$tag" 2>&1 | filt "Warning"
  else $PY eval_live.py --tag "$tag" 2>&1 | filt "Warning"; fi
  echo "DONE $tag $(date)"
}
run enforce_k1 --enforce --policy none
run enforce_policy --enforce
run edge50 --cpu-quota 50 --only DDoS-SYN_Flood Mirai-udpplain DoS-HTTP_Flood
echo "ALL_DONE $(date)"
