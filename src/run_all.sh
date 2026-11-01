#!/usr/bin/env bash
# Offline data pipeline: trim large pcaps -> extract + label flows (models: run_offline2.sh).
# Run in WSL as root. Log: results/run_all.log
set -eo pipefail
cd "$(dirname "$0")"
filt() { grep -vE "$1" || true; }  # drop noisy lines; never fail on empty output
LOG=../results/run_all.log
exec > >(tee "$LOG") 2>&1
echo "start $(date)"
bash trim_pcaps.sh 1000000
/opt/edgeflow/bin/python extract_flows.py 2>&1 | filt "Warning"
echo "ALL_DONE $(date)"
