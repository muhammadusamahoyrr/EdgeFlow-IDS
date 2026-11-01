#!/usr/bin/env bash
# Show HTTP requests to LAN hosts in the web-attack pcaps (confirms attacker IPs).
cd "$(dirname "$0")/../../data/raw/cic-iot2023"
for f in SqlInjection/SqlInjection.pcap XSS/XSS.pcap CommandInjection/CommandInjection.pcap; do
  echo "== $f"
  tshark -r "$f" -Y 'http.request && ip.dst==192.168.137.0/24' -T fields -e ip.src -e ip.dst -e http.request.uri 2>/dev/null \
    | awk -F'\t' '{print $1, $2, substr($3,1,100)}' | sort | uniq -c | sort -rn | head -6
  echo "-- requests per source:"
  tshark -r "$f" -Y 'http.request && ip.dst==192.168.137.0/24' -T fields -e ip.src 2>/dev/null | sort | uniq -c | sort -rn | head -4
done
