#!/usr/bin/env bash
# Paper-revision analyses on existing results (no new live runs). Run as root in WSL.
set -eo pipefail
cd "$(dirname "$0")/.."
filt() { grep -vE "$1" || true; }
exec > >(tee ../results/run_analyses.log) 2>&1
PY=/opt/edgeflow/bin/python
echo "start $(date)"
$PY analysis/file_label_baseline.py 2>&1 | filt "Warning"
$PY analysis/cluster_ci.py 2>&1 | filt "Warning"
$PY analysis/block_curve.py --tag run1 2>&1 | filt "Warning"
$PY analysis/match_live_offline.py --tag run1 2>&1 | filt "Warning"
echo "ALL_DONE $(date)"
