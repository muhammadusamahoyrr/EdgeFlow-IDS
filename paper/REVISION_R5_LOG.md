# Revision R5 log (2 Nov 2026)

Spec: paper/REVISION_R5.md. Backup of the R4 state: paper/backup_r4/ (sections/*.tex, main.tex, refs.bib).
Sources used: paper/CITATION_CHECK_R5.md, results/iot23/{fpr_per_capture, zeek_agreement, common_class_ci}.md,
results/paired_diff.md, results/blocking_accounting.md, results/live/edge100/live_vs_offline.json (Mirai 2,664 pps), paper/FACTS.md.

**Final PDF: 8 pages including references.** No undefined references or citations, no overfull boxes.
check_refs.py: 39 cited, 39 in bib, none missing, none unused, no TODO.

## Changes per section

### abstract.tex
- IoT-23 now leads with FPR: "In a robustness test on IoT-23 with the dataset authors' own Zeek labels (and our mapping of malware families to classes), the file-label tree flags 97--100% of background flows in every malware capture." The macro-F1 0.169 and pooled 98.5% were dropped from the abstract (kept in the body).
- Response: "60 benign host pairs (3.6% of those eligible)".
- Cut "which makes class presence and host-pair intervals part of the check" (space).

### intro.tex
- Tang et al.: "hold-out F1 0.97 whose attack recall fell to 0.0095 in operational validation on a labelled laboratory capture" (was "in deployment").
- Contribution 1 leads with FPR: CIC 71.8%; IoT-23 framed as a robustness test, 97--100% of background flows in every malware capture. "The CSVs released with CIC-IoT2023" (no "official").
- Cut the closing sentence that previewed Section V (space).

### related.tex
- Garcia & Valeros: "most of the datasets they analysed".
- Rasheed & Alobaedy: exact quote "specific behaviour changes, such as total blindness, sensitivity inflation and relatively stable detection".
- Cut "Late idle expiry in NFStream was reported before without a cause" (duplicate of the live.tex footnote).

### setup.tex
- IoT-23 benign captures: "three benign captures of real, uninfected IoT devices (Philips Hue bridge, Amazon Echo, Somfy smart door lock; of 7-1 only its Somfy-01 part)". "honeypot" removed.
- Zeek agreement added: 35.2% of flows overlap >1 Zeek row, only 270 (0.04%) overlap rows of >1 class; supports differ because flows and connections are different units; 14,394 DDoS rows on **211** 5-tuples (was 317) become 211 flows, one covering 14,159 rows; "The exporter thus changes what the benchmark contains."
- Detector paragraph tightened (same numbers).

### labels.tex
- "Replication on IoT-23" renamed "Robustness test on IoT-23": IoT-23 ships per-connection labels, so nobody labels it by file name; it tests the file-label result with labels that are not ours, not evidence of current practice. Mapping stated as our choice.
- Per-capture FPR: 97--100% in every malware capture (mean 0.993), 4.6% in the three benign-device captures; macro-averaged FPR 0.709 vs 0.049 (Zeek-label tree); pooled 98.5% explained as dominated by capture 1-1 (95% of Benign test flows). Macro-F1 0.169 kept.
- Table II caption: "FPR pooled over all Benign test flows."
- CSVs: per-pcap files (CSV/CSV), 39 features, no label/address/timestamp column, label = file name; MERGED_CSV adds Label but rows merged and shuffled and label = attack name; obtained from Hugging Face mirror bencorn/CIC-IoT-2023 whose layout matches the README. "official" removed.

### splits.tex
- "Intervals overlap" reasoning replaced by the paired bootstrap: +0.137 [0.024, 0.278] for the decision tree in Table III and +0.142 [0.025, 0.287] for the deployed tree, 0.1% of resamples <= 0. Both are given because the paragraph reports the decision tree's 0.869/0.731, while the spec names the edge tree.
- Rasheed: "a change of target within one capture session, not drift, but its effect is analogous to the ``blindness''...".
- IoT-23 common classes: 0.973 [0.919, 0.983] vs 0.956 [0.904, 0.969], paired -0.017 [-0.039, -0.009], "slightly but consistently higher"; all classes +0.214 [-0.014, 0.293], not reliably above zero.
- Cut the temporal C&C flow-vs-host-pair CI example and the IoTGeM agreement sentence (space; IoTGeM remains in Related Work).

### live.tex
- Pekar & Jozsa: exact quote "the specific mechanisms employed for updating and terminating flows"; logic fixed: the defect changes neither flow boundaries nor features, so it does not explain their value differences; it shows that the update/termination mechanism can change export timing without changing any offline feature or score, which offline comparisons such as theirs cannot see.
- One-core 0.810 explained: Mirai window replayed at 2,664 vs 3,685 pps, 5 Mirai flows instead of 4, extra flow correct, Mirai F1 0.75 -> 0.80, +0.006 macro-F1; flow splitting, not CPU. No-limit spread 0.8038--0.8043.
- "This step uses CIC-IoT2023 only" removed (stated once in Threats, per spec Section 4).
- Tightened: Delay paragraph, fidelity conclusion, harness sentence, memory sentence, CPU sentence, footnote.

### response.tex
- Garcia/Akbari sentence replaced with the spec wording ("strong consequences once detections drive IP blocking"; "severe consequences").
- Selection-criterion sentence: DDoS-SYN, DoS-HTTP and Recon pairs are blocked at every k, so k trades Mirai, web and brute-force coverage against false blocks.
- Table VI (enforced runs): "Correct" column replaced by Attackers 19/26 and 9/26; False shown as 60/1,674 and 0/1,675.
- Live results: 60/1,674 = 3.6%, DDoS-SYN window 12.5%, DoS-HTTP window 6.8%; trigger verdicts DoS-HTTP 32, MITM-ARP 21, DDoS-SYN 5, Mirai 1, Recon 1; 56 uninvolved hosts, 2 attacker host's other traffic, 2 DDoS victim's other traffic.
- Table VII (k-curve) completed with all seven attacker classes (BF 1, DS 6, DH 1, MA 7, Mi 7, Re 1, Web 3 = 26) per k, from blocking_accounting.md (c).
- Tightened "full trade-off" and "late blocks" paragraphs.

### discussion.tex
- Internal threats: CIC labels come from our own rule and are scored against it; IoT-23 supports the cost of file labels but does not validate our CIC labels.
- Conclusion threats: paired bootstrap result replaces "intervals overlap substantially".
- Tightened: checklist intro (script names list cut), construct/external duplicates cut, conclusion, artifact paragraph (duplicate #262/#263 sentence cut; still in intro and live).

### refs.bib (keys unchanged)
- nfstream263: title "Keep {LRU} order on flow update so idle flows expire on time (\#262)", note "Submitted 2 Nov. 2026, open".
- kostas2024iotgem -> @article, Computer Networks 270:111550, 2025, doi 10.1016/j.comnet.2025.111550.
- vitorino2025revisiting -> @inproceedings, FPS 2025, LNCS, Springer, pp. 150--166, 2026, doi 10.1007/978-3-032-20026-6_9.
- ramkumar2024diagnosing -> @article, IEEE TSE 51(11):3117--3137, 2025, doi 10.1109/TSE.2025.3610540.
- pinto2025hera -> @inproceedings, TrustCom 2024, pp. 1850--1856, doi 10.1109/TrustCom63139.2024.00255.
- arXiv ids kept in note (rendered); doi fields kept as in existing entries (IEEEtran does not print them).

### FACTS.md
- 317 -> 211 (with source and reason); "honeypot/benign" -> benign captures of real, uninfected devices; mapping line updated.
- New section "REVISION R5 RESULTS" with all R5 numbers and their source files.

## Numbers removed (present in backup_r4/sections, absent now)
| Number(s) | Where | Reason |
|---|---|---|
| 317 | setup.tex | Spec correction to 211 |
| 141,590, 143,796 | labels.tex | Pooled count replaced by per-capture FPR (spec 2) |
| 0.818, 0.822, 0.696, 0.347, 0.241 (and capture ids 20-1, 21-1, 1-1, 8-1, 34-1 in that list) | labels.tex | Intentional cut for space; range 0.999--0.055 kept |
| 0.945, [0.731, 0.983], [0.941, 0.949] | splits.tex | Intentional cut for space (C&C example); Table IV still contrasts flow and host-pair CIs |
| "6 of 9 at k=10" | response.tex | Intentional cut for space |
| Correct column 19 / 9 | Table VI | Now shown as Attackers 19/26 and 9/26 |
| 2.2 | response.tex | \tabcolsep formatting only |
| "227," | live.tex | Punctuation only; PR #227 still cited |
The token check also flags only these; numbers such as 0.822 coincide with other tokens (0.822 is still a live CI bound), so the list above was completed by hand from the edits.

## Grep check (sections/*.tex, main.tex, refs.bib)
- "honeypot": none. "official": none. "or stable detection": none. "updated and terminated": none. "in deployment": none. "most datasets": none.
- "317": only inside a DOI in refs.bib (10.1109/ACCESS.2026.3673172).
- "merged": only labels.tex, describing the CIC-IoT2023 MERGED_CSV files (correct), and a comment line in refs.bib; never about PR #263.

## Not done / notes
- All spec items done.
- Table VIII (checklist) row "4 Response" hyphenates as "Re-sponse" in the narrow first column; this predates R5 and was left alone.
