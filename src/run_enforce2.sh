#!/usr/bin/env bash
# Tune the blocking policy on validation data, then a live enforce run with that policy.
set -eo pipefail
cd "$(dirname "$0")"
filt() { grep -vE "$1" || true; }  # drop noisy lines; never fail on empty output
exec > >(tee ../results/run_enforce2.log) 2>&1
PY=/opt/edgeflow/bin/python
$PY tune_block_policy.py 2>&1 | filt "Warning"
bash stop_live.sh > /dev/null 2>&1 || true
rm -rf ../results/live/enforce_policy
python3 ../topology/live_experiment.py --tag enforce_policy --enforce 2>&1 | filt "bogus"
grep "blocking policy" ../results/live/enforce_policy/gateway.log
$PY eval_enforce.py --tag enforce_policy 2>&1 | filt "Warning"
echo "ALL_DONE $(date)"
