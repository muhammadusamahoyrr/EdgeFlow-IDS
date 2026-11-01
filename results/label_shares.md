# Attack vs background flows per pcap (labels from data/attackers.json)

| source_file                                    |   flows |   attack_flows |   background_flows |   background_share |
|:-----------------------------------------------|--------:|---------------:|-------------------:|-------------------:|
| Benign_Final/BenignTraffic3.pcap               |   46231 |              0 |              46231 |              1     |
| CommandInjection/CommandInjection.pcap         |    5639 |             98 |               5541 |              0.983 |
| DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap           |  511936 |         511527 |                409 |              0.001 |
| DictionaryBruteForce/DictionaryBruteForce.pcap |   11824 |           1080 |              10744 |              0.909 |
| DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap            |   51275 |          39484 |              11791 |              0.23  |
| MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap        |   12208 |            298 |              11910 |              0.976 |
| Mirai-udpplain/Mirai-udpplain24.pcap           |     653 |             41 |                612 |              0.937 |
| Recon-PortScan/Recon-PortScan.pcap             |  205065 |         143144 |              61921 |              0.302 |
| SqlInjection/SqlInjection.pcap                 |    7383 |            381 |               7002 |              0.948 |
| XSS/XSS.pcap                                   |    4992 |             77 |               4915 |              0.985 |

Large pcaps are trimmed to their first 1M packets (src/trim_pcaps.sh).
