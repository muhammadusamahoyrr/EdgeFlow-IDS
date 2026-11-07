# Final revision: responds to the 5 reviews (FINAL_REVIEW_*.md, FINAL_REVIEW_PLAN.md)

**Sources of truth**
- results\final\*.md: filelabel_decomposition, gap_decomposition, sign_test, blocking_rates, fidelity_all_runs
- paper\CITATION_CHECK_FINAL.md
- paper\refs_final_candidates.bib
- earlier results and FACTS.md

**Constraints**
- Never invent numbers.
- ≤ 8 pages including references, without font/margin/\vspace hacks.
- Escape every %.
- Back up to paper\backup_r9\ first.
- No git. No deletions.

## 1. Labels (M1): new headline
- **Lead with leave-one-capture-out (LOCO).**
  - On CIC-IoT2023, training on file labels makes the model flag 71–88% of background flows in an attack capture it never saw, against 0.5–5.4% with evidence labels.
  - Within the temporal split, it flags 31.4% of the Benign capture's own flows, against 1.0%.
  - Report the decomposition: 88.6% of the 71.8% pooled false positives come from background inside attack captures (0.861), and the Benign capture gives 0.314.
- **IoT-23.**
  - Within the split, the benign-device captures are at 4.7% flow-weighted (file labels) against 0.18% (Zeek).
  - Under LOCO on benign devices it is 23–47% against 0–17.5%.
  - State honestly that the Zeek-label model also has high FPR on some unseen malware captures (3-1 0.49, 42-1 0.42). So cross-capture generalisation is hard regardless of labels, and file labels make it much worse.
  - Replace "97–100% in every malware capture" as the headline with the LOCO numbers. The in-split number can stay once, labelled as in-capture.
- **Terminology.** "true macro-F1" → "macro-F1 against evidence labels" / "against Zeek labels".
- **Abstract and intro** must use the LOCO/out-of-capture framing.

## 2. Splits (M2, M3, claims M1)
- **BruteForce table** (gap_decomposition.md):
  - The test period has SSH .67:22 (38 flows; 475 in training) and RTSP .11 and .140:554 (567 flows; none in training).
  - The deployed tree (decision_tree.pkl) detects 32/38 SSH and 0/567 RTSP. Recall 0.053 is entirely the SSH tail.
  - Fix "one SSH pair in training, two RTSP pairs in test".
  - Make this a compact table or a single sentence.
- **Gap decomposition.**
  - BruteForce contributes 81% of the decision-tree gap.
  - Without it the gap is +0.030 [0.004, 0.187]. Over classes with ≥ 5 host pairs it is +0.023 [0.001, 0.081].
  - The coarse-cluster sign tests are not significant (capture: 7/10 positive, p = 0.34 sign / 0.19 permutation).
  - The CIC split claim is thus: a random split hides a change of target in one class. The general gap is small and not established under coarse clustering.
  - Remove "barely excludes zero" readings of the percentile intervals and say why: resamples miss classes, and one interval excludes its own point estimate.
  - Print "1 pair, no interval" instead of zero-width CIs.
- **Robustness filter.** Switch from ≥ 50 flows to ≥ 5 host pairs.
- **Model naming.** State which tree each number comes from. Use one tree name throughout: the "deployed tree" is decision_tree.pkl (54 features, EDGE_TREE). Keep the baseline tree only where Table perclass uses it, or switch the table to the deployed tree if simpler and the numbers exist.
- **Check 2 wording.** "Per-class temporal recall with host-pair counts; class presence; cluster-unit sensitivity" — not "temporal–random macro-F1 gap".

## 3. Live (M6)
- **Replace "live macro-F1 was stable" with fidelity on every run** (fidelity_all_runs.md):
  - The match rate is ≥ 0.9998 in all 7 non-enforced runs (verdict agreement ≥ 0.9997).
  - Live/offline flow count is exact at replay ≥ 69% of the original rate. At 63–68% it is +12% to +28%, and identical packet counts drop to 0.72–0.88, while macro-F1 does not move.
  - This is Check 3 applied to our own runs: macro-F1 hides fidelity loss.
- **Unpatched bug-check run.** One clause, if space allows: late-exported flows are missing from flows.csv (118 of 224 logged in the XSS window).
- **CPU budget (M7).** Name the confounds in Live itself, not only in Threats: replay rate shares the CPU, the harness versions differ, and the window sets differ.
- **Claims fixes:**
  - The one-core live flows cell is 142,725.
  - "Up to 82.5 s" → "a per-window median delay of up to 82.5 s".
  - The CPU "only in DDoS-SYN" statement must match the spill-over.

## 4. Response (M4, M5)
- **Selection rule.** State that it is degenerate: all 10 policies are within the coverage tolerance (max gap 0.0012), so the rule picked the largest k in the grid.
- **k-curve.** Present it as the result. The chosen policy is one point on it.
- **Rates.** Give false blocks per hour of capture time (k = 1 enforced: 360/h; 90 distinct benign IPs; 9 of 10 windows). Give the simulated per-k values: 384 / 84 / 12 / 0 per hour.
- **Windows.** Qualify the Mirai/Web miss as "within 60 s windows with per-window counters".
- **Mirai/Web loss points** (claims M3): Mirai is 0/7 from k = 5; Web is 0/3 from k = 10.
- **Bawany/Yan.** Cite them for OVS/OpenFlow drop rules only. The k-verdict gate is our design choice.

## 5. Related work and positioning (novelty review; use only CITATION_CHECK_FINAL.md verified entries)
- **New references** to add (wording per CITATION_CHECK_FINAL.md):
  - lyon2026iot23drift: IoT-23 temporal.
  - pekar2025early: partial flows; keep "under certain conditions".
  - zhao2026gidseval: streaming replay; arXiv, accepted CCS 2026.
  - hofstede2013realtime and velan2020impact: timeouts.
  - jacobs2022emperor: "can rely on shortcuts".
  - lanvin2023errors: label errors change scores.
  - andresini2021insomnia: drift in NIDS.
  - vormayr2020flows: optional.
- **Existing references:**
  - IoTGeM: use the exact App. A.3 wording (IoT-NID attack pcaps contain benign packets; IoTID20 labels them all attacks).
  - Traffic-MoE: give the exact split description (first 40% / last 40% of each class's time span; CIC-IoT2023 and CICIoMT2024; byte-level tokens).
- **Positioning sentence:** each pitfall is known individually; new here are the end-to-end audit of one detector, the per-capture CIC-IoT2023 label cost, the live/offline flow-fidelity check (which exposed the NFStream defect), and scoring false blocks. Use "to our knowledge" for the firsts.
- **Checklist novelty.** Say which checks are new (3, 4) and which apply known pitfalls (1, 2: Arp et al., Flood et al.).

## 6. Writing (writing review)
- Introduce the four-check audit early: in the intro, as the lead contribution, referring to Table VIII. Moving the table itself is optional.
- **Intro claim:** "run on two datasets" → "checks 1–2 on two datasets, 3–4 on CIC-IoT2023".
- **Abstract:**
  - Define background.
  - Fix the broken IoT-23 sentence.
  - Use "code, attacker evidence and result files are public", not "data".
  - Keep it ≤ 250 words.
- **Terms:** one name per concept.
  - random (not stratified/random mixed)
  - Benign (class) vs background (Benign flows inside an attack capture)
  - deployed tree
  - host-pair window
  - "keep-alive ping" instead of "background ping"
  - pps
  - consistent class names across tables and figures text
- **Tables:**
  - Define every abbreviation in its caption: Blk., BF/DS/DH/MA/Mi/Re, CIC, Flow CI, "3 win.".
  - Table VIII: raggedright columns, to avoid "Re-sponse".
- **Repetition:** state the CIC gap caveat once.
- **Space:** cut Setup cluster counts, the duplicated arpwatch/Rasheed/defect sentences and detailed Zeek-overlap counts.
- **Claims-review over-claims:**
  - O1 "mostly-background classes worst": remove; Mirai contradicts it.
  - O4: "Benign test flows", not background.
  - O5: say "temporal split".
- **Threats paragraph label:** rename the Threats "Conclusion" label to "Statistical conclusion".

## 7. Final checks
- Compile with MiKTeX (pdflatex, bibtex, pdflatex ×2).
- 8 pages.
- No undefined references, no overfull boxes, no bare %.
- Run check_refs.py.
- Do a number-preservation check vs backup_r9.
- Update FACTS.md (FINAL section).
- Write REVISION_FINAL_LOG.md.
- Re-read the abstract and intro as a skeptical reviewer: every number there must be in a results file.
