# Revision R13 log: final reviewer items

Backup: `paper\backup_r13\`. Result: 8 pages, abstract 248 words, no undefined refs, no overfull boxes, no BibTeX warnings.

## Fixes
1. **10-verdict overstatement.** Abstract: "caused none in the ten live windows (2 in 5.9 h with persistent counters)". Table I row 4: "none live at k=10 (2 in 5.9 h with persistent counters)". Source: corrected_headline.md section 5 / persistent_counters_corrected.md (persistent, k=10, 2 false blocks).
2. **"21 per hour" vs "21 at k=3".** Both correct, different things: k=1 replay = 123 false blocks / 5.91 h = 20.8/h; k=3 persistent = 21 false blocks. Text now gives k=1 as a per-pair share: 123 of 3,410 benign-only pairs = 3.6%, same as live 60/1,674 = 3.6%; per-hour (21) depends on traffic mix. The k=3 sentence now reads "2 at k=10, 6 at k=5 and 21 at k=3". Discussion Construct updated the same way.
3. **Mixed label states.** Labels: "The abstract and tables keep the original labels, which understate the evidence-label tree." Table III caption: "Original labels (corrected values in the text)."
4. **Garcia & Valeros.** "11 label flows, while file or directory names combined (14) are more common than any other style".
5. **Manual check of undecided flows.** NOT done by a person. Prepared `results/final/manual_check_sheet.csv` (100 of the 239 undecided C/D/B-fn flows, seed 0; 53 D, 29 C, 18 B-fn; blind) and `manual_check_key.csv`; script `src/analysis/make_manual_sheet.py`.

Space: abstract trimmed ("only", "i.e.", "of traffic"); Threats dropped the generic "No packets were lost refers only to these runs"; Response 52%-replay sentence shortened.

## Reference verification (primary sources, earlier rounds + today)
- Tang et al. [4]: F1 0.970148 (Table IV), recall .0095 (Table VII), arXiv 2609.24393v1. CITATION_CHECK_R5.md §5.
- Lanvin et al. [7]: Crossref, LNCS chapter pp. 18-33, DOI 10.1007/978-3-031-31108-6_2. CITATION_CHECK_FINAL.md.
- Velan & Jirsik [11]: Crossref, NOMS 2020, DOI 10.1109/NOMS47738.2020.9110361; quotes from abstract.
- Ramkumar et al. [22]: Crossref, IEEE TSE 51(11):3117-3137, DOI 10.1109/TSE.2025.3610540; claim from arXiv 2412.10738.
- Lyon et al.: Crossref CCNC 2026, DOI 10.1109/CCNC65079.2026.11366512; quotes from arXiv 2601.18736 Sec. IV-D.
- Kostas et al. App. A.3: in arXiv 2401.01343 v2 (p. 20). The bib cites the Computer Networks version, whose appendix numbering could not be checked (paywall).
- PR #263 / issue #262: open (GitHub, 3 Nov 2026).

## Proofread
Automated: no doubled words, no space before \cite/\ref, no common typos; British spelling in running text (American forms only in reference titles and the Zeek file name).

## R14 (follow-up, same day; backup paper\backup_r14\)
- "Mirai missed by the detector" -> "by the flow-count rule" (Table I); Response: "The Mirai loss belongs to the flow-count rule, not to the classifier (temporal Mirai recall 0.90) or the reset". Recall 0.90 from Table IV.
- Traffic-MoE: "the middle 20% discarded as a buffer" added (CITATION_CHECK_FINAL.md, v2 App. I); contrast: "Our split, within each capture, has no buffer; we measure the connections that span it" (36.1% boundary-spanning, Section V).
- Rasheed pages 275-302: confirmed on publisher page / DOI 10.19101/IJATEE.2026.131340379 (CITATION_CHECK_R5.md table).
- Space: related/response/live sentences tightened; IoT-23 framing shortened; "Requiring k verdicts is our design choice" and the LOCO caveat sentence in Threats removed.
- Result: 8 pages, abstract 248 words, all checks clean.

## R15 (follow-up; backup paper\backup_r15\)
- Traffic-MoE: "per-class" / "each class's time span" removed (only the 40/40/20 split is verbatim in v2 App. I); now "first 40% of the time span ... middle 20% discarded as a buffer".
- Tang et al. [4]: "hold-out F1 0.97 on UNSW-NB15 that detected 1 of 105 attacks (recall 0.0095) ... on a small labelled laboratory capture". Verified 3 Nov 2026 in arXiv 2609.24393v1: abstract (UNSW-NB15, RF-21 F1 = 0.970148), Sec. IV ("538 events (105 Attack, 433 Normal)"), Table VII (TP 1, FN 104). The paper calls these small laboratory tests; capture size in bytes is not stated.
- [29] = Rasheed (pp. 275-302), confirmed earlier via publisher page/DOI.
- Result: 8 pages, no undefined refs, no overfull boxes.
