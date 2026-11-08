# Revision R21 log: second figure, fewer numbers in paragraphs (backup paper\backup_r21\)

Result: PDF 9 pages (was 10), main text ends on page 8, no undefined refs, no overfull boxes. Running text (sections without tables, figures and abstract): 7,916 -> 7,386 words; numbers in paragraphs 477 -> 280.

## New Fig. 1 (Splits): gap by cluster unit
`docs/figures/gap_units.pdf`, built by `src/make_figures.py` (`gap_units()`) from `results/final/gap_nobf_units.md`, column "paired CI, present" (deployed tree, classes present in the resample). Random minus temporal, all classes +0.142 and without BruteForce +0.036, by host pair / attacker host / attacker device / capture. It replaces the interval list in "What a random split hides". The late-block figure becomes Fig. 2.

## Numbers moved out of paragraphs (kept in tables, figures or results files)
- Setup: tree-tuning FPRs (1.3 -> 5.7%), leaf size, NSGA-II 0.723 / 211 KiB, gradient-boosting FPR; IoT-23 match counts rounded.
- Labels: LOCO background counts and paired differences, pooled FPR counts, 0.537/0.409 (in Table III), audit's 91/67 rater disagreements (Threats keeps "four rules fixed"), 345 undecided with 9%/14% weights, corrected DoS-HTTP share / gap / LOCO range; IoT-23 within-split and LOCO numbers (in Table III); CSV per-class recalls summarized as "below 0.45".
- Splits: zero-convention vs present-class intervals, coarse-unit intervals (now Fig. 1), six-class +0.030, permutation p, boundary-spanning counts, DoS-HTTP F1, brute-force training counts and camera addresses, IoT-23 interval values and C&C shares.
- Live: run-1 match count, packet-ratio bounds (now "within 1%"), per-run flow/packet shares (in Table VI), CPU-regression coefficients and s.e., pinned replay-rate range, backlog seconds (now "up to three minutes"), memory (now "near 1 GB"), unpatched XSS flow counts (now "about a third of the packets").
- Response: MITM-counted false blocks per k (now one sentence), enforced-run packet counts and IP counts, persistent-counter Mirai and web details at k=10, 123/3,410 and 7.0%; late-block values now in Fig. 2 (97% vs 11%, 20%, 23 s, 82% kept in text).
- Threats: statistical-conclusion intervals replaced by a pointer to Fig. 1.

Every remaining number was checked against the R20 text or the results files it came from.
