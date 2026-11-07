# Round-5 revision: response to external review 2

Every fact comes from these files. Do not invent numbers.

**Inputs**
- Citations: paper\CITATION_CHECK_R5.md
- IoT-23 results: results\iot23\{fpr_per_capture, zeek_agreement, common_class_ci}.md
- CIC-IoT2023 results: results\paired_diff.md, results\blocking_accounting.md

**Constraints**
- ≤ 8 pages including references.
- Back up the current sections, main.tex and refs.bib into paper\backup_r4\ first.
- No git. No deletions.

## 1. Citation fixes (CITATION_CHECK_R5.md)
- **Rasheed [22]: exact quote.** Use "specific behaviour changes, such as total blindness, sensitivity inflation and relatively stable detection", or paraphrase.
  - In splits.tex, "a case of the blindness" becomes "analogous to the blindness…". The BruteForce change is a change of target, not drift.
- **Pekar & Jozsa [38]:** quote "the specific mechanisms employed for updating and terminating flows".
  - Fix the logic: our defect changes only export timing, not flow boundaries or features. So it is NOT an explanation of the feature-value differences they report.
  - Say instead that it shows how the update/termination mechanism of an exporter can change export *timing* without changing any offline feature or score. This is a timing difference that offline comparisons such as theirs cannot see.
- **Garcia & Valeros [16]:**
  - "most of the datasets they analysed" instead of "most datasets".
  - In Response, use the suggested sentence: Garcia and Valeros note that a few false positives can have *strong* consequences once detections drive IP blocking [16], and Akbari et al. that, because detectors are prone to false positives, simply dropping suspected traffic can have severe consequences [39].
- **Tang et al. [4]:** for recall 0.0095, write "in operational validation on a labelled laboratory capture", not "in deployment".
- **IoT-23 benign captures:** "three benign captures of real, uninfected IoT devices (Philips Hue bridge, Amazon Echo, Somfy smart door lock)". Never call them honeypot traffic. Fix this in every section, tables included; the table row labels may keep the IDs 4-1/5-1/7-1.
- **CIC-IoT2023 CSVs:**
  - We used the per-pcap files (`CSV/CSV`, one file per pcap). They have 39 features and no label, IP or timestamp column; their label is the file name.
  - The `MERGED_CSV` release adds a Label column, but its rows are merged and shuffled, and the label still equals the capture's attack name.
  - The files came from the Hugging Face mirror `bencorn/CIC-IoT-2023`. Its layout matches the official README.
  - Replace "official" with "released" or "as distributed", and qualify it.
- **Bib updates (refs.bib):**
  - nfstream263 title: "Keep LRU order on flow update so idle flows expire on time (\#262)". It is open and unreviewed, so write "submitted".
  - IoTGeM: now Computer Networks 270:111550, 2025, doi 10.1016/j.comnet.2025.111550.
  - Vitorino: now FPS 2025, LNCS, pp. 150–166, 2026, doi 10.1007/978-3-032-20026-6_9.
  - Ramkumar: now IEEE TSE 51(11):3117–3137, 2025, doi 10.1109/TSE.2025.3610540.
  - HERA: now IEEE TrustCom 2024, pp. 1850–1856, doi 10.1109/TrustCom63139.2024.00255.
  - Change entry types as needed, and keep the keys.

## 2. IoT-23 reframing (fpr_per_capture.md, zeek_agreement.md, common_class_ci.md)
- **What the experiment is.** IoT-23 ships per-connection labels, so nobody labels it by file name. Present the experiment as a *robustness test* of the file-label claim, using labels that are not ours. It is not evidence of current practice on IoT-23.
  - The family→behaviour mapping is our choice. Say so in the text and in the abstract (a few words).
- **Lead with the robust number.** In the abstract and intro, lead with FPR, not macro-F1.
  - Capture 1-1 supplies 95% of Benign test flows, so the pooled 98.5% is dominated by it. Report per capture.
  - The file-label model flags 97–100% of background flows in **every** malware capture (mean 0.993). In the three benign-device captures it flags 4.6%. Against Zeek labels, its macro-averaged FPR over captures is 0.709, and the Zeek-label model's is 0.049.
  - Use "in every malware capture, 97–100% of background flows are flagged" as the headline. Mention the pooled 98.5% only with its 1-1 dominance.
  - The macro-F1 0.169 can stay in the body, and drop it from the abstract if space is tight.
- **Zeek label agreement.**
  - 35.2% of flows match more than one Zeek row, but only 270 flows (0.04%) match rows of more than one class.
  - So the labels are consistent at flow level. The class *supports* differ, though, because flows and connections are different units: 14,394 DDoS rows → 211 flows, one flow covering 14,159 rows.
  - The exporter changes what the benchmark contains, which supports the thesis.
  - **Correct "317 tuples" to 211** (under the unordered-key join the count is 211; 317 was a different tuple definition). Check FACTS.md and the .tex.
- **Common-class comparison.**
  - Temporal 0.973 [0.919, 0.983] and stratified 0.956 [0.904, 0.969] (host-pair CIs).
  - Paired difference, stratified − temporal: −0.017, 95% CI [−0.039, −0.009]. The text may now say temporal is slightly but consistently higher, citing the paired CI.
  - All-class difference: +0.214, CI [−0.014, 0.293]. It is not reliably above zero once host pairs are resampled.

## 3. CIC-IoT2023 additions
- **Paired bootstrap of random − temporal** (paired_diff.md). Edge tree: +0.142, paired 95% CI [0.025, 0.287]; 0.1% of resamples ≤ 0. Put it in Splits; it replaces "the intervals overlap" reasoning.
- **Limitation (threats):** our CIC evidence labels use a rule written by the authors and are scored against it. IoT-23 supports the cost of file labels but does not validate our CIC labels.
- **Blocking** (blocking_accounting.md):
  - The 60 false blocks at k=1 break down as DoS-HTTP 32, MITM-ARP 21, DDoS-SYN 5, Mirai 1, Recon 1.
    - 56 involve uninvolved benign hosts.
    - 2 involve the attacker host's other traffic.
    - 2 involve the DDoS victim's other traffic.
  - Denominator: 1,674 eligible benign host-pair windows, so 60/1,674 = 3.6%. The highest rates are in the DDoS-SYN window (12.5%) and the DoS-HTTP window (6.8%).
  - The enforced policy (k=10, MITM ignored) blocks 0 of 1,675.
  - Make the blocking table complete with all attacker classes summing to 26: BruteForce 1, DDoS-SYN 6, DoS-HTTP 1, MITM-ARP 7, Mirai 7, Recon 1, Web 3. Give blocked counts per k from the file. k=1: 19/26. Policy: 9/26.
  - The reviewer says the selection criterion is dominated by DDoS-SYN. Address this in one sentence, e.g. that DDoS-SYN, DoS-HTTP and Recon are blocked at every k, so the k choice trades Mirai/Web/BruteForce coverage against false blocks. Use only numbers from the file.
- **One-core 0.810 vs 0.804, explained:**
  - The one-core run exported 5 Mirai flows instead of 4, because the Mirai window was replayed at 2,664 pps vs 3,685. The extra flow was classified correctly.
  - Mirai F1 went from 0.75 to 0.80, which adds +0.006 to macro-F1. This is the flow-splitting mechanism already described, not a CPU effect.
  - Run-to-run spread elsewhere: 0.8038–0.8043.

## 4. Keep
Live and Response steps remain CIC-IoT2023 only. State this once in the threats section.
