#!/usr/bin/env bash
# Stop any running live pipeline cleanly (run as root in WSL).
pkill -f live_experiment.py
sleep 2
# Patterns are specific: Mininet hosts share the PID namespace with the rest of the machine.
pkill -f src/gateway.py; pkill -f src/arp_watch.py; pkill -f "tcpreplay -i h1-eth0"
pkill -f "ping -i 0.005 -q 10.0.2.10"
sleep 5   # let a stopping gateway finish moving its CSV before temp files are removed
mn -c > /dev/null 2>&1
rm -f /tmp/edgeflow_gateway_*.csv
echo "stopped"
