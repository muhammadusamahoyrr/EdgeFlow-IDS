# FINAL REVIEW: claims versus evidence (paper/sections/*.tex, main.pdf)

Scope: every number and quantitative/factual claim in abstract, intro, related (quantitative parts only), setup, labels, splits, live, response, discussion, and all tables. Each was traced to `results/**/*.md|json|csv`, `data/attackers.json`, or `paper/FACTS.md`. main.pdf (11:42) was spot-checked against the .tex (11:25–11:42); the text matches and there are no `??` references.
No paper file was edited.

**Numbers checked: about 420.** That is roughly 220 table cells (Tables background, filelabel, perclass, iot23split, repeats, blocking and kcurve, cell by cell) plus about 200 numbers in the running text. **About 400 match their source exactly, including rounding.** The rest are listed below.

Some checks went beyond reading result files:
- Replay rates and catch-up times were read from `results/live/*/windows.json`.
- Peak RSS and one-core CPU backlog were read from `results/live/*/resources.csv`.
- Packets dropped by false blocks were summed from `enforce_k1/enforcement.md`. They total 132, which matches the paper.
- The brute-force split was rebuilt from `data/processed/flows.parquet` (see M1).

---

## 1. MISMATCHES

| # | Location | Paper text | Source and value | Verdict |
|---|---|---|---|---|
| M1 | splits.tex l.35 (also abstract and discussion "three host pairs") | "It rests on only three host pairs (one SSH pair in training, two RTSP pairs in the test period)" | `iot23/cluster_sensitivity.md`, CIC section: temporal **test** set, BruteForce = **3** host-pair clusters (605 flows). `round2_checks.md`: temporal BruteForce, host pairs = 3. I rebuilt the 70% cut from `flows.parquet`; the cut index is approximate. The test half holds **38 SSH flows .65→.67:22**, plus 356 to .11:554 and 211 to .140:554. | **MISMATCH.** The test period contains all three pairs, including the tail of the SSH pair. It is not "two RTSP pairs". Training holds SSH only, which is correct. A plausible guess, not verified: the 0.053 recall (about 32 of 605 flows) may come mostly from the SSH tail. That would strengthen the paper's point, but the parenthesis is wrong. Suggest: "three host pairs (training: SSH only; test: the SSH pair's last 38 flows and two RTSP pairs)". |
| M2 | live.tex Table repeats, "One core" row, "Live flows" = "--" (caption: "--: not recorded") | "One core & 13,434 & -- & 21.5 ..." | `results/live/edge100/live_vs_offline.md`, DDoS-SYN row: Flows off/live **142,724 / 142,725** | **MISMATCH.** The value was recorded. Replace "--" with 142,725 and drop "--: not recorded". It also supports the "≥12,088 pps → within 0.02%" claim. |
| M3 | response.tex l.49 | "Mirai is lost from $k=3$, the web attackers from $k=5$" | `live/run1/block_curve.md`: Mirai 1/7 at k=3, 0/7 from k=5. Web 3/3 at k=3, 1/3 at k=5, 0/3 from k=10. Same in Table kcurve. | **MISMATCH (wording versus the table).** At k=3 Mirai is mostly lost (6 of 7), not lost. Web is partly lost at k=5 and fully lost only at k=10. Suggest: "most Mirai bots are lost at $k=3$ (1/7 blocked) and all from $k=5$; the web attackers drop to 1/3 at $k=5$ and 0/3 from $k=10$". |
| M4 | abstract | "an NFStream ordering defect that delayed verdicts by up to 82.5 s" | `results/nfstream_bug_check.md`: **median** verdict after flow end 82.5 s (SQLi, unpatched) and 49.2 s (XSS). Patched: 15.6 / 15.5 s. | **MISMATCH in what is measured.** 82.5 s is a per-window **median** that includes the 15 s idle timeout. It is not a maximum, and not the delay the defect added (about 67 s). "Up to" reads as a maximum. Suggest: "that raised the median verdict delay after flow end to 82.5 s (15.6 s once fixed)". |
| M5 | live.tex l.43 | "a backlog kept the CPU at about 100% for 45–60 s after the flood" | `edge100/resources.csv` against `edge100/windows.json` replay_end: CPU ≥ 98% until **53.4 s** after the DDoS replay ended, then 15%, then about 1%. There is only one one-core run. | **Minor.** The value is consistent, but a range is reported for a single measurement. Suggest "for about 54 s". |

## 2. UNSOURCED claims (no results/ file; FACTS.md only, or not found)

| # | Location | Claim | Status |
|---|---|---|---|
| U1 | live.tex l.11 | DDoS-SYN window "388,686 packets in 22.31 s, about 17,423 packets/s"; Mirai "about 4,782 packets/s" | 388,686 is confirmed (`windows.json`). **22.31 s and 17,423 appear only in FACTS.md** ("from the fact-check"). `repeats.md` gives "22.3 s, about 17,400 pps", and 388,686/22.31 = 17,422.0, so the precision is not reproducible from the stated numbers. 4,782 equals 286,937 packets / 60 s window, so it can be derived but no file records it. Add both to a results file or round them ("about 17,400"). |
| U2 | live.tex l.9 | window "starts 1 s after the last training flow started"; "counters are quiet for 5 s" | No results file. FACTS says only "cut just after the train/test boundary". `caught_up_after_gap_s` ≥ 5.0 in `windows.json` is consistent with the 5 s figure. |
| U3 | live.tex l.60 | "A two-flow synthetic pcap reproduces the defect offline (export order A, B, A unpatched; B, A, A patched)" | FACTS.md only. Not in `nfstream_bug_check.md`. |
| U4 | setup.tex l.3 / l.5 | "about 5.17 GB"; "files over 300 MB trimmed to first 10^6 packets"; "Okiru captures (all at least 1 GB)" | FACTS.md only (pointers to src scripts and docstrings). Not checked against data. |
| U5 | live.tex l.7 | Mininet 2.3.0, i5-8350U, micro-batch 256 flows / 50 ms, 64 MB buffer | FACTS.md only (configuration, not results). |
| U6 | intro.tex l.3 | Tang et al.: "hold-out F1 0.97 ... recall fell to 0.0095" | External citation. FACTS.md and CITATION_CHECK only. Not verified against the cited paper in this audit. |
| U7 | response.tex Table kcurve caption | "Time: median time from a blocked attacker pair's first flow to its block" | Values match `block_curve.md` ("median time to block (s)"). The definition ("from first flow") is not stated in the results file. **Uncertain.** |
| U8 | discussion.tex l.41 / abstract | "the scripts that reproduce every number"; abstract "Code, data and the audit scripts are public" | `.gitignore` excludes `data/raw/`, `data/processed/`, `*.parquet`, `*.pkl` and `results/live/*/flows.csv`. Only `data/attackers.json` and result summaries are tracked. See over-claim O3. |

## 3. INCONSISTENCIES between sections

| # | Locations | Conflict | Fix |
|---|---|---|---|
| I1 | intro.tex l.12 against discussion.tex l.5 and l.31 | Intro contribution 4 says the four-check audit was "run on two datasets". Discussion says "Checks 1 and 2 were run on both datasets" and "the live and response steps only on CIC-IoT2023". | Intro: "...implemented as scripts in the repository; Checks 1–2 run on two datasets, Checks 3–4 on CIC-IoT2023". |
| I2 | abstract against response.tex Table blocking | The abstract says "requiring 10 verdicts blocked none". The evaluated policy is k=10 **with MITM-ARP verdicts ignored**, and "none" means no *benign* pair (it did block 9 attacker pairs). | "requiring 10 verdicts per pair (ignoring MITM-ARP verdicts) caused no false blocks but missed...". |
| I3 | splits.tex l.3 and l.35 (tree identity) | The paragraph and Table perclass use the **baseline** decision tree. The host-pair CIs quoted in l.35 come from the **deployed** tree (`round2_checks.md`, "edge tree"): BruteForce 0.053 [0.000, 0.842], Mirai 0.90 [0.571, 1.000], MITM 0.16 [0.000, 0.375]. The point values agree at 2 decimals, so this is cosmetic. Setup l.9 says only Section splits uses the baseline tree. | Add "(deployed tree)" to the CI sentence. |
| I4 | live.tex Table repeats, "Half core 1" row | The same quantity, live macro-F1 over the same three windows (json 0.9175), appears as "0.918" (own) and "0.9175" (3 win.) in one row. The other half-core rows read 0.917 / 0.9172 and 0.917 / 0.9173. | Cosmetic. Use one precision for these rows. |
| I5 | labels.tex l.59 | "4.6% in the three benign-device captures" is the **unweighted mean over captures** (`fpr_per_capture.md`: 0.046; per capture 0.7%, 12.1%, 1.0%). "Mean 0.993" is labelled as a mean; the 4.6% is not. | "(mean over captures 4.6%; 0.7–12.1%)". |
| I6 | setup.tex l.9 | "all other results use the deployed tree". The official-CSV results (labels l.61) necessarily use a different tree and an RF on the 39 CSV features. | Add "except the released-CSV check". |
| I7 | Source-side (not the paper) | `results/iot23/match_rates.md` still says "14,394 Zeek DDoS connections on **317** distinct 5-tuples". `zeek_agreement.md` and the paper say 211 (R5 correction). FACTS C2 lists the decision tree as "227 KB", but `baseline_temporal/report.md` says 222 (KiB). FACTS C3 says "138 s after the window", but `windows.json` gives 137.9 s **after the gap**. FACTS "Limitations: One dataset" is stale. | The paper uses the corrected values. Regenerate or annotate `match_rates.md` and tidy FACTS.md so reviewers who open the artifact do not find contradictions. |

## 4. OVER-CLAIMS (with suggested wording)

| # | Location | Paper text | Evidence | Suggested wording |
|---|---|---|---|---|
| O1 | labels.tex l.61 | "the classes that are mostly background are the ones it handles worst" | `official_csv_baseline.md`, stratified tree recall: BruteForce 0.434 and Web 0.374 are worst. But **Mirai (93.7% background) scores 0.994**, and MITM-ARP (97.6% background) scores 0.743, above Recon (30% background, 0.706). | "two of the mostly-background classes, brute force and web, are the ones it handles worst" |
| O2 | abstract and splits.tex l.35 | "brute-force recall falls from 1.00 to 0.05 when the target changes from SSH to RTSP" (causal) | See M1. The test set also contains SSH flows, the effect rests on 3 pairs, and the CI is [0.000, 0.842]. The body hedges this ("case study"); the abstract does not. | Abstract: "...falls from 1.00 to 0.05 after the target changes from SSH to RTSP (a three-host-pair case study)". |
| O3 | abstract | "Code, data and the audit scripts are public" | Flows, pcaps, models and live `flows.csv` are git-ignored. The public part is code, `attackers.json`, configuration and result summaries. The datasets come from their authors (discussion l.45). | "Code, attacker evidence, result files and the audit scripts are public." The same applies to "scripts that reproduce every number" in the artifact section: the live numbers need the git-ignored `flows.csv` files, so say "given the datasets and the live logs" or release the logs. |
| O4 | labels.tex l.32 | "the file-label model calls 38,034 of 52,993 **background** test flows attacks" | 52,993 is **all** Benign test flows, including the Benign capture (`file_label_baseline.md`), not only background inside attack captures. | "...38,034 of 52,993 Benign test flows..." |
| O5 | abstract | "training on file-name labels yields a true macro-F1 of 0.396 and flags 71.8%..." | These are temporal-split, deployed-tree numbers. Stratified gives 0.426 and 70.2%. | Add "(temporal split)", or give both. |
| O6 | live.tex l.43 | "The CPU budget mattered only in the DDoS-SYN window" | The same paragraph reports that the one-core backlog spilled into the BruteForce window (mean CPU 40.6%). Only the delay stayed normal (15.7 s). | "The CPU budget affected verdict delay only in the DDoS-SYN window". |

No over-claim was found on the main hedged results. The CIC paired gap ("likely positive but not established under coarser clustering"), the IoT-23 non-replication, "submitted" (not merged) PR #263, "to our knowledge ... previously undiagnosed" and "late, not lost" are all worded in line with the evidence.

## 5. Verified OK (summary by section)

- **Abstract and intro:**
  - 54 features.
  - 91–98.5% background (XSS 0.985 … BF 0.909).
  - 0.396 / 71.8% against 0.725 / 3.8%.
  - IoT-23 97–100% (min 0.9724 for 3-1).
  - 1.00 → 0.05.
  - 60 / 1,674 (3.6%).
  - #262 and #263.
- **Setup:**
  - 0.731, RF 0.737 (20,849/222 = 94×; 7.826/0.136 = 58×), HGB 0.714 / 7.6%.
  - Validation FPR 1.3% → 5.7%.
  - 1,767 nodes, 222 KiB, 0.725 / 3.8%.
  - NSGA 14/54, 0.723, 211 KiB.
  - 3.9%.
  - 600,050 / 257,156.
  - 857,206 and 511,527 (sum of the per-capture flows checked).
  - Flow CI [0.712, 0.742] against [0.577, 0.823].
  - Clusters 4,641 / 3,465 / 3,858 and 348,350.
  - IoT-23: 756,306, 99.99%, 38 dropped; 35.2%, 270 (0.04%), 211, 14,159.
- **Labels:**
  - Table background: all 18 values, plus the attacker evidence in `attackers.json`.
  - 13.4%.
  - Table filelabel: all 24 values.
  - 65,525 and .36.
  - IoT-23: 0.999 / 0.055, 63.1%, mean 0.993, 0.709 / 0.049, 95% (0.9515), 0.169.
  - CSV: 483,053, 39, 0.749 / 0.803, acc 0.82 / 0.87, 0.727 / 0.778, recalls 0.43 / 0.41 and 0.37 / 0.35.
- **Splits:**
  - 0.869 [0.735, 0.877], seeds 0.8535–0.8726, 0.731 [0.577, 0.823], 1.1% / 3.9%, 0.814.
  - +0.137 [0.024, 0.278] and +0.142 [0.025, 0.287], 0.1%.
  - [0.002, 0.165], [0.001, 0.151], [−0.004, 0.164], 76–97%.
  - Table perclass: all 27 values.
  - 36.1% (92,766), 0.725 → 0.604, 0.700 → 0.690, 0.919 → 0.851, 10 Mirai.
  - MITM-ARP precision 0.01, recall 0.16.
  - Table iot23split: all values.
  - −0.017 [−0.039, −0.009], +0.214 [−0.014, 0.293], 91.5% / 0.4%, 350, [0.576, 0.983], [0.469, 0.984], [−0.130, 0.114], [−0.078, 0.005].
  - 63 / 2 flows, 36.5% / 68%, 0.974, 0.918 [0.735, 0.955], 0.863 → 0.809, 0.885 → 0.733.
- **Live:**
  - 148,779 / 148,884 / 148,756 / 23 / 128.
  - 96.62–100% and 97.63–100%.
  - 0.804, [0.457, 0.823] and [0.456, 0.822].
  - Packet ratio 0.9919–1.0064, 0 drops, 12,271 pps (5.9 Mbps), 3,685 pps (16.2 Mbps).
  - 0.44 ms, 209 flows.
  - Delay 15–35 s (15.2–35.4).
  - Table repeats: all values except M2.
  - Replay 9,045–13,434 and 2,664–3,685 pps, 52–77%.
  - +0.02%, +12%, +29%.
  - 0.8038–0.8043, 0.9155–0.9175, 0.9284, 0.0125.
  - 40.6% / 0.8%, 15.7 s, 110–163 s (109.6 / 137.9 / 162.7).
  - RSS 980–1,025 MB (980.1 … 1,024.7).
  - 82.5 → 15.6 and 49.2 → 15.5 s, 64.5%.
- **Response:**
  - ARP: 1 alert at 1.7 s, 0 in the other 9 windows.
  - Validation 128 / 1 false blocks, 0.995 / 0.996.
  - Table blocking: all values.
  - 7 Mirai bots, 99,644 packets (34.7%).
  - 12.5% and 6.8%.
  - Triggers 32 / 21 / 5 / 1 / 1; 7 + 14 in eight windows; roles 56 / 2 / 2.
  - 132 packets.
  - 133k / 30k / 217 / 0.
  - Table kcurve: all 84 cells.
  - 64 → 37.
  - 11.1%, 98.1%, 10.5%, 10.3 / 0.8.
  - 0.503 / 0.342 and 0.707 / 0.698.
- **Discussion:** the checklist claims, "ran once" and "three host pairs" are consistent with the above, except I1.

Note (uncertain, not an error): the run-1 blocking simulation counts 212,965 attack flows (`blocking_accounting_r6.md`; 209,001 of them DDoS-SYN). These are drawn from `flows.csv` within ±1 s of each window and include boundary-spanning flows. The fidelity check uses 148,884 live flows with spanning connections removed. The two analyses therefore use different flow sets. The paper does not say this. Consider one clause in "Late blocks".
