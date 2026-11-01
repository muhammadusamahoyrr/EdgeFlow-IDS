# Enforcement results (enforce_k1)

Blocked host pairs: 77 · correct (attack) 18 · false blocks 59
Packets dropped by the gateway's rules: 267,393
A pair is blocked only after its first flow has ended and been classified (idle timeout 15 s), so short attacks finish before the block.

| window               |   blocked_pairs |   correct |   dropped_packets |   window_packets |   median_block_after_flow_start_s |   dropped_share_of_window |
|:---------------------|----------------:|----------:|------------------:|-----------------:|----------------------------------:|--------------------------:|
| Benign_Final         |               4 |         0 |                72 |             7215 |                           16.0985 |                     0.01  |
| CommandInjection     |               4 |         1 |               104 |             2295 |                           15.6553 |                     0.045 |
| DDoS-SYN_Flood       |              24 |         6 |            137116 |           388686 |                           25.3896 |                     0.353 |
| DictionaryBruteForce |               2 |         1 |               406 |             3070 |                           15.5122 |                     0.132 |
| DoS-HTTP_Flood       |              17 |         1 |             30573 |            43353 |                           16.6012 |                     0.705 |
| MITM-ArpSpoofing     |              11 |         0 |                77 |            22978 |                           15.7211 |                     0.003 |
| Mirai-udpplain       |               7 |         7 |             99000 |           286937 |                           25.6511 |                     0.345 |
| Recon-PortScan       |               4 |         1 |                33 |             5738 |                           15.4568 |                     0.006 |
| SqlInjection         |               4 |         1 |                12 |             3571 |                           15.8862 |                     0.003 |

False blocks (benign pairs):

| window               | src_ip          | dst_ip          |   dst_port | pred     |   dropped_packets |
|:---------------------|:----------------|:----------------|-----------:|:---------|------------------:|
| Benign_Final         | 192.168.137.133 | 192.168.137.1   |         53 | MITM-ARP |                48 |
| Benign_Final         | 192.168.137.253 | 173.198.192.103 |       4431 | DoS-HTTP |                 0 |
| Benign_Final         | 192.168.137.253 | 192.168.137.1   |         53 | MITM-ARP |                20 |
| Benign_Final         | 192.168.137.16  | 192.168.137.1   |         53 | DoS-HTTP |                 4 |
| CommandInjection     | 192.168.137.121 | 172.253.63.188  |       5228 | MITM-ARP |                10 |
| CommandInjection     | 34.213.103.51   | 192.168.137.55  |      38926 | MITM-ARP |                20 |
| CommandInjection     | 108.138.125.14  | 192.168.137.12  |      32964 | DoS-HTTP |                 0 |
| DDoS-SYN_Flood       | 192.168.137.245 | 34.158.253.218  |         80 | DoS-HTTP |                 0 |
| DDoS-SYN_Flood       | 192.168.137.253 | 34.158.253.218  |       4070 | DoS-HTTP |                 0 |
| DDoS-SYN_Flood       | 192.168.137.7   | 192.168.137.158 |       8009 | DoS-HTTP |                 1 |
| DDoS-SYN_Flood       | 54.218.246.107  | 192.168.137.209 |      48256 | MITM-ARP |                 0 |
| DDoS-SYN_Flood       | 192.168.137.245 | 99.83.183.187   |        443 | DoS-HTTP |                 0 |
| DDoS-SYN_Flood       | 3.227.250.207   | 192.168.137.228 |      56431 | DoS-HTTP |                 0 |
| DDoS-SYN_Flood       | 75.2.39.155     | 192.168.137.159 |      35502 | DoS-HTTP |                 0 |
| DDoS-SYN_Flood       | 35.169.134.177  | 192.168.137.159 |      46316 | DoS-HTTP |                 0 |
| DDoS-SYN_Flood       | 3.223.181.245   | 192.168.137.54  |      40232 | Mirai    |                 0 |
| DDoS-SYN_Flood       | 192.168.137.140 | 35.161.249.48   |      20443 | DDoS-SYN |                 0 |
| DDoS-SYN_Flood       | 44.231.239.23   | 192.168.137.172 |      34858 | MITM-ARP |                 0 |
| DDoS-SYN_Flood       | 192.168.137.11  | 54.192.51.75    |        443 | DoS-HTTP |                 0 |
| DDoS-SYN_Flood       | 192.168.137.94  | 54.148.153.241  |       8886 | Recon    |                 0 |
| DDoS-SYN_Flood       | 192.168.137.43  | 35.161.158.54   |       8886 | Recon    |                 0 |
| DDoS-SYN_Flood       | 192.168.137.225 | 35.168.43.144   |       1883 | DDoS-SYN |                 0 |
| DDoS-SYN_Flood       | 192.168.137.21  | 54.188.99.4     |       8886 | DDoS-SYN |                 0 |
| DDoS-SYN_Flood       | 75.2.39.155     | 192.168.137.11  |      43240 | DoS-HTTP |                 0 |
| DDoS-SYN_Flood       | 75.2.39.155     | 192.168.137.106 |      49154 | DoS-HTTP |                 0 |
| DictionaryBruteForce | 192.168.137.41  | 172.253.115.188 |        443 | MITM-ARP |                 4 |
| DoS-HTTP_Flood       | 192.168.137.153 | 17.57.147.5     |       5223 | MITM-ARP |                 0 |
| DoS-HTTP_Flood       | 192.168.137.66  | 192.168.137.244 |       8009 | DoS-HTTP |                 6 |
| DoS-HTTP_Flood       | 54.197.127.199  | 192.168.137.222 |      47084 | DoS-HTTP |                 0 |
| DoS-HTTP_Flood       | 17.248.175.137  | 192.168.137.153 |      54237 | DoS-HTTP |                19 |
| DoS-HTTP_Flood       | 52.87.75.92     | 192.168.137.191 |      44410 | DoS-HTTP |                 0 |
| DoS-HTTP_Flood       | 192.168.137.66  | 192.168.137.254 |      60000 | MITM-ARP |                 1 |
| DoS-HTTP_Flood       | 54.210.31.159   | 192.168.137.254 |      56256 | DoS-HTTP |                 0 |
| DoS-HTTP_Flood       | 192.168.137.64  | 192.168.137.1   |          7 | DoS-HTTP |                 2 |
| DoS-HTTP_Flood       | 192.168.137.123 | 192.168.137.191 |      55443 | DoS-HTTP |                14 |
| DoS-HTTP_Flood       | 44.197.43.221   | 192.168.137.222 |      52634 | DoS-HTTP |                 0 |
| DoS-HTTP_Flood       | 47.254.72.224   | 192.168.137.163 |      47856 | DoS-HTTP |                 0 |
| DoS-HTTP_Flood       | 52.6.61.231     | 192.168.137.254 |      58285 | DoS-HTTP |                 0 |
| DoS-HTTP_Flood       | 192.168.137.163 | 39.108.218.123  |      13502 | DoS-HTTP |                 0 |
| DoS-HTTP_Flood       | 54.212.163.173  | 192.168.137.224 |      53585 | DoS-HTTP |                 0 |
| DoS-HTTP_Flood       | 18.211.132.11   | 192.168.137.3   |      57009 | DDoS-SYN |                 0 |
| DoS-HTTP_Flood       | 34.205.1.68     | 192.168.137.6   |      47142 | MITM-ARP |                 0 |
| MITM-ArpSpoofing     | 192.168.137.100 | 34.117.13.189   |        443 | MITM-ARP |                 4 |
| MITM-ArpSpoofing     | 192.168.137.145 | 173.198.192.117 |       4431 | MITM-ARP |                28 |
| MITM-ArpSpoofing     | 192.168.137.145 | 34.107.165.188  |        443 | MITM-ARP |                 0 |
| MITM-ArpSpoofing     | 192.168.137.150 | 172.217.1.10    |        443 | MITM-ARP |                 0 |
| MITM-ArpSpoofing     | 192.168.137.163 | 120.76.210.199  |         80 | DoS-HTTP |                45 |
| MITM-ArpSpoofing     | 192.168.137.145 | 172.217.1.2     |        443 | MITM-ARP |                 0 |
| MITM-ArpSpoofing     | 192.168.137.145 | 3.144.50.152    |         80 | MITM-ARP |                 0 |
| MITM-ArpSpoofing     | 192.168.137.13  | 142.251.33.164  |        443 | MITM-ARP |                 0 |
| MITM-ArpSpoofing     | 192.168.137.38  | 142.251.111.188 |       5228 | MITM-ARP |                 0 |
| MITM-ArpSpoofing     | 192.168.137.23  | 192.168.137.1   |         53 | DoS-HTTP |                 0 |
| MITM-ArpSpoofing     | 192.168.137.76  | 54.188.27.243   |        443 | MITM-ARP |                 0 |
| Recon-PortScan       | 192.168.137.238 | 52.11.155.34    |         21 | DoS-HTTP |                 5 |
| Recon-PortScan       | 192.168.137.59  | 142.251.32.67   |         80 | MITM-ARP |                 0 |
| Recon-PortScan       | 192.168.137.41  | 109.95.152.166  |        443 | DoS-HTTP |                28 |
| SqlInjection         | 13.225.189.40   | 192.168.137.234 |      45442 | DoS-HTTP |                 0 |
| SqlInjection         | 142.251.111.188 | 192.168.137.59  |      58478 | MITM-ARP |                 0 |
| SqlInjection         | 100.21.156.247  | 192.168.137.242 |      50919 | MITM-ARP |                 0 |
