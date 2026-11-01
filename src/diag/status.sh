#!/usr/bin/env bash
# Show project processes running in WSL and kill any stray live tshark capture (no -r).
ps -eo pid,etime,args | grep -E "edgeflow|tshark|tcpreplay|mininet|live_experiment|run_live|run_all" | grep -v grep | cut -c1-160
for p in $(pgrep -x tshark); do
  if ! tr '\0' ' ' < /proc/$p/cmdline | grep -q -- " -r "; then kill "$p" && echo "killed stray live tshark $p"; fi
done
