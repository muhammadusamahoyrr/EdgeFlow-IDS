# Per-class live and offline flow counts and F1, every detection run

Source: results/live/<run>/live_vs_offline.json. Offline = the same windows exported offline from the pcaps. No-limit and one-core runs: ten windows (eight classes); half-core runs: three windows (DDoS-SYN, DoS-HTTP, Mirai; four classes).

## Test-flow counts per class

| run       | CPU       | side    |   flows |   macro-F1 |   Benign |   BruteForce |   DDoS-SYN |   DoS-HTTP |   MITM-ARP |   Mirai |   Recon |   Web |
|:----------|:----------|:--------|--------:|-----------:|---------:|-------------:|-----------:|-----------:|-----------:|--------:|--------:|------:|
| run1      | no limit  | offline | 148,779 |     0.8036 |     3230 |           25 |     142554 |       1871 |          2 |       4 |    1081 |    12 |
| run1      | no limit  | live    | 148,884 |     0.8042 |     3225 |           25 |     142580 |       1955 |          2 |       4 |    1081 |    12 |
| run1_r2   | no limit  | offline | 148,779 |     0.8036 |     3230 |           25 |     142554 |       1871 |          2 |       4 |    1081 |    12 |
| run1_r2   | no limit  | live    | 166,327 |     0.8038 |     3233 |           25 |     160068 |       1902 |          2 |       4 |    1081 |    12 |
| run1_r3   | no limit  | offline | 148,779 |     0.8036 |     3230 |           25 |     142554 |       1871 |          2 |       4 |    1081 |    12 |
| run1_r3   | no limit  | live    | 190,585 |     0.8043 |     3229 |           25 |     184308 |       1924 |          2 |       4 |    1081 |    12 |
| edge50    | half core | offline | 145,295 |     0.9145 |      866 |          nan |     142554 |       1871 |        nan |       4 |     nan |   nan |
| edge50    | half core | live    | 145,346 |     0.9175 |      871 |          nan |     142554 |       1917 |        nan |       4 |     nan |   nan |
| edge50_r2 | half core | offline | 145,295 |     0.9145 |      866 |          nan |     142554 |       1871 |        nan |       4 |     nan |   nan |
| edge50_r2 | half core | live    | 163,066 |     0.9172 |      874 |          nan |     160297 |       1891 |        nan |       4 |     nan |   nan |
| edge50_r3 | half core | offline | 145,295 |     0.9145 |      866 |          nan |     142554 |       1871 |        nan |       4 |     nan |   nan |
| edge50_r3 | half core | live    | 145,347 |     0.9173 |      871 |          nan |     142554 |       1918 |        nan |       4 |     nan |   nan |
| edge100   | one core  | offline | 148,779 |     0.8036 |     3230 |           25 |     142554 |       1871 |          2 |       4 |    1081 |    12 |
| edge100   | one core  | live    | 148,798 |     0.8102 |     3228 |           25 |     142554 |       1891 |          2 |       5 |    1081 |    12 |

## Per-class F1

| run       | CPU       | side    |   flows |   macro-F1 |   Benign |   BruteForce |   DDoS-SYN |   DoS-HTTP |   MITM-ARP |   Mirai |   Recon |    Web |
|:----------|:----------|:--------|--------:|-----------:|---------:|-------------:|-----------:|-----------:|-----------:|--------:|--------:|-------:|
| run1      | no limit  | offline | 148,779 |     0.8036 |    0.976 |         0.78 |          1 |      0.971 |          0 |    0.75 |   0.992 |   0.96 |
| run1      | no limit  | live    | 148,884 |     0.8042 |    0.977 |         0.78 |          1 |      0.975 |          0 |    0.75 |   0.992 |   0.96 |
| run1_r2   | no limit  | offline | 148,779 |     0.8036 |    0.976 |         0.78 |          1 |      0.971 |          0 |    0.75 |   0.992 |   0.96 |
| run1_r2   | no limit  | live    | 166,327 |     0.8038 |    0.976 |         0.78 |          1 |      0.972 |          0 |    0.75 |   0.992 |   0.96 |
| run1_r3   | no limit  | offline | 148,779 |     0.8036 |    0.976 |         0.78 |          1 |      0.971 |          0 |    0.75 |   0.992 |   0.96 |
| run1_r3   | no limit  | live    | 190,585 |     0.8043 |    0.978 |         0.78 |          1 |      0.974 |          0 |    0.75 |   0.992 |   0.96 |
| edge50    | half core | offline | 145,295 |     0.9145 |    0.936 |       nan    |          1 |      0.972 |        nan |    0.75 | nan     | nan    |
| edge50    | half core | live    | 145,346 |     0.9175 |    0.944 |       nan    |          1 |      0.976 |        nan |    0.75 | nan     | nan    |
| edge50_r2 | half core | offline | 145,295 |     0.9145 |    0.936 |       nan    |          1 |      0.972 |        nan |    0.75 | nan     | nan    |
| edge50_r2 | half core | live    | 163,066 |     0.9172 |    0.943 |       nan    |          1 |      0.976 |        nan |    0.75 | nan     | nan    |
| edge50_r3 | half core | offline | 145,295 |     0.9145 |    0.936 |       nan    |          1 |      0.972 |        nan |    0.75 | nan     | nan    |
| edge50_r3 | half core | live    | 145,347 |     0.9173 |    0.943 |       nan    |          1 |      0.976 |        nan |    0.75 | nan     | nan    |
| edge100   | one core  | offline | 148,779 |     0.8036 |    0.976 |         0.78 |          1 |      0.971 |          0 |    0.75 |   0.992 |   0.96 |
| edge100   | one core  | live    | 148,798 |     0.8102 |    0.977 |         0.78 |          1 |      0.972 |          0 |    0.8  |   0.992 |   0.96 |

## Fragility of the small classes (derived from rounded precision/recall; see docstring)

| run       | side    | class      |   support |   TP |   FN |   FP |   F1 (json) |   F1 (recomputed) |   classes in macro |   macro change, +1 detected |   macro change, 1 detected missed |
|:----------|:--------|:-----------|----------:|-----:|-----:|-----:|------------:|------------------:|-------------------:|----------------------------:|----------------------------------:|
| run1      | offline | BruteForce |        25 |   16 |    9 |    0 |        0.78 |              0.78 |                  8 |                      0.0013 |                           -0.0038 |
| run1      | offline | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  8 |                      0.0063 |                           -0.0223 |
| run1      | offline | Web        |        12 |   12 |    0 |    1 |        0.96 |              0.96 |                  8 |                      0.0004 |                           -0.0054 |
| run1      | live    | BruteForce |        25 |   16 |    9 |    0 |        0.78 |              0.78 |                  8 |                      0.0013 |                           -0.0038 |
| run1      | live    | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  8 |                      0.0063 |                           -0.0223 |
| run1      | live    | Web        |        12 |   12 |    0 |    1 |        0.96 |              0.96 |                  8 |                      0.0004 |                           -0.0054 |
| run1_r2   | offline | BruteForce |        25 |   16 |    9 |    0 |        0.78 |              0.78 |                  8 |                      0.0013 |                           -0.0038 |
| run1_r2   | offline | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  8 |                      0.0063 |                           -0.0223 |
| run1_r2   | offline | Web        |        12 |   12 |    0 |    1 |        0.96 |              0.96 |                  8 |                      0.0004 |                           -0.0054 |
| run1_r2   | live    | BruteForce |        25 |   16 |    9 |    0 |        0.78 |              0.78 |                  8 |                      0.0013 |                           -0.0038 |
| run1_r2   | live    | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  8 |                      0.0063 |                           -0.0223 |
| run1_r2   | live    | Web        |        12 |   12 |    0 |    1 |        0.96 |              0.96 |                  8 |                      0.0004 |                           -0.0054 |
| run1_r3   | offline | BruteForce |        25 |   16 |    9 |    0 |        0.78 |              0.78 |                  8 |                      0.0013 |                           -0.0038 |
| run1_r3   | offline | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  8 |                      0.0063 |                           -0.0223 |
| run1_r3   | offline | Web        |        12 |   12 |    0 |    1 |        0.96 |              0.96 |                  8 |                      0.0004 |                           -0.0054 |
| run1_r3   | live    | BruteForce |        25 |   16 |    9 |    0 |        0.78 |              0.78 |                  8 |                      0.0013 |                           -0.0038 |
| run1_r3   | live    | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  8 |                      0.0063 |                           -0.0223 |
| run1_r3   | live    | Web        |        12 |   12 |    0 |    1 |        0.96 |              0.96 |                  8 |                      0.0004 |                           -0.0054 |
| edge50    | offline | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  4 |                      0.0125 |                           -0.0446 |
| edge50    | live    | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  4 |                      0.0125 |                           -0.0446 |
| edge50_r2 | offline | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  4 |                      0.0125 |                           -0.0446 |
| edge50_r2 | live    | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  4 |                      0.0125 |                           -0.0446 |
| edge50_r3 | offline | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  4 |                      0.0125 |                           -0.0446 |
| edge50_r3 | live    | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  4 |                      0.0125 |                           -0.0446 |
| edge100   | offline | BruteForce |        25 |   16 |    9 |    0 |        0.78 |              0.78 |                  8 |                      0.0013 |                           -0.0038 |
| edge100   | offline | Mirai      |         4 |    3 |    1 |    1 |        0.75 |              0.75 |                  8 |                      0.0063 |                           -0.0223 |
| edge100   | offline | Web        |        12 |   12 |    0 |    1 |        0.96 |              0.96 |                  8 |                      0.0004 |                           -0.0054 |
| edge100   | live    | BruteForce |        25 |   16 |    9 |    0 |        0.78 |              0.78 |                  8 |                      0.0013 |                           -0.0038 |
| edge100   | live    | Mirai      |         5 |    4 |    1 |    1 |        0.8  |              0.8  |                  8 |                      0.0042 |                           -0.0167 |
| edge100   | live    | Web        |        12 |   12 |    0 |    1 |        0.96 |              0.96 |                  8 |                      0.0004 |                           -0.0054 |

## Flow-by-flow match (where logged)

run1: Matched 148,756 flows; offline-only 23, live-only 128 (of 148,779 offline / 148,884 live).

Range of live Mirai flows over all runs: 4--5; MITM-ARP (ten-window runs): 2--2; Web: 12--12; BruteForce: 25--25.
