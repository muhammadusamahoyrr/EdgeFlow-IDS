#!/bin/bash
# Review round 6 analyses (new result files only). Run: wsl -d Ubuntu-24.04 -u root bash /mnt/d/EdgeFlow-IDS/src/run_review_r6.sh [names...]
cd /mnt/d/EdgeFlow-IDS/src
PY=/opt/edgeflow/bin/python
LOG=../results/review_r6.log
run() { echo "== $1 start $(date)" >> $LOG; $PY "$1" >> $LOG 2>&1; echo "== $1 exit $? $(date)" >> $LOG; }
for s in "${@:-analysis/perclass_counts.py analysis/blocking_r6.py iot23/spanning_common.py}"; do
  for x in $s; do run "$x"; done
done
echo "ALL_DONE $(date)" >> $LOG
