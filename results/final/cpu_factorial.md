# CPU budget without the confounds (final review M7, plan D1)

Script: src/analysis/cpu_factorial.py. Pinned runs: src/run_pinned.sh (tcpreplay core 0, ping core 1, gateway cores 2-5 under the cgroup quota; one harness; windows DDoS-SYN_Flood, Mirai-udpplain, DoS-HTTP_Flood; budgets interleaved, 3 repeats). Old runs as in results/repeats.md. Delay = median verdict time after flow end in the window.

## Every run and window

| run         | budget   | window               |   replay pps |   replay / original |   live/offline flows |   match rate |   same packets |   same verdict |   delay (s) |   CPU mean % |   CPU max % |   catch-up wait (s) |   run macro-F1 |   kernel drops | set    |
|:------------|:---------|:---------------------|-------------:|--------------------:|---------------------:|-------------:|---------------:|---------------:|------------:|-------------:|------------:|--------------------:|---------------:|---------------:|:-------|
| edge100     | 1 core   | Benign_Final         |       118.9  |               0.988 |               1.0316 |       1      |         0.9881 |         0.9802 |        15.6 |          0.8 |           3 |               nan   |         0.8102 |              0 | old    |
| run1        | none     | Benign_Final         |       118.47 |               0.985 |               1.0316 |       1      |         0.9881 |         0.9763 |        15.6 |          1   |           3 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | Benign_Final         |       117    |               0.973 |               1.0316 |       1      |         0.9881 |         0.9763 |        15.5 |          1.9 |          43 |                 5   |         0.8038 |              0 | old    |
| run1_r3     | none     | Benign_Final         |       117.96 |               0.98  |               1.0316 |       1      |         0.9881 |         0.9802 |        15.6 |          2.8 |          91 |                 5   |         0.8043 |              0 | old    |
| edge100     | 1 core   | CommandInjection     |        38.09 |               0.994 |               0.973  |       0.9653 |         0.992  |         0.996  |        15.6 |          0.8 |           3 |               nan   |         0.8102 |              0 | old    |
| run1        | none     | CommandInjection     |        38.13 |               0.995 |               0.973  |       0.9653 |         0.992  |         0.988  |        15.7 |          0.8 |           2 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | CommandInjection     |        38.12 |               0.995 |               0.973  |       0.9653 |         0.992  |         0.996  |        15.6 |          0.8 |           2 |                 5   |         0.8038 |              0 | old    |
| run1_r3     | none     | CommandInjection     |        38.11 |               0.995 |               0.973  |       0.9653 |         0.992  |         0.996  |        15.6 |          0.8 |           3 |                 5   |         0.8043 |              0 | old    |
| edge100     | 1 core   | DDoS-SYN_Flood       |     13433.6  |               0.771 |               1      |       1      |         1      |         1      |        21.5 |         69.1 |         104 |               nan   |         0.8102 |              0 | old    |
| edge50      | 1/2 core | DDoS-SYN_Flood       |     12087.7  |               0.694 |               1      |       1      |         1      |         1      |        75.9 |         50.2 |          55 |               137.9 |         0.9175 |              0 | old    |
| edge50_r2   | 1/2 core | DDoS-SYN_Flood       |     11830.9  |               0.679 |               1.1244 |       1      |         0.8757 |         1      |        97   |         50.4 |          55 |               162.7 |         0.9172 |              0 | old    |
| edge50_r3   | 1/2 core | DDoS-SYN_Flood       |     12400.8  |               0.712 |               1      |       1      |         1      |         1      |        60.3 |         49   |          54 |               109.6 |         0.9173 |              0 | old    |
| run1        | none     | DDoS-SYN_Flood       |     12270.8  |               0.704 |               1.0002 |       1      |         0.9998 |         1      |        17.8 |        120.3 |         196 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | DDoS-SYN_Flood       |     11611.3  |               0.666 |               1.1227 |       1      |         0.8773 |         1      |        30.9 |        128.6 |         216 |                19.2 |         0.8038 |              0 | old    |
| run1_r3     | none     | DDoS-SYN_Flood       |     10935.6  |               0.628 |               1.2926 |       1      |         0.7083 |         1      |        34   |        132.3 |         211 |                22.1 |         0.8043 |              0 | old    |
| pin_q100_r1 | 1 core   | DDoS-SYN_Flood       |     13965    |               0.801 |               1      |       1      |         1      |         1      |        22.8 |         70.8 |         103 |                25.1 |         0.9172 |              0 | pinned |
| pin_q100_r2 | 1 core   | DDoS-SYN_Flood       |     14052    |               0.806 |               1      |       1      |         1      |         1      |        22.3 |         66.3 |         104 |                20.1 |         0.9166 |              0 | pinned |
| pin_q100_r3 | 1 core   | DDoS-SYN_Flood       |     12358.9  |               0.709 |               1      |       1      |         1      |         1      |        37.5 |         83.5 |         106 |               102.8 |         0.9296 |              0 | pinned |
| pin_q50_r1  | 1/2 core | DDoS-SYN_Flood       |     13595    |               0.78  |               1      |       1      |         1      |         1      |        46.2 |         48.1 |          55 |                83.4 |         0.9169 |              0 | pinned |
| pin_q50_r2  | 1/2 core | DDoS-SYN_Flood       |     14189.3  |               0.814 |               1      |       1      |         1      |         1      |        38.8 |         45.8 |          53 |                55.2 |         0.917  |              0 | pinned |
| pin_q50_r3  | 1/2 core | DDoS-SYN_Flood       |     11847.5  |               0.68  |               1.0885 |       1      |         0.9116 |         1      |        89.1 |         49.7 |          55 |               174.1 |         0.9173 |              0 | pinned |
| pin_none_r1 | none     | DDoS-SYN_Flood       |     12432.5  |               0.714 |               1      |       1      |         1      |         1      |        18.6 |        115.1 |         195 |                 5   |         0.9171 |              0 | pinned |
| pin_none_r2 | none     | DDoS-SYN_Flood       |     13743.4  |               0.789 |               1      |       1      |         1      |         1      |        17.5 |        104.4 |         192 |                 5   |         0.9169 |              0 | pinned |
| pin_none_r3 | none     | DDoS-SYN_Flood       |     12788.7  |               0.734 |               1      |       1      |         1      |         1      |        18.6 |        118.1 |         207 |                 8   |         0.9171 |              0 | pinned |
| edge100     | 1 core   | DictionaryBruteForce |        51.04 |               0.995 |               1.0033 |       1      |         1      |         0.9967 |        15.7 |         40.6 |         105 |               nan   |         0.8102 |              0 | old    |
| run1        | none     | DictionaryBruteForce |        51.14 |               0.997 |               1      |       1      |         1      |         0.9967 |        15.5 |          0.8 |           3 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | DictionaryBruteForce |        51.06 |               0.996 |               1      |       1      |         1      |         1      |        15.6 |          1.2 |           4 |                 5   |         0.8038 |              0 | old    |
| run1_r3     | none     | DictionaryBruteForce |        51.06 |               0.996 |               1      |       1      |         1      |         0.9967 |        15.6 |          1.2 |           3 |                 5   |         0.8043 |              0 | old    |
| edge100     | 1 core   | DoS-HTTP_Flood       |       685.7  |               0.949 |               1.0083 |       1      |         0.9917 |         0.9908 |        15.4 |          1.8 |           4 |               nan   |         0.8102 |              0 | old    |
| edge50      | 1/2 core | DoS-HTTP_Flood       |       657.69 |               0.91  |               1.0196 |       1      |         0.9808 |         0.9912 |        15.4 |          4.2 |           9 |                 5   |         0.9175 |              0 | old    |
| edge50_r2   | 1/2 core | DoS-HTTP_Flood       |       678.96 |               0.94  |               1.0092 |       1      |         0.9917 |         0.9917 |        15.4 |          2.7 |           6 |                 5   |         0.9172 |              0 | old    |
| edge50_r3   | 1/2 core | DoS-HTTP_Flood       |       655.93 |               0.908 |               1.02   |       1      |         0.9804 |         0.9912 |        15.4 |          4.9 |          13 |                 5.1 |         0.9173 |              0 | old    |
| run1        | none     | DoS-HTTP_Flood       |       633.67 |               0.877 |               1.0354 |       1      |         0.9662 |         0.9921 |        15.3 |          3.8 |          14 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | DoS-HTTP_Flood       |       667.43 |               0.924 |               1.0129 |       1      |         0.9871 |         0.9879 |        15.4 |          3.6 |          10 |                 5   |         0.8038 |              0 | old    |
| run1_r3     | none     | DoS-HTTP_Flood       |       654.94 |               0.906 |               1.0221 |       1      |         0.9787 |         0.9904 |        15.3 |          4.1 |          10 |                 5   |         0.8043 |              0 | old    |
| pin_q100_r1 | 1 core   | DoS-HTTP_Flood       |       690.13 |               0.955 |               1.0092 |       1      |         0.9917 |         0.9917 |        15.3 |          2.8 |           6 |                 5   |         0.9172 |              0 | pinned |
| pin_q100_r2 | 1 core   | DoS-HTTP_Flood       |       678.19 |               0.939 |               1.0117 |       1      |         0.9892 |         0.9912 |        15.4 |          3.6 |          14 |                 5   |         0.9166 |              0 | pinned |
| pin_q100_r3 | 1 core   | DoS-HTTP_Flood       |       619.05 |               0.857 |               1.0154 |       1      |         0.9846 |         0.9917 |        15.4 |          5   |          18 |                 5   |         0.9296 |              0 | pinned |
| pin_q50_r1  | 1/2 core | DoS-HTTP_Flood       |       668.43 |               0.925 |               1.0113 |       1      |         0.9887 |         0.9908 |        15.4 |          4.6 |          10 |                 9   |         0.9169 |              0 | pinned |
| pin_q50_r2  | 1/2 core | DoS-HTTP_Flood       |       681.38 |               0.943 |               1.01   |       1      |         0.9908 |         0.9912 |        15.4 |          3.5 |          10 |                 5   |         0.917  |              0 | pinned |
| pin_q50_r3  | 1/2 core | DoS-HTTP_Flood       |       666.65 |               0.923 |               1.0146 |       1      |         0.9858 |         0.9917 |        15.4 |          5.1 |          12 |                 5   |         0.9173 |              0 | pinned |
| pin_none_r1 | none     | DoS-HTTP_Flood       |       671.35 |               0.929 |               1.0133 |       1      |         0.9875 |         0.9912 |        15.3 |          3.1 |           8 |                 5   |         0.9171 |              0 | pinned |
| pin_none_r2 | none     | DoS-HTTP_Flood       |       682.34 |               0.944 |               1.0092 |       1      |         0.9917 |         0.9912 |        15.3 |          4   |          19 |                 5   |         0.9169 |              0 | pinned |
| pin_none_r3 | none     | DoS-HTTP_Flood       |       633.52 |               0.877 |               1.0309 |       1      |         0.9679 |         0.9917 |        15.4 |          5.9 |          25 |                 5   |         0.9171 |              0 | pinned |
| edge100     | 1 core   | MITM-ArpSpoofing     |       356.75 |               0.931 |               1.0073 |       1      |         0.9927 |         0.9854 |        15.5 |          2.3 |           5 |               nan   |         0.8102 |              0 | old    |
| run1        | none     | MITM-ArpSpoofing     |       364.75 |               0.952 |               1.0049 |       1      |         0.9927 |         0.983  |        15.4 |          1.5 |           4 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | MITM-ArpSpoofing     |       277.25 |               0.724 |               1.0218 |       1      |         0.9782 |         0.9854 |        15.5 |          1.8 |           8 |                 5   |         0.8038 |              0 | old    |
| run1_r3     | none     | MITM-ArpSpoofing     |       362.15 |               0.946 |               1.0073 |       1      |         0.9927 |         0.9879 |        15.4 |          1.8 |           5 |                 5.1 |         0.8043 |              0 | old    |
| edge100     | 1 core   | Mirai-udpplain       |      2663.76 |               0.557 |               1.0058 |       0.9711 |         0.9702 |         0.9762 |        15.2 |          6.6 |          11 |               nan   |         0.8102 |              0 | old    |
| edge50      | 1/2 core | Mirai-udpplain       |      3206.32 |               0.67  |               0.9884 |       0.9711 |         0.9821 |         0.994  |        15.1 |          5.4 |           9 |                 5   |         0.9175 |              0 | old    |
| edge50_r2   | 1/2 core | Mirai-udpplain       |      3685.05 |               0.771 |               0.9884 |       0.9711 |         0.9821 |         0.994  |        15.2 |          3.8 |           9 |                 5   |         0.9172 |              0 | old    |
| edge50_r3   | 1/2 core | Mirai-udpplain       |      3167.13 |               0.662 |               0.9942 |       0.9711 |         0.9762 |         0.9881 |        15.1 |          5.4 |          10 |                 5   |         0.9173 |              0 | old    |
| run1        | none     | Mirai-udpplain       |      3684.67 |               0.77  |               0.9884 |       0.9711 |         0.9821 |         0.994  |        15.1 |          3.8 |           8 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | Mirai-udpplain       |      3578.53 |               0.748 |               0.9884 |       0.9711 |         0.9821 |         0.994  |        15.2 |          4.4 |           7 |                 5   |         0.8038 |              0 | old    |
| run1_r3     | none     | Mirai-udpplain       |      3566.92 |               0.746 |               0.9884 |       0.9711 |         0.9821 |         0.994  |        15.1 |          4.8 |           8 |                 5   |         0.8043 |              0 | old    |
| pin_q100_r1 | 1 core   | Mirai-udpplain       |      3887.92 |               0.813 |               1      |       0.9711 |         0.9821 |         0.994  |        15.2 |          3   |           5 |                 5   |         0.9172 |              0 | pinned |
| pin_q100_r2 | 1 core   | Mirai-udpplain       |      3512.33 |               0.734 |               1      |       0.9711 |         0.9821 |         0.9881 |        15.2 |          4.5 |           8 |                 5   |         0.9166 |              0 | pinned |
| pin_q100_r3 | 1 core   | Mirai-udpplain       |      2176.26 |               0.455 |               1.0289 |       0.9711 |         0.9583 |         0.994  |        15.2 |          4.5 |          11 |                 5   |         0.9296 |              0 | pinned |
| pin_q50_r1  | 1/2 core | Mirai-udpplain       |      3851.07 |               0.805 |               1      |       0.9711 |         0.9821 |         0.994  |        15.1 |          3.9 |           8 |                 5   |         0.9169 |              0 | pinned |
| pin_q50_r2  | 1/2 core | Mirai-udpplain       |      3738.62 |               0.782 |               1      |       0.9711 |         0.9821 |         0.994  |        15.2 |          4.1 |           8 |                 5   |         0.917  |              0 | pinned |
| pin_q50_r3  | 1/2 core | Mirai-udpplain       |      3292.83 |               0.689 |               0.9942 |       0.9711 |         0.9762 |         0.994  |        15.2 |          5.9 |          10 |                 5   |         0.9173 |              0 | pinned |
| pin_none_r1 | none     | Mirai-udpplain       |      3569.3  |               0.746 |               0.9942 |       0.9711 |         0.9821 |         0.994  |        15.1 |          3.1 |           6 |                10   |         0.9171 |              0 | pinned |
| pin_none_r2 | none     | Mirai-udpplain       |      3807.54 |               0.796 |               0.9884 |       0.9711 |         0.9821 |         0.994  |        15.1 |          3.9 |           9 |                 5   |         0.9169 |              0 | pinned |
| pin_none_r3 | none     | Mirai-udpplain       |      3535.28 |               0.739 |               0.9884 |       0.9711 |         0.9821 |         0.994  |        15.1 |          4.6 |           9 |                 5   |         0.9171 |              0 | pinned |
| edge100     | 1 core   | Recon-PortScan       |        94.94 |               0.991 |               1      |       1      |         1      |         0.9987 |        15.6 |          3.3 |          17 |               nan   |         0.8102 |              0 | old    |
| run1        | none     | Recon-PortScan       |        94.91 |               0.99  |               1      |       1      |         1      |         0.9987 |        15.6 |          2   |           8 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | Recon-PortScan       |        94.98 |               0.991 |               1      |       1      |         1      |         0.9994 |        15.6 |          2.1 |           7 |                 5   |         0.8038 |              0 | old    |
| run1_r3     | none     | Recon-PortScan       |        92.66 |               0.967 |               1.0006 |       1      |         0.9994 |         0.9981 |        15.5 |          2.5 |          10 |                 5.2 |         0.8043 |              0 | old    |
| edge100     | 1 core   | SqlInjection         |        59.04 |               0.991 |               1.0022 |       1      |         0.9978 |         0.9978 |        15.6 |          1.7 |           5 |               nan   |         0.8102 |              0 | old    |
| run1        | none     | SqlInjection         |        59.02 |               0.991 |               1      |       1      |         1      |         0.9978 |        15.5 |          1.1 |           4 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | SqlInjection         |        59    |               0.991 |               1      |       1      |         1      |         0.9978 |        15.5 |          1.4 |           5 |                 5   |         0.8038 |              0 | old    |
| run1_r3     | none     | SqlInjection         |        58.92 |               0.989 |               1      |       1      |         1      |         0.9978 |        15.6 |          1.7 |           5 |                 5   |         0.8043 |              0 | old    |
| edge100     | 1 core   | XSS                  |        33.18 |               0.995 |               0.9598 |       0.9598 |         1      |         0.9953 |        15.5 |          1.3 |           3 |               nan   |         0.8102 |              0 | old    |
| run1        | none     | XSS                  |        33.28 |               0.998 |               0.9598 |       0.9598 |         1      |         1      |        15.5 |          0.8 |           3 |               nan   |         0.8042 |              0 | old    |
| run1_r2     | none     | XSS                  |        33.22 |               0.996 |               0.9598 |       0.9598 |         1      |         1      |        15.6 |          1.2 |           5 |                 5   |         0.8038 |              0 | old    |
| run1_r3     | none     | XSS                  |        33.1  |               0.993 |               0.9598 |       0.9598 |         1      |         0.9953 |        15.6 |          1.2 |           3 |                 5   |         0.8043 |              0 | old    |

## DDoS-SYN_Flood

|                        |   runs |   pps_min |   pps_max |   delay_mean |   delay_min |   delay_max |   flows_ratio_min |   flows_ratio_max |   same_pk_min |   catchup_max |
|:-----------------------|-------:|----------:|----------:|-------------:|------------:|------------:|------------------:|------------------:|--------------:|--------------:|
| ('old', '1 core')      |      1 |   13433.6 |   13433.6 |       21.5   |        21.5 |        21.5 |                 1 |             1     |         1     |         nan   |
| ('old', '1/2 core')    |      3 |   11830.9 |   12400.8 |       77.733 |        60.3 |        97   |                 1 |             1.124 |         0.876 |         162.7 |
| ('old', 'none')        |      3 |   10935.6 |   12270.8 |       27.567 |        17.8 |        34   |                 1 |             1.293 |         0.708 |          22.1 |
| ('pinned', '1 core')   |      3 |   12358.9 |   14052   |       27.533 |        22.3 |        37.5 |                 1 |             1     |         1     |         102.8 |
| ('pinned', '1/2 core') |      3 |   11847.5 |   14189.3 |       58.033 |        38.8 |        89.1 |                 1 |             1.088 |         0.912 |         174.1 |
| ('pinned', 'none')     |      3 |   12432.5 |   13743.4 |       18.233 |        17.5 |        18.6 |                 1 |             1     |         1     |           8   |

OLS delay ~ budget + replay rate, old runs:

| term             |   coef (s) |   s.e. |   n |   dof |
|:-----------------|-----------:|-------:|----:|------:|
| intercept        |     260.87 | 130.73 |   7 |     3 |
| 1 core vs none   |      30.68 |  24.51 |   7 |     3 |
| 1/2 core vs none |      60.23 |  10.98 |   7 |     3 |
| per +1,000 pps   |     -20.1  |  11.25 |   7 |     3 |

OLS delay ~ budget + replay rate, pinned runs:

| term             |   coef (s) |   s.e. |   n |   dof |
|:-----------------|-----------:|-------:|----:|------:|
| intercept        |     207.37 |  49.91 |   9 |     5 |
| 1 core vs none   |      16.15 |   7.66 |   9 |     5 |
| 1/2 core vs none |      43.04 |   7.5  |   9 |     5 |
| per +1,000 pps   |     -14.56 |   3.82 |   9 |     5 |

Kruskal-Wallis across budgets (pinned): H = 7.26, p = 0.027; replay pps range in pinned runs 11,847-14,189.

## DoS-HTTP_Flood

|                        |   runs |   pps_min |   pps_max |   delay_mean |   delay_min |   delay_max |   flows_ratio_min |   flows_ratio_max |   same_pk_min |   catchup_max |
|:-----------------------|-------:|----------:|----------:|-------------:|------------:|------------:|------------------:|------------------:|--------------:|--------------:|
| ('old', '1 core')      |      1 |    685.7  |    685.7  |       15.4   |        15.4 |        15.4 |             1.008 |             1.008 |         0.992 |         nan   |
| ('old', '1/2 core')    |      3 |    655.93 |    678.96 |       15.4   |        15.4 |        15.4 |             1.009 |             1.02  |         0.98  |           5.1 |
| ('old', 'none')        |      3 |    633.67 |    667.43 |       15.333 |        15.3 |        15.4 |             1.013 |             1.035 |         0.966 |           5   |
| ('pinned', '1 core')   |      3 |    619.05 |    690.13 |       15.367 |        15.3 |        15.4 |             1.009 |             1.015 |         0.985 |           5   |
| ('pinned', '1/2 core') |      3 |    666.65 |    681.38 |       15.4   |        15.4 |        15.4 |             1.01  |             1.015 |         0.986 |           9   |
| ('pinned', 'none')     |      3 |    633.52 |    682.34 |       15.333 |        15.3 |        15.4 |             1.009 |             1.031 |         0.968 |           5   |

OLS delay ~ budget + replay rate, old runs:

| term             |   coef (s) |   s.e. |   n |   dof |
|:-----------------|-----------:|-------:|----:|------:|
| intercept        |      14.23 |   0.79 |   7 |     3 |
| 1 core vs none   |       0.01 |   0.06 |   7 |     3 |
| 1/2 core vs none |       0.05 |   0.03 |   7 |     3 |
| per +1,000 pps   |       1.69 |   1.22 |   7 |     3 |

OLS delay ~ budget + replay rate, pinned runs:

| term             |   coef (s) |   s.e. |   n |   dof |
|:-----------------|-----------:|-------:|----:|------:|
| intercept        |      16.2  |   0.35 |   9 |     5 |
| 1 core vs none   |       0.03 |   0.03 |   9 |     5 |
| 1/2 core vs none |       0.08 |   0.03 |   9 |     5 |
| per +1,000 pps   |      -1.3  |   0.52 |   9 |     5 |

Kruskal-Wallis across budgets (pinned): H = 2.67, p = 0.264; replay pps range in pinned runs 619-690.

## Mirai-udpplain

|                        |   runs |   pps_min |   pps_max |   delay_mean |   delay_min |   delay_max |   flows_ratio_min |   flows_ratio_max |   same_pk_min |   catchup_max |
|:-----------------------|-------:|----------:|----------:|-------------:|------------:|------------:|------------------:|------------------:|--------------:|--------------:|
| ('old', '1 core')      |      1 |   2663.76 |   2663.76 |       15.2   |        15.2 |        15.2 |             1.006 |             1.006 |         0.97  |           nan |
| ('old', '1/2 core')    |      3 |   3167.13 |   3685.05 |       15.133 |        15.1 |        15.2 |             0.988 |             0.994 |         0.976 |             5 |
| ('old', 'none')        |      3 |   3566.92 |   3684.67 |       15.133 |        15.1 |        15.2 |             0.988 |             0.988 |         0.982 |             5 |
| ('pinned', '1 core')   |      3 |   2176.26 |   3887.92 |       15.2   |        15.2 |        15.2 |             1     |             1.029 |         0.958 |             5 |
| ('pinned', '1/2 core') |      3 |   3292.83 |   3851.07 |       15.167 |        15.1 |        15.2 |             0.994 |             1     |         0.976 |             5 |
| ('pinned', 'none')     |      3 |   3535.28 |   3807.54 |       15.1   |        15.1 |        15.1 |             0.988 |             0.994 |         0.982 |            10 |

OLS delay ~ budget + replay rate, old runs:

| term             |   coef (s) |   s.e. |   n |   dof |
|:-----------------|-----------:|-------:|----:|------:|
| intercept        |      14.51 |   0.45 |   7 |     3 |
| 1 core vs none   |       0.23 |   0.13 |   7 |     3 |
| 1/2 core vs none |       0.04 |   0.05 |   7 |     3 |
| per +1,000 pps   |       0.17 |   0.12 |   7 |     3 |

OLS delay ~ budget + replay rate, pinned runs:

| term             |   coef (s) |   s.e. |   n |   dof |
|:-----------------|-----------:|-------:|----:|------:|
| intercept        |      15.14 |   0.1  |   9 |     5 |
| 1 core vs none   |       0.09 |   0.03 |   9 |     5 |
| 1/2 core vs none |       0.07 |   0.03 |   9 |     5 |
| per +1,000 pps   |      -0.01 |   0.03 |   9 |     5 |

Kruskal-Wallis across budgets (pinned): H = 5.60, p = 0.061; replay pps range in pinned runs 2,176-3,888.

