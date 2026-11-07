# Revision R17 log: reviewer round after R16 (backup paper\backup_r17\)

Result: NOMS format kept (main text ends on page 8, references to page 9); abstract 250 words; no undefined refs, no overfull boxes, no BibTeX warnings; check_refs clean.

## New analyses (offline, existing data, run one at a time in WSL)
- `src/analysis/block_timing.py` -> `results/final/block_timing.md`: same run-1 ten 60 s windows, same live flows, blocking rule replayed with three verdict times. Attack flows starting after their block (pooled; k in {1,3,10}; MITM-ARP counted or ignored): (a) flow end 0.9706-0.9719; (b) flow end + 15 s 0.1127-0.1128; (c) logged live verdict time 0.1110-0.1111 (reproduces block_curve.py). Validation (whole periods, flow-end stamps) 0.995.
- `src/diag/ddos_window_starts.py` (sanity check, printed only): DDoS-SYN window attack flows start within 0-31.5 s; 81.7% within the first 15 s; first flow ends at 0.00 s; first live verdict at 15.16 s.
- `src/analysis/gap_nobf_units.py` -> `results/final/gap_nobf_units.md`: paired bootstrap, deployed edge tree, same draws as cluster_sensitivity_cic_present.py; all-class rows reproduce the published intervals. Without BruteForce (+0.036): host pair zero [0.007, 0.199] / present [0.008, 0.105]; attacker host present [0.003, 0.095]; attacker device present [-0.003, 0.099]; capture present [-0.007, 0.064].

## Paper changes
1. Late blocks (Response, contributions, Table I): the 99.5% vs 11.1% contrast was confounded. Text now reports the window-matched decomposition: 97.1-97.2% at flow end, 11.3% with +15 s, 11.1% live; "the export delay, not the window, causes the drop"; its size depends on the attack's time profile (DDoS-SYN: first verdict at 15.2 s, 82% of attack flows already started), so a longer attack would lose a smaller share.
2. Gap beyond BruteForce: convention of +0.036 [0.007, 0.199] stated (missing classes scored 0) with the present-class interval [0.008, 0.105]; coarse-unit without-BruteForce intervals added; claim now "excludes zero by host pair and attacker host but not by attacker device or capture" (Splits and Threats).
3. Table I: "3 in 5.9 h with persistent counters; 2 with corrected labels".
4. Fadel (CIC IoT-DIAD 2024) sentence and bib entry removed: under review, only a GitHub README is public.

## Checks
- Latency 58x -> 63x (R16) confirmed: results/baseline_temporal/report.md single-flow ms, random forest 7.826 / deployed edge tree 0.124 = 63.1x; 58x was 7.826 / 0.136 (the unconstrained decision_tree row).
- MDPI Sensors 26(4) art. 1184 (suggested LOCO citation): could not be found (MDPI 403; Crossref search returned no such record). Not cited.
- PR #263: open (GitHub API, 3 Nov 2026). NFStream #106/#193/#215 titles verified via GitHub API (R16).
- Apruzzese [1]: Crossref pp. 1028-1042; paraphrase backed by abstract quotes ("security operators triage high-level reports -- and not individual samples flagged by some classifier"; evaluations "without carrying out any experiment in a (even synthetic) 'real' network").
- [8] Lanvin, [12] Velan, [23] Ramkumar, [31] Rasheed pp. 275-302, Lyon: verified earlier (CITATION_CHECK_FINAL.md, CITATION_CHECK_R5.md; see REVISION_R13_LOG.md).

## R18 (backup paper\backup_r18\)
- New: `src/analysis/block_timing_long.py` -> `results/final/block_timing_long.md` (5.9 h test periods, audit-corrected labels, verdict at flow end vs flow end + 15 s, reset 60 s and persistent). Persistent, k=1, MITM-ARP ignored: pooled 0.968 -> 0.2033; DDoS-SYN 0.962 -> 0.072 (test period 23 s, 153,402 of 206,430 attack flows); DoS-HTTP 0.96 -> 0.869; Web 0.905 -> 0.884; Recon 0.996 -> 0.50; BruteForce 0.977 -> 0.188.
- Paper: contribution, Table I and Response scoped to "in 60 s windows"; "the 15 s export delay, not the window cut, causes the drop" in short windows; long-horizon numbers added (pooled 96.8% -> 20.3%, driven by the 23 s DDoS-SYN test period; DoS-HTTP 96 -> 87%, web 91 -> 88%, port scan 99.6 -> 50%).
- Latency 63x confirmed (see R17). Page limit: NOMS 2027 = 8 pages main text + references/appendix up to 12; main text ends on page 8, PDF 9 pages. Sensors 26(4) 1184 still not found.

## R19: spelling check (2026-11-03)

- Ran a dictionary spell check (pyspellchecker) over all section sources and main.tex. No misspellings: every flagged word is a name (Mirai, Zeek, Valeros), a tool (tcpreplay, NFStream) or a LaTeX token. No repeated words, no a/an errors, no stray spacing.
- The text used British spelling throughout; IEEE style uses American. Converted 26 words: labelled/labelling/relabelled, behaviour, generalisation/generalise, analysed, favours, defences, licence, artefact, catalogue, memorise (including the index term "dataset labeling" in main.tex). Reference titles in refs.bib are left as published (one "Behaviour"); `conn.log.labeled` is a file name.
- Backup: backup_r19. Build: 9 pages, references on page 8, abstract 250 words, proof check clean.
