#!/usr/bin/env bash
# Top talkers + ARP evidence for the large attack pcaps. Run in WSL as root. Output: results/attackers_large.log
cd "$(dirname "$0")"
D=../../data/raw/cic-iot2023
OUT=../../results/attackers_large.log
: > "$OUT"
for f in DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap Mirai-udpplain/Mirai-udpplain24.pcap MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap; do
  /opt/edgeflow/bin/python "$(dirname "$0")/find_attackers.py" "$D/$f" 2>&1 | grep -v Warning >> "$OUT"
done
echo -e "\n=== MITM ARP replies: sender MAC -> claimed IPs" >> "$OUT"
tshark -r "$D/MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap" -Y "arp.opcode==2" -T fields -e eth.src -e arp.src.proto_ipv4 2>/dev/null \
  | sort | uniq -c | sort -rn | head -15 >> "$OUT"
echo -e "\n=== MACs claiming more than one IP" >> "$OUT"
tshark -r "$D/MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap" -Y "arp.opcode==2" -T fields -e eth.src -e arp.src.proto_ipv4 2>/dev/null \
  | sort -u | awk '{n[$1]++; ips[$1]=ips[$1]" "$2} END {for (m in n) if (n[m]>1) print m, n[m], ips[m]}' >> "$OUT"
echo "ALL_DONE" >> "$OUT"
