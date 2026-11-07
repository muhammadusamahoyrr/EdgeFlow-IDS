# IoT-23: attack vs background flows per scenario (Zeek labels)

NFStream flows matched to a Zeek connection (src/iot23/extract_label.py); background = Zeek label Benign.

| scenario                          | family    |   flows |   attack_flows |   background_flows |   background_share |
|:----------------------------------|:----------|--------:|---------------:|-------------------:|-------------------:|
| CTU-Honeypot-Capture-4-1          | Benign    |    4577 |              0 |               4577 |              1     |
| CTU-Honeypot-Capture-5-1          | Benign    |    2676 |              0 |               2676 |              1     |
| CTU-Honeypot-Capture-7-1-Somfy-01 | Benign    |     321 |              0 |                321 |              1     |
| CTU-IoT-Malware-Capture-1-1       | Hide&Seek |  633932 |         192640 |             441292 |              0.696 |
| CTU-IoT-Malware-Capture-20-1      | Torii     |    3922 |            713 |               3209 |              0.818 |
| CTU-IoT-Malware-Capture-21-1      | Torii     |    4005 |            712 |               3293 |              0.822 |
| CTU-IoT-Malware-Capture-3-1       | Muhstik   |   88381 |          83516 |               4865 |              0.055 |
| CTU-IoT-Malware-Capture-34-1      | Mirai     |    7896 |           5995 |               1901 |              0.241 |
| CTU-IoT-Malware-Capture-42-1      | Trojan    |    4266 |              6 |               4260 |              0.999 |
| CTU-IoT-Malware-Capture-8-1       | Hakai     |    6292 |           4111 |               2181 |              0.347 |

Flows per class:

| scenario                          | family    |   Attack |   Benign |   C&C |   DDoS |   FileDownload |   PortScan |
|:----------------------------------|:----------|---------:|---------:|------:|-------:|---------------:|-----------:|
| CTU-Honeypot-Capture-4-1          | Benign    |        0 |     4577 |     0 |      0 |              0 |          0 |
| CTU-Honeypot-Capture-5-1          | Benign    |        0 |     2676 |     0 |      0 |              0 |          0 |
| CTU-Honeypot-Capture-7-1-Somfy-01 | Benign    |        0 |      321 |     0 |      0 |              0 |          0 |
| CTU-IoT-Malware-Capture-1-1       | Hide&Seek |        0 |   441292 |     8 |      0 |              0 |     192632 |
| CTU-IoT-Malware-Capture-20-1      | Torii     |        0 |     3209 |   713 |      0 |              0 |          0 |
| CTU-IoT-Malware-Capture-21-1      | Torii     |        0 |     3293 |   712 |      0 |              0 |          0 |
| CTU-IoT-Malware-Capture-3-1       | Muhstik   |     5994 |     4865 |  4112 |      0 |              0 |      73410 |
| CTU-IoT-Malware-Capture-34-1      | Mirai     |        0 |     1901 |  5678 |    211 |              0 |        106 |
| CTU-IoT-Malware-Capture-42-1      | Trojan    |        0 |     4260 |     0 |      0 |              6 |          0 |
| CTU-IoT-Malware-Capture-8-1       | Hakai     |        0 |     2181 |  4111 |      0 |              0 |          0 |
