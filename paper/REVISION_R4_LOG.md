# Revision R4 log (2 Nov 2026)

Spec: `REVISION_R4.md` (sections A-E). Backup of the R3 sources: `backup_r3/` (main.tex, refs.bib,
sections/*.tex). main.tex was not changed.

## Final build
- pdflatex -> bibtex -> pdflatex x2 (MiKTeX). **8 pages** including references (about a quarter
  of the last right-hand column free). No undefined references or citations, no overfull boxes,
  no LaTeX errors; only minor underfull-box warnings.
- `check_refs.py`: 39 keys cited, 39 in refs.bib, none missing, none unused, no TODO entries.

## Changes per section
- **Abstract.** Reframed as an audit condensed into four checks. Added the IoT-23 label result
  (0.169, 98.5%, authors' Zeek labels) and the honest split nuance (IoT-23 gap comes from classes
  missing from one half). Dropped "previously undiagnosed ... offline evaluation cannot show these".
- **Introduction.** Contributions rewritten: labels result holds on two datasets; released CSVs
  allow only file labels; NFStream issue #262 with fix submitted as PR #263; the four-check audit
  as the reusable artifact. Exporter citation now `pinto2025flowexporter`. Removed the repeated
  label numbers from the bullet list (they stay in the abstract).
- **Related Work.** Added garcia2023labeling (file/directory labels, errors), schraven2026mawiflow,
  rasheed2026drift, ali2026siamxbert (Splits), pinto2025flowexporter (exporters),
  orsdemir2026sok (Response). Shortened the Traffic-MoE/BRIDGE and Ramkumar sentences.
- **Setup.** New "IoT-23" paragraph (10 scenarios, Okiru excluded, Zeek join, 756,306 flows,
  99.99% match, 38 dropped, six classes, DDoS 14,394 Zeek rows -> 211 flows). Merged "Detector"
  and "Model and size choices" into one shorter paragraph (absolute RF size/latency and NSGA node
  count cut; ratios kept).
- **Step 1: Labels.** Table II extended with four IoT-23 rows. New paragraphs "Replication on
  IoT-23" (background shares per malware capture, family-to-behaviour mapping stated as our
  choice, 63.1% differing labels, 141,590/143,796, emphasis that labels are the authors' own) and
  "The benchmark as distributed" (official CSVs: 39 features, no IPs/timestamps/label column;
  0.749/0.803, accuracy 0.82/0.87, row-order 0.727/0.778, BruteForce 0.43/0.41, Web 0.37/0.35).
- **Step 2: Splits.** New Table IV and paragraph "IoT-23: the temporal gap does not replicate"
  (missing DDoS/FileDownload classes, 4-class 0.973 vs 0.956, 63 DDoS / 2 FileDownload test flows,
  host-pair vs flow CIs incl. C&C, spanning 4.1%/5.8% and C&C 36.5%/68%, 0.863 -> 0.809), ending
  with the three check requirements. Added the rasheed2026drift "blindness" clause. Cut the Benign
  host-pair CI and a few duplicate words.
- **Step 3: Live.** CPU table (old Table V) folded into the repeats table (one-core row added);
  harness and replay-rate text shortened; repeats and CPU-budget paragraphs merged. Added the
  pekar2024integrity sentence (defect = one mechanism behind NFStream/CICFlowMeter value
  differences) and "fix submitted with a regression test as PR #263".
- **Step 4: Response.** Added garcia2023labeling and akbari2020atmos on the cost of false
  positives when detections drive blocking. Trade-off and late-block paragraphs shortened
  (numbers already in Table VII removed from the text).
- **Discussion.** "Lessons: Five Cheap Checks" replaced by "An Audit Checklist" (Table VIII, four
  checks, scripts in src/analysis and src/iot23, run on two datasets). Threats updated for IoT-23
  (our family mapping; missing classes; live/response only on CIC-IoT2023; cross-dataset
  asymmetry, ali2026siamxbert) and stripped of numbers repeated from earlier sections.
  Conclusion and Artifact Availability updated (IoT-23 data source, PR #263 "submitted").
- **refs.bib.** Appended verbatim from refs_candidates.bib: garcia2023labeling,
  pekar2024integrity, pinto2025flowexporter, schraven2026mawiflow, rasheed2026drift,
  ali2026siamxbert (the spec calls it `ali2026unknown`; the verified key in refs_candidates.bib is
  `ali2026siamxbert`, kept unchanged), orsdemir2026sok, akbari2020atmos. New `nfstream263` misc
  entry (author Muhammad Usama, 2026, url .../pull/263, note "Submitted, under review").
- **FACTS.md.** New section "REVISION R4 RESULTS" with all IoT-23, official-CSV, PR and citation
  facts and their source files.

## Number-preservation check
Method: every numeric token in `backup_r3/sections/*.tex` was counted and compared with the
counts in the new `sections/*.tex`; each token whose count dropped was traced to its old context.
No value was changed: every removal below is an intentional cut. Values that still appear
elsewhere in the paper are marked "kept in ...".

### Tokens that no longer appear at all
| Token | Old context | Reason |
|---|---|---|
| 20,849 / 7.826 / 0.136 | RF vs tree size (KiB) and per-call latency (ms), Setup | Cut for space; the ratios 94x and 58x are kept |
| 1,681 | NSGA-II tree node count, Setup | Cut; 211 KiB and 14 of 54 features kept |
| 0.901 / 0.962 / 0.990 | Temporal Benign recall 0.962 [0.901, 0.990], Splits | Cut (large class, not at issue) |
| 120 / 196, 69 / 104, 50 / 55 | CPU mean/max per budget, old CPU table | CPU table folded into repeats table; CPU columns dropped |
| 990 / 981 | Max RSS per budget, old CPU table | Covered by the kept range 980-1,025 MB |
| 138, 137.9, 162.7, 109.6 | Half-core catch-up time, CPU table and text | Covered by the kept range 110-163 s |
| 2023 (in "CIC-IoT-2023") | BRIDGE sentence, Related Work | Sentence rephrased; not a result |

### Tokens whose count dropped (duplicates or text that repeated a table)
| Token(s) | Removed occurrence | Still in paper |
|---|---|---|
| 0.396, 0.725, 3.8, 71.8, 91 | Intro bullet; Lessons item 1; Live ("test-set 0.725") | Abstract, Setup, Labels, Table II, Response |
| 0.05 | Lessons item 2 | Abstract, Splits text, Fig. 1 caption |
| 36.1 | Lessons item 3 | Splits |
| 60, 79 | Lessons item 5; Threats ("60 of 79"); Conclusion | Abstract, Response, Table VI |
| 0.814, 25 | Threats (construct) | Splits |
| 52, 77 | Threats ("52-77%") | Live, Response ("52%") |
| 0.804, 0.917, 0.918, 0.914 | Live text ("0.804 here; 0.914-0.918", "0.917-0.918 at half a core") | Fidelity text, Table (repeats), "offline 0.914" |
| 17.8, 21.5, 75.9 | Delay text ("17.8 s in the DDoS window"), CPU table/text | Repeats table |
| 34.0, 60.3, 97.0 | Range "17.8-34.0 s ... 60.3-97.0 s" | Repeats table |
| 10,936, 12,088, 12,271, 13,434 | "10,936-13,434 in the detection runs"; CPU table replay row | Live text and repeats table |
| 1,025 | CPU table RSS | Live ("980-1,025 MB") |
| 1.00 | CPU table packet-ratio and attack-recall rows; Lessons | Live text, Splits, Table III |
| 222 | Setup ("vs 222 KiB") | Setup, Live |
| 30 | Harness text (second "30 s" mention) | Live harness text |
| 15.3, 33.8 | Response "median time to block (15.3-33.8 s)" | Table VII |
| 15 | "(idle timeout 15 s)" in Late blocks; Lessons | Setup, Live |
| 0, 6, 7, 9, 10, 100 | k-curve text ("1/7, then 0/7", "0/3 at k>=10"), CPU table drops row, "6 DDoS"/"7 Mirai" duplicates, "(100% = one core)" note | Table VII, Response, Live |
| 0.347 (masked by a new IoT-23 value) | Mirai window packet share dropped at k=1, Response "Late blocks" | Cut for space (token now appears only as the Hakai 8-1 background share) |

## Spec items not done or done differently
- Bib key for the Ali et al. preprint is `ali2026siamxbert` (as in refs_candidates.bib), not
  `ali2026unknown`; metadata copied verbatim.
- IEEEtran.bst does not print `eprint`/`doi`, so the verbatim-copied arXiv entries
  (garcia2023labeling, ali2026siamxbert) and the existing garcia2020iot23 render without an
  arXiv id/DOI. Fixing this would require adding a `howpublished` field, i.e. altering the copied
  entries, so it was left for the author to decide.
- The PR #263 title in the bib entry is descriptive (no official PR title was available locally).
- The live and response steps were not run on IoT-23, as the spec requires.
