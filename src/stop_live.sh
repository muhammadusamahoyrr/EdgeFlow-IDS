#!/usr/bin/env bash
# Stop any running live pipeline cleanly (run as root in WSL).
pkill -f live_experiment.py
sleep 2
pkill -f src/gateway.py; pkill -f tcpreplay; pkill -f "ping -i"
mn -c > /dev/null 2>&1
rm -f /tmp/edgeflow_gateway_*.csv
echo "stopped"
