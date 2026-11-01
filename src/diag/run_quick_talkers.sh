#!/usr/bin/env bash
# Run quick_talkers on the remaining large pcaps + ARP evidence for MITM.
cd "$(dirname "$0")"
D=../../data/raw/cic-iot2023
for f in DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap Mirai-udpplain/Mirai-udpplain24.pcap MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap; do
  bash ./quick_talkers.sh "$D/$f" 300000
done
M="$D/MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap"
echo "=== MITM: ARP replies (count, sender MAC, claimed IP), first 300000 packets"
tcpdump -nn -e -r "$M" -c 300000 arp 2>/dev/null | grep -i "is-at" \
  | awk '{for(i=1;i<=NF;i++){if($i=="Reply"){ip=$(i+1)}} print $2, ip}' | sort | uniq -c | sort -rn | head -12
echo "=== MACs claiming more than one IP"
tcpdump -nn -e -r "$M" -c 300000 arp 2>/dev/null | grep -i "is-at" \
  | awk '{for(i=1;i<=NF;i++){if($i=="Reply"){ip=$(i+1)}} print $2, ip}' | sort -u \
  | awk '{n[$1]++; ips[$1]=ips[$1]" "$2} END {for (m in n) if (n[m]>1) print m, n[m], ips[m]}'
