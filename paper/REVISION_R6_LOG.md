# Revision R6 log (2 Nov 2026)

Spec: paper/REVISION_R6.md. Backup of the R5 state: paper/backup_r5/ (sections/*.tex, main.tex, refs.bib).
Runner: src/run_review_r6.sh (`wsl -d Ubuntu-24.04 -u root bash /mnt/d/EdgeFlow-IDS/src/run_review_r6.sh`), log results/review_r6.log (all three scripts exit 0).

**Final PDF: 8 pages including references.** No undefined references or citations, no overfull boxes, no bare `[0-9]%`.
check_refs.py: 39 cited, 39 in bib, none missing, none unused, no TODO. Abstract: 222 words (unchanged; already <= 250).

## Analyses (new scripts, new result files; no existing result file modified)

1. **src/iot23/spanning_common.py -> results/iot23/spanning_common.md**
   - Temporal: common-class macro-F1 0.973 -> 0.974 without spanning flows; all-class 0.649 -> 0.649.
   - Stratified: common-class 0.956 -> 0.918 (host-pair CI [0.735, 0.955]); all-class 0.863 -> 0.809.
   - The stratified drop comes from **C&C** (F1 0.885 -> 0.733, precision 0.799 -> 0.583; 1,473 of 4,600 C&C test flows left) and **FileDownload** (1 of 2 flows removed; 0.571 -> 0.400). **DDoS has no spanning flows** and is unchanged, so the spec's premise ("driven by DDoS (63 flows) and FileDownload (2 flows)") is not supported; the paper states the measured attribution.
   - No class loses all its test flows in either split.
2. **src/analysis/perclass_counts.py -> results/live/perclass_counts.md**: per-class live/offline counts and F1 for run1, run1_r2, run1_r3, edge50 (x3), edge100. Mirai 4 live flows in every run, 5 in edge100; MITM-ARP 2, Web 12, BruteForce 25. One Mirai flow: +0.0063 macro-F1 (8 classes), +0.0125 (4 half-core classes); one missed: -0.0223 / -0.0446.
3. **src/analysis/blocking_r6.py -> results/blocking_accounting_r6.md**
   - (a) Eligible = unordered IP pair seen in the run's own live flows in the window (eval_live.in_window) with no attack-labelled flow there; summed over windows.
   - (b) 1,674 vs 1,675 (run1 sim: 1,673): the two enforced runs differ only by ICMPv6 (proto 58) pairs to ff02::2 from two link-local sources that change in every run (10 other such sources occur in all runs); they land in different windows (DictBF -1, MITM +1, Mirai -1; Benign/CmdInj swap 2 for 2).
   - (c) 21 MITM-ARP-triggered false blocks: 7 in the MITM window, 14 in eight other windows (none in Mirai).
   - (d) 11.1% at every k: DDoS-SYN = 98.1% of 212,965 attack flows, 10.5% of them start after block = 0.103 of 0.111; DoS-HTTP 0.008; six DDoS-SYN pairs blocked at every k (confirmed).

## Changes per section
- **splits.tex**: IoT-23 paragraph now reports common-class F1 with/without spanning flows (temporal 0.974 unchanged; stratified 0.956 -> 0.918 [0.735, 0.955]; all-class 0.863 -> 0.809 via C&C 0.885 -> 0.733 and FileDownload), no class losing all flows, DDoS has none. Claim narrowed (not softened away, since the stratified effect is not small): "because here it inflated the stratified C&C score". Added hedged guess: test-set composition (C&C test flows 4,600 vs 5,152, predicted as C&C 5,714 vs 5,683, C&C precision 0.799 vs 0.901). Spanning-share requirement kept. Space cuts: "The live windows exclude these connections" (stated in live.tex), ARP-rule pointer sentence, Fig. 1 caption's repeat of 1.00->0.05, "case study" sentence shortened.
- **setup.tex**: paired-bootstrap method sentence (union keying, same draw to both splits, absent cluster contributes nothing, F1 from summed confusion matrices; CIC 4,641 from 3,465/3,858; IoT-23 348,350). The 3,465/3,858 parenthetical moved from the marginal-bootstrap sentence into it.
- **live.tex**: fragility sentence next to the one-core 0.810 explanation (4-5 live Mirai flows, MITM-ARP 2, Web 12; one flow ~0.006, 0.0125 over half-core classes). Table V unchanged. Space: intro paragraph shortened; "All live results hold at these rates only" (in Threats); "near-identical" sentence; Pekar sentence tightened; footnote's second sentence (issues #196, #215, PR #227) cut.
- **response.tex**: Table VI caption defines eligible and explains 1,674 vs 1,675; MITM-ARP false-block windows (7 in MITM window, 14 in eight others); Late blocks restores the per-class basis of 11.1%; Garcia & Valeros "(Sec. 6.3)". Table VII caption shortened; tightening of opening, ARP, full-trade-off sentences ("Time to block is not monotonic" cut).
- **discussion.tex**: Threats/External: open-loop replay, "packets dropped" counterfactual, no retransmissions, attackers do not adapt. Future work: per-class or attack-class-averaged criterion for k. Checklist row 2 now "spanning flows inflating stratified C&C (IoT-23)". Space: Construct, Internal, Conclusion-threats, Conclusion and Artifact paragraphs tightened ("needs about 1 GB of memory" cut, still in live.tex as 980-1,025 MB).
- **related.tex**: Garcia & Valeros pointers "(abstract)" and "(Sec. 2.2)" (the second quote's location per CITATION_CHECK_R5.md). Space: Ali et al. asymmetry sentence (still cited in Threats) and Tang et al. sentence (still cited in Intro) cut.
- **labels.tex**: mirror sentence: layout, its 39 columns and per-pcap file names match the dataset's README; bytes not compared with the UNB download (registration form). Tightened robustness-test opening and label-error paragraph.
- **intro.tex**: tightened opening and contribution 1 (same numbers).
- **abstract.tex**: unchanged (222 words <= 250).
- **FACTS.md**: new section "REVISION R6 RESULTS".

## Numbers removed (present in backup_r5/sections, absent now)
| Number(s) | Where | Reason |
|---|---|---|
| 196, 215, 227 (nfstream issue/PR numbers) | live.tex footnote | Cut for space (sentence on a different timer problem) |
All other R5 numbers are still present (checked by token diff of sections/*.tex against backup_r5/sections).

## Not done / deviations
- Spec 1 asked to soften the inflation claim *if* the common-class effect were small; it is small for temporal but not for stratified (-0.038, C&C), so the claim was narrowed to C&C rather than softened, and the DDoS attribution in the spec was not used because the analysis contradicts it.
- Spec 2: chose the compact text option, not new Table V columns (space).
- Spec 8: "39 columns and per-pcap file names match the README" is taken from the spec and CITATION_CHECK_R5.md (layout check) plus results/official_csv_baseline.md (39 features, ten per-pcap files); no new comparison was run in R6.
