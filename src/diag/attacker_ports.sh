#!/usr/bin/env bash
# Destination ports used by one attacker IP in the first N packets.
# Usage: bash attacker_ports.sh <pcap> <attacker_ip> [N]
tcpdump -nn -r "$1" -c "${3:-100000}" "src host $2" 2>/dev/null \
  | awk '{print $5}' | sed -E 's/^([0-9]+\.){4}//; s/:$//' | sort | uniq -c | sort -rn | head -5
