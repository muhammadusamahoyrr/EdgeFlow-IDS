# Flow-by-flow match, live vs offline (run1)

Matched 148,756 flows; offline-only 23, live-only 128 (of 148,779 offline / 148,884 live).

Macro-F1 with host-pair bootstrap 95% CI: offline 0.804 [0.457, 0.823], live 0.804 [0.456, 0.822] (1,327 host-pair clusters live).

| window               |   offline flows |   live flows |   matched |   offline only |   live only |   same packets |   same bytes |   same verdict |
|:---------------------|----------------:|-------------:|----------:|---------------:|------------:|---------------:|-------------:|---------------:|
| Benign_Final         |             253 |          261 |       253 |              0 |           8 |         0.9881 |       0.9881 |         0.9763 |
| CommandInjection     |             259 |          252 |       250 |              9 |           2 |         0.992  |       0.992  |         0.988  |
| DDoS-SYN_Flood       |          142724 |       142752 |    142724 |              0 |          28 |         0.9998 |       0.9998 |         1      |
| DictionaryBruteForce |             300 |          300 |       300 |              0 |           0 |         1      |       1      |         0.9967 |
| DoS-HTTP_Flood       |            2398 |         2483 |      2398 |              0 |          85 |         0.9662 |       0.9662 |         0.9921 |
| MITM-ArpSpoofing     |             412 |          414 |       412 |              0 |           2 |         0.9927 |       0.9927 |         0.983  |
| Mirai-udpplain       |             173 |          171 |       168 |              5 |           3 |         0.9821 |       0.9821 |         0.994  |
| Recon-PortScan       |            1572 |         1572 |      1572 |              0 |           0 |         1      |       1      |         0.9987 |
| SqlInjection         |             464 |          464 |       464 |              0 |           0 |         1      |       1      |         0.9978 |
| XSS                  |             224 |          215 |       215 |              9 |           0 |         1      |       1      |         1      |
