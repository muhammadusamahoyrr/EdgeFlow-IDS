#!/usr/bin/env bash
# All sources sending to each flood victim across the whole trimmed file (catches late-joining attackers).
cd "$(dirname "$0")/../../data/raw/trimmed"
echo "=== DDoS-SYN: sources -> 192.168.137.245 port 4070"
tcpdump -nn -r DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap 'dst host 192.168.137.245 and dst port 4070' 2>/dev/null \
  | awk '{s=$3; sub(/\.[0-9]+$/,"",s); print s}' | sort | uniq -c | sort -rn
echo "=== DoS-HTTP: sources -> .71/.141 port 80"
tcpdump -nn -r DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap '(dst host 192.168.137.71 or dst host 192.168.137.141) and dst port 80' 2>/dev/null \
  | awk '{s=$3; sub(/\.[0-9]+$/,"",s); print s}' | sort | uniq -c | sort -rn | head
echo "=== Mirai: sources -> 192.168.137.191 (udp)"
tcpdump -nn -r Mirai-udpplain/Mirai-udpplain24.pcap 'udp and dst host 192.168.137.191' 2>/dev/null \
  | awk '{s=$3; sub(/\.[0-9]+$/,"",s); print s}' | sort | uniq -c | sort -rn | head -12
