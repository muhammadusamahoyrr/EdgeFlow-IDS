# ARP watcher per live window (fresh state per window)

| Window | High alerts | Info alerts | First high alert (s into window) | High alert detail |
|---|---|---|---|---|
| Benign_Final | 0 | 0 | - |  |
| CommandInjection | 0 | 0 | - |  |
| DDoS-SYN_Flood | 0 | 0 | - |  |
| DictionaryBruteForce | 0 | 0 | - |  |
| DoS-HTTP_Flood | 0 | 0 | - |  |
| MITM-ArpSpoofing | 1 | 2 | 1.7 | dc:a6:32:dc:27:d5 claims 192.168.137.1 |
| Mirai-udpplain | 0 | 0 | - |  |
| Recon-PortScan | 0 | 0 | - |  |
| SqlInjection | 0 | 0 | - |  |
| XSS | 0 | 0 | - |  |

Only MITM-ArpSpoofing contains an ARP attack: high alerts elsewhere are false alarms.
