#!/usr/bin/env bash
# Fast attacker discovery: count IP src->dst pairs in the first N packets (tcpdump, no flow building).
# Usage: bash quick_talkers.sh <pcap> [N]
f="$1"; n="${2:-500000}"
echo "=== $(basename "$f") (first $n packets)"
start=$(date +%s)
tcpdump -nn -r "$f" -c "$n" ip 2>/dev/null \
  | awk '{s=$3; d=$5; sub(/\.[0-9]+$/,"",s); sub(/\.[0-9]+:?$/,"",d); sub(/:$/,"",d); print s" -> "d}' \
  | sort | uniq -c | sort -rn | head -12
echo "distinct sources: $(tcpdump -nn -r "$f" -c "$n" ip 2>/dev/null | awk '{s=$3; sub(/\.[0-9]+$/,"",s); print s}' | sort -u | wc -l)"
echo "took $(( $(date +%s) - start )) s"
