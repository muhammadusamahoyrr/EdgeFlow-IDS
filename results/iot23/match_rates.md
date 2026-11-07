# IoT-23: NFStream flows joined to Zeek conn.log.labeled

Join: unordered 5-tuple + nearest start within +-2 s; otherwise the flow's start inside a Zeek connection with the same 5-tuple (NFStream splits long connections; Zeek does not).

| scenario                          |   NFStream flows |   Zeek conns |   matched (start +-2 s) |   matched (inside Zeek conn) |   unmatched (dropped) |   match rate |   start-only rate |
|:----------------------------------|-----------------:|-------------:|------------------------:|-----------------------------:|----------------------:|-------------:|------------------:|
| CTU-Honeypot-Capture-4-1          |             4577 |          452 |                     452 |                         4125 |                     0 |       1      |            0.0988 |
| CTU-Honeypot-Capture-5-1          |             2712 |         1374 |                    1300 |                         1376 |                    36 |       0.9867 |            0.4794 |
| CTU-Honeypot-Capture-7-1-Somfy-01 |              322 |          130 |                     129 |                          192 |                     1 |       0.9969 |            0.4006 |
| CTU-IoT-Malware-Capture-1-1       |           633932 |      1008748 |                  631770 |                         2162 |                     0 |       1      |            0.9966 |
| CTU-IoT-Malware-Capture-3-1       |            88382 |       156103 |                   83729 |                         4652 |                     1 |       1      |            0.9474 |
| CTU-IoT-Malware-Capture-8-1       |             6292 |        10403 |                    6292 |                            0 |                     0 |       1      |            1      |
| CTU-IoT-Malware-Capture-20-1      |             3922 |         3209 |                    3200 |                          722 |                     0 |       1      |            0.8159 |
| CTU-IoT-Malware-Capture-21-1      |             4005 |         3286 |                    3279 |                          726 |                     0 |       1      |            0.8187 |
| CTU-IoT-Malware-Capture-34-1      |             7896 |        23145 |                    6262 |                         1634 |                     0 |       1      |            0.7931 |
| CTU-IoT-Malware-Capture-42-1      |             4266 |         4426 |                    3931 |                          335 |                     0 |       1      |            0.9215 |

Total: 756,306 flows, matched 99.99% (start rule alone 97.89%); 38 unmatched flows dropped.

Zeek connections can outnumber flows: Zeek logs repeated SYNs and flood packets on one 5-tuple as many short connections, which NFStream merges into one flow (e.g. 34-1: 14,394 Zeek DDoS connections on 317 distinct 5-tuples). Zeek and pcap time ranges agree to the millisecond, so no clock offset was applied.

Class counts after the join:

| label        |   flows |
|:-------------|--------:|
| Benign       |  468575 |
| PortScan     |  266148 |
| C&C          |   15334 |
| Attack       |    5994 |
| DDoS         |     211 |
| FileDownload |       6 |

Zeek (label, detailed-label) -> class:

|                                                        |   flows |
|:-------------------------------------------------------|--------:|
| ('Benign', '-', 'Benign')                              |  461001 |
| ('Malicious', 'Attack', 'Attack')                      |    5994 |
| ('Malicious', 'C&C', 'C&C')                            |   13909 |
| ('Malicious', 'C&C-FileDownload', 'FileDownload')      |       3 |
| ('Malicious', 'C&C-Torii', 'C&C')                      |    1425 |
| ('Malicious', 'DDoS', 'DDoS')                          |     211 |
| ('Malicious', 'FileDownload', 'FileDownload')          |       3 |
| ('Malicious', 'PartOfAHorizontalPortScan', 'PortScan') |  266148 |
| ('benign', '-', 'Benign')                              |    7574 |
