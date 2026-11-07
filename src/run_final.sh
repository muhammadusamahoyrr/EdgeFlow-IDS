#!/bin/bash
# Final-review analyses (new result files in results/final/ only).
# Run: wsl -d Ubuntu-24.04 -u root bash /mnt/d/EdgeFlow-IDS/src/run_final.sh [scripts...]
cd /mnt/d/EdgeFlow-IDS/src
PY=/opt/edgeflow/bin/python
LOG=../results/final.log
mkdir -p ../results/final
run() { echo "== $1 start $(date)" >> $LOG; $PY "$1" >> $LOG 2>&1; echo "== $1 exit $? $(date)" >> $LOG; }
DEFAULT="analysis/final_gap.py analysis/final_sign_test.py analysis/final_blocking_rates.py analysis/final_filelabel.py analysis/final_fidelity.py"
for x in ${@:-$DEFAULT}; do run "$x"; done
echo "ALL_DONE $(date)" >> $LOG
