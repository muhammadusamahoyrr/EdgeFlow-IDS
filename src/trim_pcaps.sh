#!/usr/bin/env bash
# Keep the first N packets of each large pcap (> 300 MB) in data/raw/trimmed/<Folder>/<file>,
# so NFStream extraction stays fast. Originals are untouched.
# Usage: bash trim_pcaps.sh [N]   (default 1,000,000)
set -e
cd "$(dirname "$0")/../data/raw"
N="${1:-1000000}"
find cic-iot2023 -name '*.pcap' -size +300M | while read -r f; do
  out="trimmed/${f#cic-iot2023/}"
  if [[ -f "$out" ]]; then echo "skip $out"; continue; fi
  mkdir -p "$(dirname "$out")"
  tcpdump -r "$f" -c "$N" -w "$out.tmp" 2>/dev/null && mv "$out.tmp" "$out"
  echo "trimmed $f -> $out ($(du -h "$out" | cut -f1))"
done
