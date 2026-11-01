#!/usr/bin/env bash
# Re-run all offline results after the review fixes. Run in WSL as root. Log: results/run_offline2.log
set -eo pipefail
cd "$(dirname "$0")"
filt() { grep -vE "$1" || true; }  # drop noisy lines; never fail on empty output
exec > >(tee ../results/run_offline2.log) 2>&1
PY=/opt/edgeflow/bin/python
echo "start $(date)"
echo "=== MITM: MACs claiming more than one IP in ARP replies (whole trimmed file)"
tcpdump -nn -e -r ../data/raw/trimmed/MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap arp 2>/dev/null | grep -i "is-at" \
  | awk '{for(i=1;i<=NF;i++){if($i=="Reply"){ip=$(i+1)}} print $2, ip}' | sort -u \
  | awk '{n[$1]++; ips[$1]=ips[$1]" "$2} END {for (m in n) if (n[m]>1) print m, n[m], ips[m]}' || true
$PY tune_edge_tree.py 2>&1 | filt "Warning|^{"
for s in temporal stratified; do
  echo "########## split: $s"
  $PY train_baseline.py --split "$s" 2>&1 | filt "Warning|^\s*$"
done
$PY nsga_select.py --pop 40 --gen 30 --per-class 5000 2>&1 | filt "Warning|DeprecationWarning|^\s+[0-9]+ \|"
$PY train_edge_model.py --features all
$PY train_edge_model.py --features nsga
rm -rf ../data/raw/live
$PY make_live_windows.py --seconds 60 2>&1 | filt "Warning|bogus"
echo "ALL_DONE $(date)"
