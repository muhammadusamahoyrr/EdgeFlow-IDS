# Revision R12 log: reviewer round (audit carried into scoring, audit statistics, persistent counters)

Backup: `paper\backup_r12\` (taken after R11, before any R12 edit).
Result: 8 pages, abstract 240 words (was 250), no undefined refs/citations, no overfull boxes, no BibTeX warnings, no bare `%`, check_refs.py clean.

## New analyses (all run 3 Nov 2026, one at a time in WSL)
- `src/analysis/corrected_headline.py` -> `results/final/corrected_headline.md`: every affected headline number under the audit-corrected labels (C1 .174 flood, C2 two Web flows; label_corrections.correct()). Old-label rows reproduce the paper exactly (0.7249, CI [0.568, 0.822], FPR 2,030/52,993).
- `src/analysis/persistent_counters.py --corrected` -> `results/final/persistent_counters_corrected.md` (new option; per-class blocking under corrected labels).
- `src/diag/iot23_0649_check.py` -> `results/iot23/table3_0649_check.md`.

## Priority 1: audit carried into scoring
- **Benign FPR 3.8% -> 1.3%** under corrected labels (656/50,726); background FPR 4.85% -> 1.42%; the DoS-HTTP capture's "background" FPR 26.8% -> 1.3%. Macro-F1 0.7249 -> 0.7294, host-pair CI [0.585, 0.827]; w/o MITM-ARP 0.8311. DoS-HTTP background share 23.0% -> 18.6%; file/evidence label disagreement 13.4% -> 13.1%. File-label tree: macro-F1 vs evidence 0.396 -> 0.409, pooled FPR 71.8% -> 70.6%, background 86.1% -> 85.3%. LOCO evidence-label range 0.5-5.4% -> 0.7-4.4%.
- **5.4% LOCO top = DDoS-SYN capture** (22/409 background flows), not the flood; corrected 4.4%.
- **Live false blocks unchanged:** no live window (any run) contains a .66-.174 flow (grep of all flows.csv) or the .178-.154 UPnP pair. 60/1,674 stands. Breakdown restored: 56 uninvolved, 2 attacker host's other traffic, 2 victim's (results/blocking_accounting.md (a)).
- **5.9 h replay:** under original labels, the single false block left by the 60 s reset at k >= 5 IS the (.66, .174) pair. Corrected: reset 0 false blocks at k = 5, 10, 20.
- Paper: tables keep original labels; Labels "Label audit" lists every corrected headline number; Setup gives 0.729 / 1.3%; Response notes the live counts are unaffected; Discussion Internal gives the FPR change.

## Priority 2: audit statistics
- Wilson CI dropped. Stratum-weighted error: 0.004% of attack-labelled, 4.3% of Benign-labelled test flows (all the .174 flood). Computed from label_audit.md (a) populations.
- Undecided 345/975: 239 in strata C, D, B-fn (label-model disagreement); weighted share 9.3% of attack-labelled, 13.8% of Benign-labelled flows. Stated as a limit.
- Human check: NOT done (needs a person). Paper says the blind 975-flow sample is released.

## Priority 3: persistent counters / response claims
- k = 10 (enforced policy) under persistent counters: 2 false blocks (0.3/h), reset 0 (corrected labels). k = 5: 6 vs 0; k = 3: 21 vs 2. Web at k = 5: 7/7 persistent vs 3/7 reset; k = 10: 2 vs 1. Mirai unchanged (1/6 at k = 3, 0 from k = 5).
- Table I row 4 now: "Mirai bots missed by the detector, web attackers at k=5 by the 60 s counter reset".
- Table VII "/h" column dropped; "360 per hour" extrapolation removed; per-hour rate now from the 5.9 h replay (k = 1: 21/h).
- Abstract response sentence: Mirai miss explained ("floods form too few flows").

## Still-open items
- Text quoted non-ignored rows 84/12/0 per hour not in Table VII -> now counts 14, 2, 0 "(rows not shown)" (blocking_rates.md run1 simulation).
- 0.649 / 0.649: 0.6486 vs 0.6487, coincidence; stated in Table III caption.
- Garcia & Valeros: "14 of 36 datasets ... most common single practice" (CITATION_CHECK_R5.md: 11 flows, 9 dir, 7 metadata, 5 files, 4 none).
- LOCO: per-capture background counts (409-61,921) and paired differences (70.9-86.7 points, 9/9 positive; IoT-23 benign devices 7.6-46.7, 3/3) in text; full table in corrected_headline.md section 4.
- Sign test metric named (per-capture macro-F1 over classes present in both splits; sign_test.md).
- Ref [14] Zhao & Hassan: arXiv DOI added; ACM DOI 10.1145/3830454.3846576 still 404 on doi.org and Crossref (checked 3 Nov 2026).
- Traffic-MoE: cited as arXiv v2 (6 authors, "...Security Analysis", 8 Jul 2026; v1 had 5 authors and a shorter title). Text now "In a time-shift experiment"; 40/40 per class confirmed in v2 App. I earlier (CITATION_CHECK_FINAL.md). PR #263 and issue #262: open (checked 3 Nov 2026).
- One-core effect worded "less certainly ... about two standard errors".

## Cuts for space (no result lost except noted)
- Response: paragraphs condensed (motivation, ARP watcher, policies, trade-off, late blocks); "No MITM-ARP pair is blocked" (in table); sliding-horizon mention (results file only); 35% Mirai window share.
- Labels: file-label in-split sentences that repeat Table III (31.4%, 86.1%, 0.396/0.725); CSV paragraph tightened; one redundant clause in IoT-23.
- Live: drop-rule sentence (repeated in Response); CPU paragraph tightened.
- Splits: Check 2 recap points to Table I.
- Related: Hofstede survey pointer and its bib entry removed (no result).
- Bib: redundant "opened <date>" notes on GitHub refs; PR #263 keeps "open".
