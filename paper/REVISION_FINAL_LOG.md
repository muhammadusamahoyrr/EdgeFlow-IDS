# Final revision log (spec: REVISION_FINAL.md)

Backup: `paper\backup_r9\` (sections\, main.tex, refs.bib), taken before any edit.

**Result**
- 8 pages including references.
- Abstract: 250 words (wc after stripping LaTeX markup).
- No undefined references or citations. No overfull boxes.
- No bare `%`, checked with a script over every non-comment line.
- check_refs.py: 47 cited, 47 in bib, none missing or unused, no TODO.
- No font, margin or `\vspace` changes. Tables stay `\footnotesize`. The only preamble change is `\usepackage{array}`, needed for the ragged-right table columns.
- Remaining underfull lines are minor: Setup line 1, the defect paragraph's run-in head, and reference [44].

## What changed, by section

### Abstract (rewritten)
- Reframed around out-of-capture (LOCO) results:
  - CIC-IoT2023: 71–88% vs 0.5–5.4%.
  - IoT-23 benign devices: 23–47% vs 0–17.5%.
- Defines "background" at first use.
- The broken IoT-23 sentence is fixed: "the gap comes from classes missing from one half of the split".
- Splits: the brute-force case is "on three host pairs" and "makes up most of the random–temporal gap, and the rest is small".
- Live:
  - 82.5 s is described as "a window's median verdict delay".
  - Adds the flow-splitting finding.
- Response: "60 false blocks in ten minutes of traffic". The k=10 claim is qualified "within 60 s windows".
- Ends with "Code, attacker evidence and result files are public."

### Intro (rewritten)
- Paragraph 2 is the positioning paragraph:
  - each pitfall is known on its own (new citations);
  - "we do not claim a new failure mode";
  - our work follows one detector end to end.
- The four-check audit is now the lead contribution, and its table (`tab:checklist`) has moved from the Discussion into the Intro, so it appears as Table I on p.1–2.
- The bullet says Checks 1–2 were run on both datasets and Checks 3–4 on CIC-IoT2023. It also says Checks 1–2 apply known pitfalls (Arp et al., Flood et al.) and that Checks 3–4 go past the offline evaluation.
- Added a bullet for the split check.
- "To our knowledge" is used for the per-capture CIC-IoT2023 background share and for the NFStream defect diagnosis.
- Table I:
  - ragged-right p-columns, so "4 Re-sponse" no longer hyphenates;
  - Check 2 reads "Per-class temporal recall with host-pair counts; class presence; cluster-unit sensitivity; boundary-spanning share";
  - the "Caught here" column has headline numbers.

### Related work
- Labels:
  - + lanvin2023errors ("correcting them changes detection scores");
  - + jacobs2022emperor ("can rely on shortcuts rather than attack behaviour").
  - The IoTGeM sentence was replaced by the App. A.3 wording from CITATION_CHECK_FINAL.md, cited as `\cite[App.~A.3]{kostas2024iotgem}`.
  - Removed the second Garcia & Valeros quote ("sometimes contain errors…", Sec. 2.2) for space.
- Splits:
  - + andresini2021insomnia;
  - + lyon2026iot23drift;
  - the Traffic-MoE split is described exactly as in CITATION_CHECK_FINAL.md: first/last 40% of each class's time span, CIC-IoT2023 and CICIoMT2024, byte-level flow tokens.
- Live: + hofstede2013realtime, velan2020impact, pekar2025early ("under certain conditions" kept) and zhao2026gidseval (graph-based NIDS, 18 detector–dataset pairs).
- Response:
  - Bawany/Yan are now cited only for OVS/OpenFlow drop rules, and k-gating is stated as our design choice (in Sec. VII).
  - The arpwatch citation was moved to Response only, removing the duplicate.

### Setup
- One tree. "Deployed tree" is defined here and used throughout. The baseline tree (0.731) is gone, and RF/HGB are compared against 0.725.
- "Stratified random" became "random" everywhere, including the IoT-23 table.
- Defined "host pair" and "benign-device captures".
- Cut:
  - union cluster counts;
  - Zeek-overlap details (35.2%, 14,394 rows / 211 5-tuples / 14,159);
  - `\texttt{statistical_analysis=True}` (caused an underfull line).
- The flow-level CI is now the deployed tree's: [0.702, 0.741] vs [0.568, 0.822] (cluster_ci.md).
- Noted that the released-CSV check uses a different tree (claims I6).

### Labels (rewritten around LOCO)
- New paragraph "The cost of file-name labels on unseen traffic":
  - explains why in-split FPR is partly circular;
  - leads with LOCO;
  - states that holding out the single Benign capture gives FPR 100% by construction;
  - in-split numbers: Benign capture 31.4% vs 1.0%, pooled 71.8% with 88.6% of FPs from background at 86.1%.
- "true macro-F1" became "macro-F1 against evidence labels". 38,034 of 52,993 are now called "Benign test flows" (claims O4). The temporal split is named (claims O5).
- Table `tab:filelabel` rebuilt:
  - columns: macro-F1 vs file / vs evidence-Zeek; Benign FPR on background and on benign captures;
  - rows: temporal and LOCO, for both datasets.
  - The random-split rows were cut; their pooled FPR is given in the text.
- IoT-23 paragraph:
  - benign devices 4.7% vs 0.18% in-split, 23.4–46.7% vs 0–17.5% under LOCO;
  - states plainly that the Zeek-label tree also fails on unseen malware captures 3-1 (49.1%) and 42-1 (42.0%);
  - "97–100%" is kept once, explicitly as the in-capture number.
- Table `tab:background` shows percentages. The MAC and SQLi cells were shortened.
- "The benchmark as distributed" was shortened, and the over-claim "mostly-background classes handled worst" (O1) was removed.

### Splits (rewritten)
- Deployed tree throughout. Table `tab:perclass` now has, per class:
  - temporal host pairs;
  - F1 random/temporal (deployed tree, gap_decomposition.md);
  - temporal recall with host-pair CI;
  - "1 pair, no interval" for DoS-HTTP, and "every pair 1.000" for DDoS-SYN and Recon instead of zero-width CIs.
- Fig. `split_recall.png` was dropped. It showed the baseline tree, and its content is now in the table.
- Gap decomposition:
  - BruteForce is 78% of the summed difference;
  - without it +0.036 [0.007, 0.199];
  - with ≥5 host pairs +0.030 [0.004, 0.098] (this replaces the ≥50-flow filter);
  - capture-level sign test 6/9 positive, p = 0.51 (sign) and 0.18 (permutation).
- The coarse-cluster percentile intervals are no longer read as evidence. The text says why: 76–97% of the resamples miss a class, and the capture-level interval [0.360, 0.719] excludes its own point estimate 0.725.
- The claim is now "a random split hides a change of target in one class; a general gap is small and not established under coarse clustering".
- The BruteForce facts are fixed: training holds SSH .67:22 (475 flows); the test period holds the last 38 SSH flows plus 567 RTSP flows to .11/.140:554. The deployed tree detects 32/38 SSH and 0/567 RTSP, so the recall 0.053 comes entirely from the SSH tail.
- The Rasheed "blindness" analogy was removed (duplicate of Related).
- The IoT-23 paragraph was cut by about half:
  - kept: missing classes, near-singleton host pairs, originator and capture CIs that include zero, the C&C spanning effect;
  - it ends with the Check 2 requirements.

### Live
- Opens with "What an offline score hides".
- Defines "verdict" and "pps".
- Flow-by-flow match is now on every run: match ≥ 99.98% and same verdict ≥ 99.97% in all 7 non-enforced runs.
- Table `tab:repeats` rebuilt:
  - columns: replay pps, % of original, live DDoS-SYN flows, same packets, delay, 3-window macro-F1 (4 decimals);
  - the one-core live flows cell is now 142,725;
  - the "own" macro-F1 column was removed.
- New paragraph "Repeats: macro-F1 hides flow splitting":
  - at ≥69% of the original rate, live flows are within 0.02%;
  - at 63–68%, +12–29% flows and same packets 0.71–0.88;
  - macro-F1 does not move;
  - "This is Check 3 applied to our own runs".
- The CPU paragraph:
  - says the budget affected *delay* only in DDoS-SYN but the load spilled into BruteForce;
  - names the confounds in Live itself: shared CPU and replay rate, the harness version, the window sets.
- Defect paragraph:
  - "per-window median delay";
  - the unpatched run clause now reads 118 of 224 XSS flows (64.5% of packets).
  - The duplicate "changes only export timing" sentence was removed.
- "Background ping" became "keep-alive ping". "Quiet meters" became "Idle meters".
- Removed numbers that were unsourced in a results file (claims U2/U3): the 30 s / 5 s harness waits and the A, B, A synthetic-pcap sentence.
- The footnote no longer mentions the uncited #193.

### Response
- Opens with "What a per-flow FPR hides". Defines host-pair window and eligible benign host-pair windows in the text rather than the caption.
- The selection rule is stated as degenerate: all ten policies lie within 0.0012 of the best share, so the rule picked the largest k in the grid. The k-curve is now presented as the result, with the enforced policy as one point on it.
- Table `tab:kcurve`:
  - "Blk." (= Att. + False) was replaced by "/h" (false blocks per hour of capture time);
  - every abbreviation is defined in the caption.
- Text:
  - 384 / 84 / 12 / 0 per hour (MITM-ARP not ignored);
  - Mirai 1/7 at k=3 and 0/7 from k=5; Web 1/3 at k=5 and 0/3 from k=10;
  - losses are qualified "within 60 s windows with per-window counters".
- Table `tab:blocking`: added a /h column (360, 0), and the abbreviations are defined.
- Text: 360 per hour, 90 distinct IPs, 9 of 10 windows.

### Discussion
- The checklist subsection was removed: the table moved to the Intro, and the novelty statement is in the Intro bullet.
- Threats:
  - "Conclusion" became "Statistical conclusion", with updated content (three pairs, a small gap beyond it, LOCO scope);
  - Construct notes that per-hour rates extrapolate and depend on the counter reset;
  - the WSL2/tcpreplay CPU point moved into External.
- Conclusion mentions the flow-splitting finding and persistent counters.
- The Artifact section no longer over-claims: it says the scripts recompute the offline numbers from the datasets, and that the live numbers also need the live flow logs, which are not in the repository.

## Sources of every new number

| Number(s) in paper | Source |
|---|---|
| 71.4–87.8%, 0.5–5.4%, 1.5%, (100%) | results/final/filelabel_decomposition.md, CIC B (LOCO) |
| 86.1%, 31.4%, 4.8%, 1.0%, 88.6%, 71.8%, 38,034/52,993, 70.2%, 1.1% | filelabel_decomposition.md, CIC A. 4.8% = 1,897/39,124 = 4.85% |
| 99.97%, 4.7%, 3.4%, 0.18% | filelabel_decomposition.md, IoT-23 A (141,483/141,525; 107/2,271; 4,880/141,525 = 3.45%; 4/2,271) |
| 23.4–46.7%, 0–17.5%, 9.4–99.95%, 0–49.1%, 49.1%, 42.0% | filelabel_decomposition.md, IoT-23 B |
| 97–100% (in-capture) | filelabel_decomposition.md, IoT-23 per capture, temporal (min 0.9724) |
| 5.5%–99.9% IoT-23 background | earlier paper text (0.055/0.999), results/iot23/label_shares.md |
| Table perclass: F1, pairs, 78%, +0.036 [0.007, 0.199], +0.030 [0.004, 0.098], 0.867/0.725 | results/final/gap_decomposition.md (deployed edge tree) |
| 475, 38, 356+211 = 567, 32/38, 0/567 | gap_decomposition.md, BruteForce per target |
| recall and host-pair CIs per class | results/round2_checks.md (edge tree) |
| [0.733, 0.875], [0.568, 0.822], [0.702, 0.741] | results/cluster_ci.md (edge tree) |
| [0.360, 0.719], 76–97% | results/cluster_sensitivity_cic.md (via FACTS R8) |
| 6/9, p = 0.51 / 0.18 | results/final/sign_test.md (capture, deployed tree) |
| ≥99.98% match, ≥99.97% verdict, 142,725, 17,424 pps (17,423.6), 4,782 pps, 70.4/66.6/62.8/77.1/69.4/67.9/71.2%, same pkts 1.000/0.877/0.708/0.876, 0.71–0.88, 118 of 224 | results/final/fidelity_all_runs.md |
| 360/h, 90 IPs, 9 of 10 windows, 384/84/12/0, 222/30/6/0, 0.0012 | results/final/blocking_rates.md |
| 4–5 live Mirai flows | results/live/perclass_counts.md (as before) |

Percentages written from fractions (e.g. 0.2342 → 23.4%; 0.628 → 62.8%; background shares 0.985 → 98.5%) are rounding conversions of the listed sources. The number-diff script flags these as "not verbatim".

## Numbers removed, and why
- **Baseline-tree numbers:** 0.731, 0.869, [0.577, 0.823], [0.735, 0.877], +0.137 [0.024, 0.278], 0.8535–0.8726, 3.9%, [0.712, 0.742], and Table perclass at 2 decimals. Reason: one tree throughout (spec §2). Deployed-tree equivalents are used.
- **Coarse-cluster percentile CIs:** [0.002, 0.165], [0.001, 0.151], [−0.004, 0.164]. Reason: no longer read as evidence (spec §2). Replaced by the sign test.
- **Macro-F1 over classes with ≥50 test flows (0.814).** Reason: replaced by the ≥5-host-pair filter.
- **Random-split rows of Table filelabel:** 0.617, 0.426, 0.439, 0.867, 0.692, 0.149, 0.167, 0.863, 98.4%, 3.7%. Reason: space; the text keeps the random-split pooled FPR (70.2% vs 1.1%).
- **IoT-23 summary numbers:** 63.1%, mean 0.993, 0.709/0.049, "95% capture 1-1", 98.5% pooled. Reason: superseded by the (i)/(ii) decomposition.
- **IoT-23 split paragraph:** +0.214 [−0.014, 0.293]; marginal common-class CIs [0.919, 0.983], [0.904, 0.969], [0.576, 0.983], [0.469, 0.984]; 350 clusters; 63/2 test flows; 0.974; [0.735, 0.955]; 0.863 → 0.809. Reason: space and the writing review. The conclusions are kept.
- **Setup:** 35.2%, 14,394, 211, 14,159 (Zeek overlap) and 4,641/3,465/3,858/348,350 (cluster counts). Reason: spec §6 space.
- **CSV paragraph:** 483,053 rows, accuracy 0.82/0.87, row-order split 0.727/0.778. Reason: space.
- **Live:**
  - offline/live-only counts 23/128 and host-pair CIs [0.457, 0.823], [0.456, 0.822]: space;
  - 388,686 packets in 22.31 s and 9,045–13,434 / 2,664–3,685 pps: the table now gives the per-run rates;
  - 5.9/16.2 Mbps: space;
  - the "own" macro-F1 column (0.804/0.810/0.918…) and the Mirai 0.75 → 0.80, +0.006, 0.0125 explanation: replaced by one sentence;
  - 30 s / 5 s waits and the synthetic-pcap sentence: not in any results file (claims U2, U3).
- **Response:**
  - Blk. column (83, 56, 23, 14, 10, 9, 8): it equals Att. + False;
  - trigger counts 32/5/1/1 and roles 56/2/2, 132 packets, 10.5% and 10.3/0.8 points: space;
  - 98.1%: space.
- **Related:** Garcia & Valeros Sec. 2.2 quote. Reason: space.

## Citations
- Added from refs_final_candidates.bib, with fields unchanged except trimming:
  - lyon2026iot23drift and pekar2025early: arXiv note dropped, because they are published;
  - lanvin2023errors: series, publisher and address dropped, as for the other LNCS entries in R9;
  - zhao2026gidseval: kept as arXiv with the acceptance note;
  - hofstede2013realtime, velan2020impact, jacobs2022emperor, andresini2021insomnia: unchanged.
- **Not used:** vormayr2020flows (optional in the spec). It was added, then removed again to meet the 8-page limit; the entry is not in refs.bib.
- **Reworded per CITATION_CHECK_FINAL.md:**
  - kostas2024iotgem: App. A.3 wording;
  - zhou2026trafficmoe: exact split description;
  - bawany2017ddos and yan2016sdn: drop rules only.

## Spec items not done, or done differently
- **Spec §2, decision-tree figures.** The spec quotes decision-tree values: 81%, +0.030 [0.004, 0.187], +0.023 [0.001, 0.081] and 7/10 with p = 0.34/0.19. Because the spec also asks for one tree name throughout, the paper uses the deployed-tree values from the same files: 78%, +0.036 [0.007, 0.199], +0.030 [0.004, 0.098] and 6/9 with p = 0.51/0.18. The conclusions are identical.
- **Spec §3, live flow-count ranges.** The spec gives the run-level range "+12% to +28%" and "0.72–0.88". The paper reports the DDoS-SYN window, which is what Table repeats shows: +12–29% and 0.71–0.88 (fidelity_all_runs.md, per-run-and-window rows).
- **Spec §3, CPU backlog.** "About 100% for 45–60 s" is kept from FACTS. The claims review notes that it is a single run, measured at 53.4 s in resources.csv, which has no .md summary.
- **Figures.** Fig. live_delay was not regenerated. Its legend still reads "1/2 core" and its axis labels are abbreviated; the caption explains "1/2 core". Fig. split_recall was removed (see Splits).
- **Spec §5, vormayr2020flows.** Optional, and dropped for space.
- **Number-preservation check.** Done (script in the session scratchpad: revfinal_numdiff.py). The removed and added numbers are listed above.
