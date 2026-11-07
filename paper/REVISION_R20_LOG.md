# Revision R20 log (backup paper\backup_r20\)

Result: main text ends on page 8 (Conclusion and Artifact Availability on page 8; references pages 8-10, PDF 10 pages). Abstract 244 words (wc). No undefined refs, no overfull boxes; check_refs clean.

## Paper changes
1. **New Fig. 1 (Response, late blocks).** `docs/figures/late_blocks.pdf`, built by `src/make_figures.py` (`late_blocks()`) from `results/final/block_timing.md` and `results/final/block_timing_long.md`; k = 1, MITM-ARP verdicts ignored. Rows: pooled 60 s live windows (0.9715 -> 0.1128), pooled 5.9 h persistent (0.968 -> 0.2033), DDoS-SYN 0.962 -> 0.072, BruteForce 0.977 -> 0.188, Recon 0.996 -> 0.50, DoS-HTTP 0.96 -> 0.869, Web 0.905 -> 0.884. MITM-ARP (25) and Mirai (10) omitted, as the caption says.
2. **Correction in Late blocks.** The text said the pooled 5.9 h drop happened "only because" of the 23 s DDoS-SYN test period and that "for longer attacks the loss is smaller". BruteForce contradicts this: its test period is 4,727 s (79 min), yet its share falls from 0.977 to 0.188 (block_timing_long.md, persistent, k = 1). The text now says that DDoS-SYN dominates the pooled value but a long test period does not by itself protect a class, and gives the range from small (DoS-HTTP, web) to large (port scan; brute force).
3. **Abstract.** Adds the late-block result ("Timed at flow export, verdicts let 11% of attack flows start after their block, not 97%"). Wording shortened elsewhere to fit: "traffic outside the attack", "in unseen attack captures", "one split half", Live sentence condensed, Mirai reason ("whose floods form too few flows") removed (still in Section VII).
4. **Label audit paragraph** split into shorter sentences; every number unchanged (checked by script: identical set of numbers before and after).

## Repository (branch `paper-artifacts`, commit 0d2f7fa, not pushed)
- Committed the code and results the paper cites but that were untracked: src/analysis (24 scripts), src/iot23 (11), src/diag additions, results/final, results/iot23, results/live/pin_* (flows.csv ignored), patches/, the `--pin` option of topology/live_experiment.py.
- README aligned with the paper: deployed-tree numbers (0.725 / 0.867) with host-pair CIs instead of the unconstrained tree's flow-level CIs (0.731 / 0.869); latency 63x; four-check summary; IoT-23 scope; repeat and pinned runs; late-block figure; Fadel (CIC IoT-DIAD 2024) removed as in the paper (R17); reproduce steps 8-9.
- split_recall.png now plots the deployed tree.

## Open
- paper/ is still untracked (not committed).
- Zenodo DOI placeholder in Artifact Availability still to be filled.
- results/final/manual_check_key.csv and label_audit_key.csv are committed next to the blind sheets; an external checker should be told not to open the key first.

## R20b (code review pass, 2026-11-07)
- Response, ARP watcher: "a MAC other than the known one announces the router IP" -> "an ARP reply binds the router IP (.1) to a MAC other than the known one" (the code at v1.0-paper reads replies only).
- Artifact Availability: names the tag `v1.0-paper` (pushed; commit 0d2f7fa). The DOI placeholder now asks only for the Zenodo DOI of that tag.
- Build: 10 pages, main text ends on page 8, no undefined refs, no overfull boxes.
- Repo (branch `post-paper-fixes`, commit 7ff7935, not pushed): ARP watcher also reads requests (`--replies-only` = paper rule; on the ten windows the same single high alert, no new high alerts), exact management-subnet check, 28 unit tests + GitHub Actions.
