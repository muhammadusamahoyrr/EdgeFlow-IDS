#!/usr/bin/env bash
# Full offline pipeline: trim large pcaps -> extract + label flows -> baselines (both splits).
# Run in WSL as root. Log: results/run_all.log
set -e
cd "$(dirname "$0")"
LOG=../results/run_all.log
exec > >(tee "$LOG") 2>&1
echo "start $(date)"
bash trim_pcaps.sh 1000000
/opt/edgeflow/bin/python extract_flows.py 2>&1 | grep -v Warning
for s in temporal stratified; do
  echo "########## split: $s"
  /opt/edgeflow/bin/python train_baseline.py --split "$s"
done
echo "ALL_DONE $(date)"
