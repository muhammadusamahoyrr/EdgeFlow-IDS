# Revision R7 log (2 Nov 2026)

Spec: external reviewer points 1-5 (cluster sensitivity, same-window live baseline, "host-pair windows" terminology, artifact seeds/patch, final checks).
Backup of the R6 state: paper/backup_r6/ (sections/*.tex, main.tex, refs.bib).
Runner: src/run_review_r7.sh (`wsl -d Ubuntu-24.04 -u root bash /mnt/d/EdgeFlow-IDS/src/run_review_r7.sh`), log results/review_r7.log (all runs exit 0).

**Final PDF: 8 pages including references** (no font/margin/\vspace changes). No undefined references or citations, no overfull boxes, no bare `%` (only the three new comment lines and main.tex's existing comment).
check_refs.py: 39 cited, 39 in bib, none missing, none unused, no TODO. Abstract 221 words.

## Analyses (new scripts, new result files; no existing result file modified)

1. **src/iot23/cluster_sensitivity.py -> results/iot23/cluster_sensitivity.md**
   - Clusterings: host pair (paper), capture (10), originator = (capture, NFStream src_ip = sender of the first packet), local host = (capture, private endpoint) [supplementary]. Host-pair rows reproduce common_class_ci.md / splits.md exactly.
   - 91.5% of temporal IoT-23 test flows are single-flow host-pair clusters (stratified 88.8%; CIC-IoT2023 0.4% / 0.6%).
   - Temporal common-class CI: host pair [0.919, 0.983], originator [0.576, 0.983], capture [0.469, 0.984]. Paired common-class difference (-0.017): host pair [-0.039, -0.009], originator [-0.130, 0.114], capture [-0.078, 0.005] -> sign not robust. All-class difference (+0.214) includes 0 under every clustering. C&C F1 and all-class CIs per scheme in the file and FACTS.md.
   - Capture bootstrap is coarse: 35% of resamples miss a common class (0.9^10).
   - Note: a first run wrote the per-class size table with the scheme label overwritten by a column of the same name (dict key collision). That file was renamed (not deleted) to results/iot23/cluster_sensitivity_run1_mislabelled.md, the key fixed, and the script rerun; all CI sections are byte-identical between the two runs.
2. **src/analysis/same_window.py -> results/live/same_window.md**: live macro-F1 on the three half-core windows: no limit 0.9171 / 0.9155 / 0.9175, one core 0.9284, half core 0.9175 / 0.9172 / 0.9173, offline 0.9145 (0.914). Recomputation over each run's own windows reproduces every live_vs_offline.json.
3. **src/make_nfstream_diff.sh -> patches/nfstream-6.6.0-lru.diff**: installed nfstream copied to a temp dir, `patch_nfstream.py --revert` run against the copy, original vs patched meter.py diffed (one added line). Reverted copy is byte-identical to meter.py in the PyPI 6.6.0 wheel. Live install never touched: `grep -c "EdgeFlow-IDS patch"` = 1 before and after.

## Changes per section
- **abstract.tex**: "blocked 60 benign host pairs (3.6% of those eligible)" -> "blocked 60 of 1,674 eligible benign host-pair windows (3.6%)".
- **setup.tex**: Metrics: "All reported intervals use host-pair clusters." Cut "The exporter thus changes what the benchmark contains." (space).
- **splits.tex**: IoT-23 paragraph: "slightly but consistently higher" -> "slightly higher"; new 2-sentence sensitivity summary (91.5% singletons vs 0.4% on CIC; originator 350 clusters / capture 10, coarse; temporal common-class CI [0.576, 0.983] / [0.469, 0.984]; paired difference [-0.130, 0.114] / [-0.078, 0.005]; sign not robust). Removed the speculative test-set-composition sentence (see below).
- **live.tex**: Table V gains a "3 win." macro-F1 column for every run (0.9171, 0.9155, 0.9175, 0.9284, 0.9175, 0.9172, 0.9173) and the caption explains both columns (offline 0.914); text: half core is not more accurate, it averages four classes instead of eight, and no-limit runs score 0.9155-0.9175 on the same windows. "(offline 0.914 on the half-core windows)" moved into the caption. Space: intro sentence tightened, "Equal macro-F1 despite ... 29%" sentence cut (29% still stated), Pekar follow-up sentence tightened.
- **response.tex**: false blocks "counted per host-pair window" in the definition; Table VII caption "False: false blocks (host-pair windows)".
- **discussion.tex**: checklist row 4 "False blocks per host-pair window" / "Benign host-pair windows blocked at k=1"; conclusion "wrongly blocked host-pair windows"; Threats/Conclusion: repeat of run counts cut (in live.tex). Artifact: seeds (all 0; live runs timing-dependent), NFStream fix included as src/patch_nfstream.py and diff in patches/; LaTeX-comment placeholder for tagged release + Zenodo DOI (no DOI invented).
- **labels.tex**, **related.tex**: wording tightened for space ("Our gateway is not new in its parts..." cut; MERGED_CSV and opening sentences merged). No numbers changed.
- **FACTS.md**: new section "REVISION R7 RESULTS".

## Numbers removed (present in backup_r6/sections, absent now)
| Number(s) | Where | Reason |
|---|---|---|
| 4,600, 5,152, 5,714, 5,683, 0.799, 0.901 | splits.tex | Sentence speculating why the temporal common-class score is higher (test-set composition). The cluster sensitivity shows the difference's sign is not robust, so explaining it is moot; also needed for space. Numbers remain in results/iot23/spanning_common.md / splits.md and FACTS.md. |
Count decreases only: "29" (2 -> 1, the cut repeat sentence) and "1". Checked by token diff of sections/*.tex against backup_r6/sections.

## Not done / deviations
- Tagged release / Zenodo DOI: placeholder comment only, to be minted by the author.
- The "3 win." column uses 4 decimals (results are stored at 4 decimals; 0.9155 cannot be rounded safely to 3).
- Artifact text says "diff in patches/" rather than the full file name (space; the page is exactly full).
- C&C paired difference ([-0.150, -0.028] host pair, includes 0 otherwise) and the local-host scheme are reported in the result file only, not in the paper (space).
