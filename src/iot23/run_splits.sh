#!/bin/bash
# Run the IoT-23 split analysis; output to results/iot23/splits.log.
cd /mnt/d/EdgeFlow-IDS/src && /opt/edgeflow/bin/python iot23/splits.py > ../results/iot23/splits.log 2>&1
echo "exit $?" >> ../results/iot23/splits.log
