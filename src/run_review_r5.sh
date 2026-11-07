#!/bin/bash
# Reviewer-requested analyses (new result files only). Run: wsl bash /mnt/d/EdgeFlow-IDS/src/run_review_r5.sh [names...]
cd /mnt/d/EdgeFlow-IDS/src
PY=/opt/edgeflow/bin/python
LOG=../results/review_r5.log
run() { echo "== $1 start $(date)" >> $LOG; $PY "$1" >> $LOG 2>&1; echo "== $1 exit $? $(date)" >> $LOG; }
for s in "${@:-analysis/blocking_accounting.py analysis/paired_diff.py iot23/fpr_per_capture.py iot23/common_class_ci.py iot23/zeek_agreement.py}"; do
  for x in $s; do run "$x"; done
done
echo "ALL_DONE $(date)" >> $LOG
