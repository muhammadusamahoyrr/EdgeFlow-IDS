# Round-6 revision: response to external review 3

Use numbers only from the result files; new analyses go in NEW result files.

**Constraints**
- Back up the sections, main.tex and refs.bib to paper\backup_r5\ first.
- ≤ 8 pages.
- No git. No deletions.
- Every `%` in .tex must be written `\%`. Grep for bare `[0-9]%` before compiling.

**How to run Python:** `wsl -d Ubuntu-24.04 -u root bash /mnt/d/EdgeFlow-IDS/src/run_review_r5.sh` is the pattern; the default WSL distro has no bash. Write a similar runner, src/run_review_r6.sh.

## Analyses (scripts in src/, outputs in results/)
1. **IoT-23 spanning flows, common classes** → results/iot23/spanning_common.md
   - Report common-class (Attack, Benign, C&C, PortScan) macro-F1, with and without boundary-spanning test flows, for both splits.
   - Report the per-class test support left after removal, and flag any class that loses all its test flows.
   - Reuse src/iot23/splits.py and common_class_ci.py.
2. **Per-class live flow counts** → results/live/perclass_counts.md
   - For each live run (run1 = no limit, the half-core runs, edge100 = one core) and offline, give the per-class test-flow counts and per-class F1.
   - Sources: results/live/*/live_vs_offline.json and flow_match.md.
3. **Blocking details** (extend into results/blocking_accounting_r6.md; read src/analysis/blocking_accounting.py)
   - (a) The exact definition of an "eligible" benign host-pair window.
   - (b) Why the counts are 1,674 (k=1 run) and 1,675 (policy run).
   - (c) The window each of the 21 MITM-ARP-triggered false blocks fell in.
   - (d) Per-class attack-flow shares behind the constant 11.1% at every k. Find 11.1% in sections/response.tex and its source in results/live/run1/block_curve.md. Confirm it is six DDoS pairs blocked at every k, dominating the attack flows.

## Paper edits
1. **Spanning-flow claim (splits.tex and checklist).**
   - Report common-class F1 with and without spanning flows.
   - If the common-class effect is small or absent, soften the claim that spanning flows inflate stratified scores on IoT-23. The 0.863→0.809 drop is driven by DDoS (63 flows) and FileDownload (2 flows).
   - Keep the spanning-share check as a reporting requirement.
   - Add one short, hedged guess for why temporal beats stratified on the common classes, e.g. test-set composition. Use only facts from the result files.
2. **Live macro-F1 fragility.** Add per-class live counts to Table V, or state compactly next to 0.804/0.918 that the Mirai class has 4–5 live flows and one flow moves macro-F1 by about 0.006.
3. **Paired bootstrap method.** Add one sentence:
   - Clusters are keyed by (capture, unordered host pair) over the union of both test sets.
   - Each resample draws union clusters with replacement and applies the same draw to both splits.
   - A cluster absent from one test set contributes nothing to that split.
   - F1 is recomputed from summed confusion matrices.
   - Union sizes: CIC 4,641 (temporal 3,465, random 3,858); IoT-23 348,350. See results/paired_diff.md and results/iot23/common_class_ci.md.
4. **Table VI.** Define "eligible" and explain 1,674 vs 1,675 (in a footnote or caption).
5. **Threats section.** Replay is open-loop, so "packets dropped" is a counterfactual. Dropped packets cause no retransmissions, and attackers do not adapt.
6. **Response.** Restore the explanation of the constant 11.1% at every k, with the per-class basis from analysis 3d. Say which window the MITM-ARP false blocks fell in.
7. **Future work.** Add a per-class or macro-over-attack-class criterion for choosing k.
8. **Provenance.**
   - Garcia & Valeros [16]: add section pointers. The "files or directory names" quote is from the abstract; the false-positive/blocking passage is Sec. 6.3.
   - Hugging Face mirror: state that the layout, the 39 columns and the per-pcap file names match the dataset's own README. Say we could not compare bytes against the UNB download, which requires a registration form. Put this in setup or labels, briefly.
9. **Abstract.** Trim to ≤ 250 words.

## Finally
- Compile with MiKTeX: pdflatex, bibtex, pdflatex, pdflatex.
- Run check_refs.py.
- Do the number-preservation check against backup_r5.
- Update FACTS.md.
- Write REVISION_R6_LOG.md.
