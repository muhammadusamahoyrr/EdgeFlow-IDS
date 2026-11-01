#!/usr/bin/env bash
# Final live runs. Run in WSL as root. Log: results/run_live3.log
#  run1     all windows, all-feature model, no CPU limit
#  edge100  all windows, gateway limited to one CPU core (cgroup quota 100%)
#  edge50   the three heaviest windows, half a core (quota 50%)
#  enforce_k1  all windows, block on the first attack verdict (scored by eval_enforce.py)
cd "$(dirname "$0")"
filt() { grep -vE "$1" || true; }  # drop noisy lines; never fail on empty output
exec > >(tee ../results/run_live3.log) 2>&1
PY=/opt/edgeflow/bin/python
echo "start $(date)"
$PY patch_nfstream.py
run() {  # tag, extra args...
  local tag=$1; shift
  bash stop_live.sh > /dev/null 2>&1 || true
  rm -rf "../results/live/$tag"
  python3 ../topology/live_experiment.py --tag "$tag" "$@" 2>&1 | filt "bogus"
  if [[ " $* " == *" --enforce "* ]]; then
    $PY eval_enforce.py --tag "$tag" 2>&1 | filt "Warning"
  else
    $PY eval_live.py --tag "$tag" 2>&1 | filt "Warning"
  fi
  echo "DONE $tag $(date)"
}
run run1
run edge100 --cpu-quota 100
run edge50 --cpu-quota 50 --only DDoS-SYN_Flood Mirai-udpplain DoS-HTTP_Flood
run enforce_k1 --enforce --policy none
echo "ALL_DONE $(date)"
