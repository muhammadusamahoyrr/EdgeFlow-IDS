# Revision R11 log: final polish (bugs, consistency, IEEE format)

Backup: `paper\backup_r11\` (sections\, main.tex, refs.bib), taken before any edit.
Result: 8 pages, no undefined refs/citations, no overfull boxes, no BibTeX warnings, no bare `%`, check_refs.py clean, all fonts Type 1 and embedded. Abstract untouched (250 words).

## Bugs (stale or ambiguous numbers)
- live.tex, Testbed: "replayed at 52--77%" was written before the pinned runs. Over all runs the DDoS-SYN and Mirai windows ran at 46--81% of the original rate (min pin_q100_r3 Mirai 0.455; max pin_q50_r2 DDoS-SYN 0.814; source `results/final/fidelity_all_runs.md`, per-window table). Now "46--81%".
- live.tex, CPU paragraph: "($-15$ s per 1,000 pps)" read as a sign puzzle; now "by 15 s per 1,000 pps less" (OLS −14.56, cpu_factorial.md). "the replay rate" → "the DDoS-SYN replay rate" (the 11,848–14,189 range is that window only). Kruskal–Wallis now gives H = 7.26 with p.
- live.tex footnote: "nfstream \#120" → "nfstream\#120" (same form as #262).

## IEEE format
- Conclusion is now its own numbered section (Section IX); "Discussion" with one subsection became "Threats to Validity" (Section VIII). Label `sec:discussion` was not referenced.
- refs.bib: every conference venue now starts with "Proc." (14 entries changed; "Proceedings of the" shortened, years removed from venue names, "Volume 2" dropped).
- refs.bib: arXiv entries in one form ("arXiv:NNNN.NNNNN, year"); "(per arXiv comment)" removed from Tang et al.
- refs.bib: arpwatch title braces keep "Ethernet" capitalised (IEEEtran had lower-cased it).

## Checked, no change
- All other numbers in the text against the results files and REVISION_D_LOG.md (sixteen runs, 60/1,674 = 3.6%, 79 − 19 = 60, 9 blocked = 6+1+1+1, 32/605 = 0.053, 38,034/52,993 = 71.8%, train + test = 857,206).
- SQLi attacker = .178 (attackers.json), so "UPnP requests of the SQLi attacker" is correct.
- British spelling consistent ("labeling"/"labeled" occur only in cite keys and the Zeek file name).

## Noted, not changed
- Table VII counts 7 Mirai attacker pairs in the live window, the persistent-counter paragraph 6 pairs over the test period (different populations; a reader may ask).
