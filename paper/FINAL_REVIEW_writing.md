# Final review: writing, structure and presentation

Paper: "What Benchmark Scores Hide: Auditing a Flow-Based IoT Intrusion Detector from Labels to Live Blocking" (main.pdf, 8 pages including references, compiled 2 Nov 2026).

## Overall impression

1. The paper is honest, careful and well supported, and the four-step arc (labels, splits, live, response) is a good spine. But the four-check audit, which is the reusable contribution, is not shown until the last page (Table VIII), and the first page sells a list of findings rather than a method.
2. Sections IV-V and VII are written as walls of numbers: there are paragraphs with 20-30 figures, nested confidence intervals, and caveats on caveats. A reader new to CIC-IoT2023/IoT-23 loses the point of each paragraph before reaching it.
3. The page budget is fully used (the references end at the bottom of p.8), so every fix below is paired with a cut. About 350-450 words can be removed with no loss of substance, mainly from the IoT-23 split paragraph, the "benchmark as distributed" paragraph, the Table V/repeats discussion and the setup details.

---

## Top 10 changes, ranked by impact

### 1. Put the four-check audit on page 1-2 and make the intro sell it (intro.tex, discussion.tex Table VIII)
The audit is the stated reusable result, but in the intro it is the *last* bullet, and the table appears on p.7. Splits, which is one of the four steps, has **no contribution bullet at all** (the bullets cover labels, live, response and the audit).
- Move Table VIII (`tab:checklist`) into the Introduction as "Table I: The four-check audit and what it caught". This costs no space, because it moves rather than grows. Add one column, "Section", and replace "Caught here" with the single headline number per check: 71.8% benign flagged; BruteForce recall 1.00 to 0.05; verdicts delayed up to 82.5 s; 60/1,674 false blocks.
- Rewrite the contribution list as one lead bullet ("A four-check audit, implemented as scripts, run on two datasets (Table I)") followed by one bullet per check with its headline finding. Add the missing splits bullet, for example: *"Split check: a within-capture temporal split exposes a brute-force target change that a random split hides (CIC-IoT2023), and the same check shows that the IoT-23 gap comes from missing classes, not from time."*
- The phrase "At each of four steps ... we ask what the previous step hid" does not hold for Step 1, which has no previous step. Use instead: *"At each step we ask what a standard evaluation would hide, and which check reveals it."*
- Cost: 0 lines if the table moves. The rewritten bullets are about the same length as the current ones.

### 2. Make the abstract readable on first contact (abstract.tex)
The abstract uses undefined terms ("background traffic", "true macro-F1", "evidence-based labels", "host-pair windows", "eligible", "idle flow meters", "verdicts"). It also contains a broken sentence: *"on IoT-23 the temporal--random gap does not replicate; it is explained by missing classes and unstable under clustering."* And it ends on artifacts rather than on a takeaway.
- Define "background" the first time it appears: *"... are background traffic (benign traffic of other devices, not the named attack)"*.
- Replace "true macro-F1 of 0.396" with *"macro-F1 of 0.396 when scored against evidence-based labels"*.
- Fix the IoT-23 clause: *"on IoT-23 the temporal--random gap does not replicate: it comes from classes missing from one half of the split and is not robust to the choice of bootstrap cluster."*
- Response: *"blocking a host pair on its first attack verdict wrongly blocked 3.6% of benign host pairs (60 of 1,674 pair-windows)"*.
- Add a closing claim before the artifact sentence: *"Each check exposed a problem invisible to the previous one; none is visible in a benchmark score."*
- "Code, data and the audit scripts are public" overclaims, because the datasets belong to third parties. Write *"Code, labels, evidence and audit scripts are public."*
- To pay for this, cut "(and our mapping of malware families to classes)" (it is covered in Sec. IV) and "on an emulated Open vSwitch gateway" (shorten to "on an emulated gateway").

### 3. Split and shrink the IoT-23 split paragraph (splits.tex, "IoT-23: the temporal gap does not replicate", p.4 col.2)
This single paragraph runs about 400 words and contains about 30 numbers. It also mixes three messages: missing classes, cluster sensitivity, and spanning flows inflating C&C.
- Restructure it as three short paragraphs, each opening with its message: (a) *Missing classes.* (b) *Cluster sensitivity.* (c) *Spanning flows.*
- Move the alternative-cluster intervals (originating host / capture) into two extra rows of Table IV ("Common-class CI by originating host / by capture"), or into the artifact, and keep only the conclusion: *"Under coarser clusters both intervals include zero."*
- Delete the final "What carries over are three requirements..." sentence. Table VIII already lists these requirements, and with change 1 the reader has seen them on p.1.
- Saves about 150 words (about 12 lines).

### 4. De-nest the CIC-IoT2023 gap paragraph and state the claim once (splits.tex, first paragraph, p.3-4)
This paragraph contains 14 numbers and five interval statements, and ends with *"Its sign is thus likely positive but not established under coarser clustering; its size is uncertain..."*. The hedge is repeated in the BruteForce paragraph ("It is a case study, not a statistically robust effect"), in Threats/Conclusion and in the abstract ("three host pairs"). This is too much hedging in one place and too little guidance on what the reader should conclude.
- Rewrite: *"Macro-F1 is 0.869 under the random split and 0.731 under the temporal split (Table III). A paired host-pair bootstrap puts the difference at +0.137 [0.024, 0.278]. Under coarser clusters (per attacker or per capture) the interval barely excludes zero, and with recurring attacker IPs merged it includes zero. We therefore treat the gap as a likely but unestablished effect, and Section V-A as a case study."*
- Move the seed range (0.8535-0.8726), the 50-flow macro-F1 (0.814) and the "76-97% of resamples omit one" detail to the artifact.
- Say "case study" once, here, and refer back to it later.
- Saves about 70 words.

### 5. Use one tree (or one name per tree) throughout (setup.tex "Detector", splits.tex, Table III)
Two trees with near-identical scores (baseline 0.731/3.9%; deployed 0.725/3.8%) force the reader to track which one every number belongs to. The 0.725 vs 0.731 difference is noise. In addition, Table III and Fig. 1 use the baseline tree while every other table uses the deployed one.
- Best option: report the deployed tree everywhere (Table III, Fig. 1, Sec. V text), since the paired difference for it already exists (+0.142), and delete "Section V reports the baseline tree...".
- If that is not possible, label it explicitly in every caption: "baseline tree (Sec. III)" vs "deployed tree".
- Also cut the NSGA-II sentence. It is not part of the audit story and no result depends on it.
- Saves about 45 words.

### 6. Give Steps 3 and 4 the same opening shape as Steps 1 and 2, and close each step with its check (live.tex, response.tex)
Steps 1 and 2 open with "*What the benchmark hides*" and "*What a random split hides*". Steps 3 and 4 do not, so the arc breaks halfway through.
- Open Sec. VI with *"What an offline score hides. Equal scores do not show that the live gateway classifies the same flows..."*.
- Open Sec. VII with *"What a per-flow FPR hides. ..."*.
- End each step with a one-line, italic "Check N:" sentence naming the measure. This replaces the long derivation at the end of the IoT-23 paragraph and lets Table VIII be read as a summary.
- Cost: about 4 lines in total, paid for by change 3.

### 7. Tighten the "Repeats and CPU budget" paragraph and Table V (live.tex, p.5)
This paragraph has about 300 words. The one-core Mirai explanation ("adding 0.006 to macro-F1 (0.0125 over the four classes of the three half-core windows, which explains its 0.9284 there)") is a footnote-level detail in the main text. Table V's two macro-F1 columns with different precisions (0.804 vs 0.9171) and its caption ("over the run's own windows (half core: three) and over the three half-core windows (offline 0.914)") are hard to decode.
- Drop the "own" column, keep only the macro-F1 on the three common windows (3 decimals), and add a "Flows vs offline" column (+0.02%, +12%, +29%) so that the replay-rate effect can be read directly from the table.
- Reduce the Mirai explanation to: *"The one-core run's higher score comes from one extra, correctly classified Mirai flow at a lower replay rate."*
- Cut "The half-core runs are not more accurate..." once the "own" column is gone.
- Saves about 100 words.

### 8. Shorten "The benchmark as distributed" (labels.tex, p.3 col.2)
About 200 words, half of which is about provenance (Hugging Face mirror, folder name, the UNB registration form).
- Rewrite as: *"The released per-pcap CSVs (39 packet-window features; no address, timestamp or label column; the label is the file name) cannot be relabelled from evidence, and the merged CSVs are shuffled. Even scored against file labels, a decision tree reaches only 0.43 BruteForce and 0.37 Web recall (macro-F1 0.749): the classes that are mostly background are the ones the released format handles worst."*
- Move the mirror name and the byte-comparison caveat to the artifact README, or to one clause in Threats.
- Saves about 110 words.

### 9. Make every table self-contained (Tables I-VII)
- **Table II:** "F1" in the headers means macro-F1, so write "Macro-F1 (apparent/true)". "CIC" is never defined, so use "CIC-IoT2023". "true" in "Trained on" covers two different label sources, so write "evidence/Zeek". Also say in the caption that "apparent" is what a file-label study would report.
- **Table III:** add the random-split support, or state that n is the same order. Caption: *"Per-class F1 of the baseline (or deployed) decision tree on CIC-IoT2023."*
- **Table IV:** "Flow CI" is undefined. Write *"95% CI from a flow-level / host-pair bootstrap."*
- **Table V:** see change 7. Use a consistent 3-decimal precision.
- **Table VI:** the caption runs six lines and buries the definition of "eligible". Move the ICMPv6 denominator note to the text, and define "eligible benign host-pair window" once in Sec. VII text rather than in the caption.
- **Table VII:** "Blk." is **not defined** in the caption. The class abbreviations (BF, DS, DH, MA, Mi, Re) appear nowhere else. Either use the Fig. 1 labels or add a key line. The caption runs seven lines, so shorten it by moving "simulated on the run-1 verdict stream" into the text.
- **Table VIII:** in the p-columns, justified text produces "4 Re-sponse" and wide gaps. See the typography list.
- **Fig. 1 / Fig. 2:** the axis labels "BruteF", "DDoS" and "MITM" differ from the class names used in the tables (BruteForce, DDoS-SYN, MITM-ARP). Fig. 2 mixes capture names (CmdInj, SQLi, XSS) with class names. Use the Table I names. "1/2 core" in Fig. 2 should be "half core", to match Table V.

### 10. Define jargon before use, and remove the double meaning of "background" (related.tex, setup.tex, live.tex)
- "Background" means the benign traffic in attack captures (Sec. IV), but Sec. VI-C also uses a **"background ping"**. Rename the latter "keep-alive ping" (live.tex, "Quiet meters" and "An exporter defect").
- "Boundary-spanning connections" is used in Related Work (p.2) but only defined in Sec. V. Either define it there or replace it with "connections that cross the split point".
- "Meter" (an NFStream concept) appears in the abstract and intro ("idle flow meters") but is only explained in Sec. VI-C. In the abstract use *"flows stuck in idle exporter queues"*, or define it in Setup.
- DVWA, Zeek, OVS and MITM are not expanded at first use. Expand them as "the DVWA (Damn Vulnerable Web Application) test site", "Zeek network monitor", "Open vSwitch (OVS)" and "man-in-the-middle (MITM)".
- "Verdict" (one per exported flow) is never defined. Add a sentence in Sec. III or VI-A: *"Each exported flow receives one verdict (predicted class)."*
- The intro claim *"Live prototypes rarely check that they classify the flows the model was evaluated on"* is uncited. Either cite two or three of the prototypes alluded to in Related Work, or soften it to "we found few prototypes that check...".

### Further cuts to fund the above (if more space is needed)
- Setup "Metrics": cut the union cluster counts "(CIC-IoT2023: 4,641 from 3,465 temporal and 3,858 random; IoT-23: 348,350)". Saves about 20 words.
- Setup "IoT-23": cut "Of the flows, 35.2% overlap more than one Zeek row ... one of which covers 14,159 rows". Replace with *"Labels agree at flow level for all but 270 flows (0.04%)."* Saves about 50 words.
- Related "Splits": cut the Rasheed and Alobaedy quote. It is quoted again in Sec. V. Saves about 25 words.
- "Arpwatch idea" appears verbatim in Related Work and in Sec. VII. Keep it in one place only.
- The defect paragraph says "without changing flow boundaries or features" and later "changes only export timing, not flow boundaries or features". Delete the second.
- Footnote 1: drop "#193", which has no citation, or cite it.
- Merge Threats "Conclusion." into "Construct." The paragraph label "Conclusion" also clashes with the "Conclusion" subsection right below it. Rename it "Statistical conclusion" if kept.

---

## Term inconsistencies

| Concept | Variants found | Suggestion |
|---|---|---|
| Random split | "stratified random" (Setup), "random" (Sec. V text, Table III, Fig. 1, abstract), "Stratified" (Tables II, IV; IoT-23 text), "temporal-random gap" (abstract). "Stratified random" also describes the CSV row split in Sec. IV. | Define "stratified random (hereafter *random*)" once, and use "random" everywhere, including in Tables II and IV. |
| Benign in attack captures | "background", "Background (Benign)", "Backgr.", "background (Zeek label Benign)", "benign flows" (abstract), "Benign test flows". Also "background ping" (live). | Background = Benign flows inside an attack capture. Benign = the class. Rename the ping. |
| Label sources | "file-name labels", "file labels", "file-label model/tree", "per-PCAP / per-pcap", "evidence-based labels", "evidence labels", "true labels", "our labels", "Zeek labels", "the authors' Zeek labels" | Use "file-name labels" and "evidence labels" (CIC) / "Zeek labels" (IoT-23). Use "true" only in the Table II header, with a definition. Write "pcap" in lower case (except inside the quote). |
| The models | "decision tree", "the tree", "baseline tree", "deployed tree", "the detector", "the model", "file-label tree", "evidence-label model" | One tree (see change 5). Use "file-label tree / evidence-label tree" consistently ("evidence-label model" appears in Sec. IV). "Edge tree" is not used, which is good, so keep it that way. |
| Host pair | "host pair", "(capture, host pair)", "(capture, unordered host pair)", "attacker pair", "pair", "host-pair window", "eligible benign host-pair windows", "pairs seen in a window" | Define "host pair" (unordered, per capture) once in Setup, and "host-pair window" once in Sec. VII. |
| Live failure 2 | "idle flow meters" (abstract, intro), "Quiet meters" (Sec. VI-C heading), "idle meters" (Table VIII) | Use "idle meters" everywhere. |
| Live failure 3 | "NFStream ordering defect", "export-ordering defect", "exporter defect" | Use "NFStream export-ordering defect". |
| Response policies | "Block on first verdict", "block-on-first-verdict run", "k = 1", "validation-chosen policy", "the policy", "k = 10, MITM-ARP ign." | Name them P1 (k=1) and P10 (k=10, MITM-ARP ignored) and use the names in Tables VI-VII. |
| Class names | DDoS-SYN / DDoS (figures) / DS; BruteForce / BruteF / BF / brute force / brute-force / DictionaryBruteForce; MITM-ARP / MITM-ArpSpoofing / MITM / MA / ARP spoofing; Web vs SQLi/XSS/CmdInj/SqlInjection/CommandInjection | Use one label per class in all tables and figures. Capture names should appear only in Setup and Table I. |
| IoT-23 units | "scenarios", "captures", "malware captures", "benign-device captures" | Use "captures" after the first "scenarios (captures)". |
| Rate units | "packets/s", "packet/s" (ping), "pps" (Table V) | Use packets/s throughout. |
| FPR format | percentages (71.8%, Table II) vs fractions (0.709, 0.049, mean 0.993 in IoT-23 text; Table I fractions vs 91-98.5% in text) | Use percentages for FPR and for background share, everywhere. |
| Run naming | "run 1", "run-1", "No limit 1", "first no-limit run" | Use "run 1" in text, and the same label in Table V. |
| Gap | "temporal-random gap", "temporal gap", "the CIC-IoT2023 gap", "random minus temporal" vs "stratified minus temporal" | Use "random-temporal gap", always random minus temporal. |
| Spelling | British usage throughout (labelling, generalisation, licence, behaviour) except the file name `conn.log.labeled` | This is consistent; keep it. Check that the venue accepts British spelling. |

---

## Typographic issues (by page)

- **p.1, col.2, contribution 2:** "nf-stream#262" is hyphenated across a line inside an identifier. Use `\mbox{nfstream\#262}` or `\texttt{}`, and add `\hyphenation{NFStream}` in the preamble.
- **p.1, abstract:** the abstract is about 230 words of dense bold-italic IEEE abstract type. The four italic run-in labels (*Labels:*, *Splits:* ...) help, but each block holds 3-6 numbers. Aim for at most 2 numbers per block.
- **p.2, col.1, Related Work:** "NF-Stream" is hyphenated ("combine NF- / Stream"). The same `\hyphenation` fix applies.
- **p.2, col.1, Setup:** "MITM-ArpSpoofing, Dic-tionaryBruteForce" hyphenates CamelCase capture names. Set the capture names in `\texttt{}` or put them in a small list.
- **p.2, col.1, "Flows and features":** underfull line (badness 10000) with visibly stretched inter-word spaces, caused by `\texttt{statistical\_analysis=True}`. Rephrase ("with statistical features enabled") or allow a break.
- **p.2, col.1, line 3 of Setup:** underfull line "(about 5.17 GB). Files over 300 MB are" (badness 2050).
- **p.3, Table I:** the "Attacker evidence" p-column wraps for the MITM-ARP and SQLi rows, giving uneven row heights. Shorten the cells ("MAC …:27:d5 claims .1, .65"; "SLEEP(5), UNION SELECT"). Mixed fonts (`\texttt` evidence next to roman) are fine. "Backgr." is an unneeded abbreviation: write "Backgr. (%)" with percentages.
- **p.3, Table II:** the IoT-23 block is separated by a full `\hline`, which visually reads as a footer row. Use `\midrule`-style spacing or a sub-header row "IoT-23". Consider `booktabs` for all tables (`\toprule`/`\midrule`/`\bottomrule`). The current `\hline` rules sit tight against the text.
- **p.3:** Tables I and II stack on top of col.1, leaving only about 20 lines of text in that column.
- **p.4, col.2:** underfull vbox (log, page 4). Paragraph gaps around "What flow features cannot see" are visibly stretched. Change 3 will reflow this.
- **p.4, Fig. 1:** the legend is larger than the caption font, and the tick labels are rotated and abbreviated (BruteF, DDoS, MITM). "recall" in lower case on the y-axis. Use matching class names and a 7-8 pt font.
- **p.4, Table IV:** with `\tabcolsep` 2.5pt the CI columns nearly touch. Use 3 decimals for CIs, or drop the Flow CI column (it is only needed to make the "too narrow" point, which is already made in Setup).
- **p.5, Table V:** "--" renders as a lone en dash in the One-core row. Mixed precision (0.804 vs 0.9171). Header "3 win." is cryptic. The caption has five lines of parentheticals.
- **p.6, col.1:** underfull vbox (log, page 6). A visible white gap between the Fig. 2 caption and "Quiet meters".
- **p.6, Fig. 2:** the legend says "1/2 core" while the text and Table V say "half core". The x-axis mixes "DDoS", "BruteF" and capture names. The dashed idle-timeout line has no label in the plot (the caption covers it, which is acceptable).
- **p.6, col.2:** Table VI is placed above the "VII. Step 4: Response" heading, so the reader meets the blocking table before the section that defines blocking. Use `[!b]` or move the float definition further down in response.tex.
- **p.6, footnote 1:** "#193" has no citation, and "(2022)" sits after the reference marker. Write "nfstream #120 (2022) [37] and #193".
- **p.7, Table VII:** 13 columns at `\tabcolsep` 2.4pt. The 3-row header with counts in parentheses is hard to parse. "Blk." is undefined. The caption runs seven lines in small caps, which is hard to read.
- **p.7, Table VIII:** justified p-columns cause "4 Re-sponse", "Benign host-pair win-dows" and loose lines (underfull badness 10000 in the log). Use `>{\raggedright\arraybackslash}p{..}` and widen the first column so that "4 Response" fits.
- **p.7, Artifact Availability:** the URL breaks after "https:" ("https: //github.com/..."). Use `\url` with the `xurl` package, or let it start on its own line.
- **p.7:** "Conclusion" is used both as a run-in Threats label and as a subsection title, a few lines apart.
- **p.8, references:** [4] "accepted at VNICT 2026 (per arXiv comment)" is informal, so write "to appear, VNICT 2026". [37] gives an underfull reference line with a broken URL. [14] and [15] are self-authored GitHub items, which is fine, but check that the venue allows them in the references (they could go in footnotes). Several 2026 arXiv entries say "preprint" in some cases and not in others ([21], [20] vs [39], [16]). Make them uniform.
- **Global:** there is no `\usepackage{booktabs}`, `\usepackage{siunitx}` or `xurl`. Adding booktabs plus raggedright p-columns fixes most of the table complaints above at no cost in length.

---

## Page-budget ledger (approximate)

| Change | Words | Lines |
|---|---|---|
| Cut IoT-23 split paragraph (3) | -150 | -12 |
| Shorten "benchmark as distributed" (8) | -110 | -9 |
| Repeats/Table V (7) | -100 | -8 |
| De-nest CIC gap paragraph (4) | -70 | -6 |
| One tree + drop NSGA-II (5) | -45 | -4 |
| Setup details (Metrics counts, Zeek overlap) | -70 | -6 |
| Duplicates (arpwatch, defect sentence, Rasheed quote) | -45 | -4 |
| **Total freed** | **about -590** | **about -49** |
| Abstract and intro rewrites (1, 2) | +40 | +3 |
| Step openers and "Check N" closers (6) | +60 | +5 |
| Jargon definitions (10) | +50 | +4 |
| **Net** | **about -440** | **about -37 (about 0.6 column)** |

Moving Table VIII to the intro costs nothing. The freed space is enough to un-cram Tables V and VII, or to give Table VII a readable header.
