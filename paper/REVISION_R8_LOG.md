# Revision R8 log (2 Nov 2026)

Spec: CIC-IoT2023 cluster-unit sensitivity of the random-temporal difference (A), random-split seed spread (B), edits 1-8 (carry-over requirement, softened CIC gap claim, IoT-23 common-class wording, one-core 0.9284, abstract IoT-23 wording, seed spread clause, proofreading, final checks).
Backup of the R7 state: paper/backup_r7/ (sections/*.tex, main.tex, refs.bib).
Runner: src/run_review_r8.sh (`wsl -d Ubuntu-24.04 -u root bash /mnt/d/EdgeFlow-IDS/src/run_review_r8.sh [scripts]`), log results/review_r8.log (all three runs exit 0).

**Final PDF: 8 pages including references** (no font/margin/\vspace changes). No undefined references/citations, no overfull boxes (underfull warnings only, in narrow table cells/URLs). check_refs.py: 39 cited, 39 in bib, none missing/unused, no TODO. Bare `%`: only the three existing placeholder comment lines in discussion.tex. Abstract 223 words (wc).

## Analyses (new scripts, new result files; no existing result file modified)
1. **src/analysis/cluster_sensitivity_cic.py -> results/cluster_sensitivity_cic.md.** Units: host pair (reproduces paired_diff.md and cluster_ci.md: checked "yes"), attacker host (capture, attacker IP; any flow involving a confirmed attacker of its capture, IP rule or ARP-spoofing MAC rule; other flows keep host-pair clusters; label not used for the key), attacker device (attacker IP across captures; supplementary), capture (10). Paired random-temporal CI, decision tree / deployed: host pair [0.024, 0.278] / [0.025, 0.287]; attacker host [0.002, 0.165] / [0.004, 0.179]; attacker device [-0.004, 0.164] / [-0.002, 0.176]; capture [0.001, 0.151] / [0.004, 0.153]. Resamples missing a class 0.76-0.97 for coarse units (host pair already 0.40 temporal). Marginal CIs in the file and FACTS.md.
2. **src/analysis/cluster_sensitivity_cic_present.py -> results/cluster_sensitivity_cic_present.md** (added because coarse units mostly drop whole classes, which score F1 0): same draws, macro-F1 over classes present. Same conclusion (attacker device [-0.007, 0.216] includes 0; others lower bound 0.002-0.026).
3. **src/analysis/random_seed_spread.py -> results/random_seed_spread.md.** Decision tree joint seeds 0-4: 0.8535-0.8726 (SD 0.0074); split seed only SD 0.008; model seed only SD 0.001. Deployed tree joint 0.8526-0.8728. Seed 0 reproduces metrics.json.
- Note: the first background launch from Git Bash failed before running anything (path rewritten to C:/Program Files/Git/mnt/...); relaunched from PowerShell. No output was produced by the failed launch.

## Changes per section
- **abstract.tex**: IoT-23: "does not replicate and comes from classes missing from one half" -> "does not replicate; it is explained by missing classes and unstable under clustering".
- **intro.tex**: cut "The CSVs released with CIC-IoT2023 allow only file-name labels." (space; stated in Labels and Table VIII).
- **setup.tex**: "All reported intervals use host-pair clusters." -> "Intervals use host-pair clusters unless stated otherwise."; cut "and F1 is recomputed from the summed confusion matrices" (space).
- **splits.tex**: seed spread clause next to 0.869; CIC cluster-unit sensitivity (attacker host / capture barely exclude 0, attacker device includes 0; 76-97% of coarse resamples omit a class; present-class averaging same) and softened conclusion "probably positive but not robust to the cluster unit"; removed "(Mirai 10 and MITM-ARP 25 flows)" (in Table III); IoT-23 common classes first mention "slightly higher in the point estimates, but the sign is not robust to the cluster unit" (host-pair CI labelled as such), later "its sign is not robust" -> "both including zero"; all-class "+0.214 ... includes zero"; dropped "(scans, one-off Benign connections;" and "DDoS has no spanning flows, and no class loses all its test flows" (space); second carry-over requirement rewritten (choose the cluster unit deliberately: host pair, attacker host, capture; report sensitivity; host pairs near-singletons, IoT-23 91.5%).
- **live.tex**: one-core clause: the extra correct Mirai flow adds 0.0125 over the four classes of the three half-core windows, "which explains its 0.9284 there"; merged with the 4-5 Mirai flows sentence. Space: "None of them changed an offline score..." and Pekar follow-up shortened; "Flow construction varied with the replay rate:".
- **discussion.tex**: Table VIII Check 2 "per-class F1 with cluster CIs, sensitivity to the cluster unit"; Threats/Conclusion: "gap is above zero with host-pair clusters but not robustly so under coarser cluster units, and of uncertain size"; cut "and two live runs used an earlier harness" (stated in live.tex) and "The testbed is an emulated network on a laptop, not an edge device;" (laptop/emulation stated in Internal and live.tex); Future work shortened.
- **FACTS.md**: new section "REVISION R8 RESULTS".

## Proofreading
- grep of sections/*.tex for macros followed by glued letters, `\cite{}`/`\emph{}` followed by letters, `~` between letters, doubled words, double spaces: nothing found.
- pdftotext of main.pdf, tokens checked against the source vocabulary for word concatenations: only hyphen-at-line-break joins (e.g. host-pair, half-core) from the checker itself; no real glued words. pypdf shows "inNOMS", "Tibshirani,An" etc. at italic boundaries; pdftotext of the same PDF has the spaces, so these are extraction artifacts. "tree classifiers" / "Traffic-MoE uses" are correct in source and PDF.

## Numbers removed (token diff of sections/*.tex vs backup_r7/sections)
No number removed entirely. Count decreases: "10" and "25" (the "(Mirai 10 and MITM-ARP 25 flows)" parenthetical; both remain in Table III), "1" and "2023" (word-level: "F1", "CIC-IoT2023" in cut sentences).
New numbers: 0.002, 0.004 (as -0.004), 0.151, 0.164, 0.165, 0.8535, 0.8726, 76(--97%).

## Not done / deviations
- Marginal macro-F1 CIs under the coarse units are in the result files and FACTS.md only, not in the paper (space); likewise the deployed-tree coarse-unit intervals and the present-class variant numbers.
- The paper quotes the attacker-device interval (supplementary unit) as the one that includes zero; the primary attacker-host unit and capture barely exclude it.
- Tagged release / Zenodo DOI still a placeholder (unchanged from R7).
