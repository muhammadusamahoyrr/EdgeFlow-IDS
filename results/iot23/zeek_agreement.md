# IoT-23: Zeek rows per NFStream flow and their label agreement

Matching rule: same unordered 5-tuple (extract_label.tuple_key) and Zeek interval [ts, ts+duration] overlapping the flow's [first_seen - 2 s, last_seen + 2 s]. This includes every row the join could have chosen, so each flow has >= 1 row. Class per row = extract_label.map_class. Flows: 756,268 (the labelled parquet; the 38 unmatched flows are not in it).

## All flows

|           |   flows |   mean rows/flow |   median |   p99 |   max |   flows with >1 row |   flows whose rows carry >1 class |   share >1 class |   joined label != majority of rows |   mean share of rows with joined label |
|:----------|--------:|-----------------:|---------:|------:|------:|--------------------:|----------------------------------:|-----------------:|-----------------------------------:|---------------------------------------:|
| all flows |  756268 |             1.62 |        1 |     3 | 14159 |               0.352 |                               270 |           0.0004 |                                257 |                                 0.9998 |

## By joined (Zeek) class

|              |   flows |   mean rows/flow |   median |   p99 |   max |   flows with >1 row |   flows whose rows carry >1 class |   share >1 class |   joined label != majority of rows |   mean share of rows with joined label |
|:-------------|--------:|-----------------:|---------:|------:|------:|--------------------:|----------------------------------:|-----------------:|-----------------------------------:|---------------------------------------:|
| Attack       |    5994 |             1    |        1 |     1 |     3 |               0     |                                 2 |           0.0003 |                                  2 |                                 0.9998 |
| Benign       |  468575 |             1.06 |        1 |     3 |     5 |               0.032 |                                13 |           0      |                                  7 |                                 1      |
| C&C          |   15334 |             1.44 |        1 |     3 |     3 |               0.308 |                                 0 |           0      |                                  0 |                                 1      |
| DDoS         |     211 |            68.22 |        1 |     9 | 14159 |               0.019 |                                 0 |           0      |                                  0 |                                 1      |
| FileDownload |       6 |             1    |        1 |     1 |     1 |               0     |                                 0 |           0      |                                  0 |                                 1      |
| PortScan     |  266148 |             2.58 |        3 |     3 |     9 |               0.927 |                               255 |           0.001  |                                248 |                                 0.9995 |

## By scenario

|                                   |   flows |   mean rows/flow |   median |   p99 |   max |   flows with >1 row |   flows whose rows carry >1 class |   share >1 class |   joined label != majority of rows |   mean share of rows with joined label |
|:----------------------------------|--------:|-----------------:|---------:|------:|------:|--------------------:|----------------------------------:|-----------------:|-----------------------------------:|---------------------------------------:|
| CTU-Honeypot-Capture-4-1          |    4577 |             1    |        1 |     1 |     1 |               0     |                                 0 |           0      |                                  0 |                                 1      |
| CTU-Honeypot-Capture-5-1          |    2676 |             1.03 |        1 |     2 |     4 |               0.013 |                                 0 |           0      |                                  0 |                                 1      |
| CTU-Honeypot-Capture-7-1-Somfy-01 |     321 |             1    |        1 |     1 |     2 |               0.003 |                                 0 |           0      |                                  0 |                                 1      |
| CTU-IoT-Malware-Capture-1-1       |  633932 |             1.59 |        1 |     3 |     6 |               0.298 |                               216 |           0.0003 |                                210 |                                 0.9998 |
| CTU-IoT-Malware-Capture-20-1      |    3922 |             1    |        1 |     1 |     3 |               0.001 |                                 0 |           0      |                                  0 |                                 1      |
| CTU-IoT-Malware-Capture-21-1      |    4005 |             1    |        1 |     1 |     3 |               0.001 |                                 0 |           0      |                                  0 |                                 1      |
| CTU-IoT-Malware-Capture-3-1       |   88381 |             1.82 |        2 |     2 |     4 |               0.818 |                                54 |           0.0006 |                                 47 |                                 0.9997 |
| CTU-IoT-Malware-Capture-34-1      |    7896 |             3.14 |        1 |     2 | 14159 |               0.339 |                                 0 |           0      |                                  0 |                                 1      |
| CTU-IoT-Malware-Capture-42-1      |    4266 |             1.12 |        1 |     2 |     3 |               0.115 |                                 0 |           0      |                                  0 |                                 1      |
| CTU-IoT-Malware-Capture-8-1       |    6292 |             1.65 |        1 |     3 |     3 |               0.327 |                                 0 |           0      |                                  0 |                                 1      |

## Class combinations among flows whose rows carry >1 class

|                 |   flows |
|:----------------|--------:|
| Benign+PortScan |     267 |
| Attack+Benign   |       2 |
| Attack+PortScan |       1 |

|                                             |   flows with >1 class |
|:--------------------------------------------|----------------------:|
| ('CTU-IoT-Malware-Capture-1-1', 'PortScan') |                   216 |
| ('CTU-IoT-Malware-Capture-3-1', 'Attack')   |                     2 |
| ('CTU-IoT-Malware-Capture-3-1', 'Benign')   |                    13 |
| ('CTU-IoT-Malware-Capture-3-1', 'PortScan') |                    39 |

## Zeek-row side: rows per class and how many flows each overlaps

| scenario                          | cls          |   zeek_rows |   distinct_5tuples |   rows_overlapping_no_flow |   rows_overlapping_1_flow |   rows_overlapping_2plus |
|:----------------------------------|:-------------|------------:|-------------------:|---------------------------:|--------------------------:|-------------------------:|
| CTU-Honeypot-Capture-4-1          | Benign       |         452 |                438 |                          0 |                       437 |                       15 |
| CTU-Honeypot-Capture-5-1          | Benign       |        1374 |                824 |                          0 |                      1253 |                      121 |
| CTU-Honeypot-Capture-7-1-Somfy-01 | Benign       |         130 |                 20 |                          0 |                        74 |                       56 |
| CTU-IoT-Malware-Capture-1-1       | Benign       |      469275 |             429630 |                          0 |                    468752 |                      523 |
| CTU-IoT-Malware-Capture-1-1       | C&C          |           8 |                  8 |                          0 |                         8 |                        0 |
| CTU-IoT-Malware-Capture-1-1       | PortScan     |      539465 |             191161 |                          0 |                    538095 |                     1370 |
| CTU-IoT-Malware-Capture-20-1      | Benign       |        3193 |                623 |                          0 |                      3177 |                       16 |
| CTU-IoT-Malware-Capture-20-1      | C&C          |          16 |                  7 |                          0 |                        14 |                        2 |
| CTU-IoT-Malware-Capture-21-1      | Benign       |        3272 |               1923 |                          0 |                      3256 |                       16 |
| CTU-IoT-Malware-Capture-21-1      | C&C          |          14 |                  7 |                          0 |                        11 |                        3 |
| CTU-IoT-Malware-Capture-3-1       | Attack       |        5962 |               5962 |                          0 |                      5949 |                       13 |
| CTU-IoT-Malware-Capture-3-1       | Benign       |        4536 |               3398 |                          0 |                      4367 |                      169 |
| CTU-IoT-Malware-Capture-3-1       | C&C          |           8 |                  8 |                          0 |                         2 |                        6 |
| CTU-IoT-Malware-Capture-3-1       | PortScan     |      145597 |              72091 |                          0 |                    145597 |                        0 |
| CTU-IoT-Malware-Capture-34-1      | Benign       |        1923 |                290 |                          0 |                      1916 |                        7 |
| CTU-IoT-Malware-Capture-34-1      | C&C          |        6706 |               4055 |                          0 |                      6086 |                      620 |
| CTU-IoT-Malware-Capture-34-1      | DDoS         |       14394 |                211 |                          0 |                     14394 |                        0 |
| CTU-IoT-Malware-Capture-34-1      | PortScan     |         122 |                106 |                          0 |                       122 |                        0 |
| CTU-IoT-Malware-Capture-42-1      | Benign       |        4420 |               3167 |                          0 |                      4407 |                       13 |
| CTU-IoT-Malware-Capture-42-1      | FileDownload |           6 |                  6 |                          0 |                         6 |                        0 |
| CTU-IoT-Malware-Capture-8-1       | Benign       |        2181 |                  8 |                          0 |                      2181 |                        0 |
| CTU-IoT-Malware-Capture-8-1       | C&C          |        8222 |               2056 |                          0 |                      8222 |                        0 |

## DDoS in CTU-IoT-Malware-Capture-34-1 (14,394 Zeek rows -> 211 flows)

- Zeek DDoS rows in 34-1: 14,394 on 211 distinct 5-tuples; NFStream flows with joined label DDoS: 211.
- DDoS rows overlapping >= 1 NFStream flow: 14,394; overlapping none: 0.
- Matching rows per DDoS flow: mean 68.2, median 1, max 14,159; sum over DDoS flows 14,394 (rows can match several flows).
- DDoS flows whose matching rows carry >1 class: 0; mean share of DDoS among their rows 1.0000.
- 34-1 flows of any joined label that overlap >= 1 DDoS row: 211 (by joined label: {'DDoS': 211}).
- 34-1 flows on a 5-tuple that carries DDoS rows (any time): 211 (by joined label: {'DDoS': 211}); distinct such 5-tuples with >= 1 flow: 211 of 211.

Zeek splits a flood on one 5-tuple into many short connections (repeated SYNs / packets), NFStream merges them into one bidirectional flow until the 15 s idle or 120 s active timeout, so one flow overlaps many Zeek rows. Rows whose interval overlaps no flow lie in gaps the flows do not cover under the +-2 s tolerance (or belong to the unmatched flows).
