# Official CIC-IoT2023 CSV features with file labels (benchmark as distributed)

483,053 rows, 39 features, ten per-pcap CSV files matching this project's captures. No IPs, timestamps or label column: labels come from the file name only.

| split                    | model         |   macro-F1 (file labels) |   accuracy |   recall Benign |   recall BruteForce |   recall DDoS-SYN |   recall DoS-HTTP |   recall MITM-ARP |   recall Mirai |   recall Recon |   recall Web |
|:-------------------------|:--------------|-------------------------:|-----------:|----------------:|--------------------:|------------------:|------------------:|------------------:|---------------:|---------------:|-------------:|
| stratified random 70/30  | decision tree |                    0.749 |      0.82  |           0.766 |               0.434 |             0.999 |             0.996 |             0.743 |          0.994 |          0.706 |        0.374 |
| stratified random 70/30  | random forest |                    0.803 |      0.873 |           0.934 |               0.41  |             0.999 |             0.999 |             0.727 |          0.995 |          0.768 |        0.353 |
| row order per file 70/30 | decision tree |                    0.727 |      0.814 |           0.763 |               0.399 |             0.996 |             0.997 |             0.771 |          1     |          0.688 |        0.224 |
| row order per file 70/30 | random forest |                    0.778 |      0.868 |           0.938 |               0.372 |             0.996 |             1     |             0.76  |          1     |          0.743 |        0.207 |

| source_file          |   rows |
|:---------------------|-------:|
| Benign_Final         | 129832 |
| CommandInjection     |   5409 |
| DDoS-SYN_Flood       | 137254 |
| DictionaryBruteForce |  13064 |
| DoS-HTTP_Flood       |  31175 |
| MITM-ArpSpoofing     |  59854 |
| Mirai-udpplain       |  15090 |
| Recon-PortScan       |  82284 |
| SqlInjection         |   5245 |
| XSS                  |   3846 |
