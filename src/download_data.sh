#!/usr/bin/env bash
# Download the CIC-IoT2023 pcap subset (~5.1 GB) into data/raw/cic-iot2023/.
# Resumable: re-run after a broken connection.
# Usage: bash src/download_data.sh [small|all]
#   small = files under 250 MB only (~290 MB, for the first smoke test)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CIC="https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/PCAP"
MODE="${1:-small}"

SMALL=(
  "Recon-PortScan/Recon-PortScan.pcap"
  "DictionaryBruteForce/DictionaryBruteForce.pcap"
  "SqlInjection/SqlInjection.pcap"
  "XSS/XSS.pcap"
  "CommandInjection/CommandInjection.pcap"
)
LARGE=(
  "Benign_Final/BenignTraffic3.pcap"
  "DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap"
  "DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap"
  "MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap"
  "Mirai-udpplain/Mirai-udpplain24.pcap"
)

files=("${SMALL[@]}")
[[ "$MODE" == "all" ]] && files+=("${LARGE[@]}")

for f in "${files[@]}"; do
  out="$ROOT/data/raw/cic-iot2023/$f"
  mkdir -p "$(dirname "$out")"
  if [[ -f "$out" ]]; then echo "== skip (already complete) $f"; continue; fi
  echo ">> $f"
  # Download to .part and rename only when complete, so a finished file is never re-requested.
  # Connection resets (curl 56) are not retried by --retry, so loop and resume from .part.
  ok=0
  for attempt in $(seq 1 20); do
    if curl -sS -L --fail -C - --retry 5 --retry-all-errors --retry-delay 10 -o "$out.part" "$CIC/$f"; then
      ok=1; break
    fi
    echo "   attempt $attempt failed, resuming in 15 s"; sleep 15
  done
  if [[ $ok -ne 1 ]]; then echo "FAILED $f after 20 attempts"; exit 1; fi
  mv "$out.part" "$out"
  echo "   done $f ($(du -h "$out" | cut -f1))"
done

echo "Done. Files in $ROOT/data/raw/cic-iot2023"
