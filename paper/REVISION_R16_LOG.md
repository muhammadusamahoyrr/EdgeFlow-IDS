# Revision R16 log: four-agent internal review, applied for IEEE/IFIP NOMS 2027

Backup: `paper\backup_r16\` (state just before R16). Target venue chosen by the author: NOMS 2027.
NOMS rule (read from the CFP page, 3 Nov 2026): "up to 8 (eight) pages for the main text, with additional pages for references and an optional Appendix ... for a maximum of 12 (twelve) pages in total"; the main 8 pages "must be self-contained". NOT verified (TLS error on the page): deadline (scout reported 9 Nov 2026) and whether review is double-blind. The author must check both on the CFP before submitting.
Result: main text ends on page 8 (references start on page 8, end on page 9); abstract 250 words; no undefined refs, no overfull boxes, no BibTeX warnings; check_refs clean.

Reviews (read-only agents): hostile venue reviewer, methods/number auditor, IEEE editor, literature scout. Every adopted claim was re-checked against files or primary sources before writing.

## Errors fixed
- **3.6% "same share live and in replay" was WRONG** (introduced in R13): replay 123/3,410 ignores MITM-ARP verdicts; the live k=1 run counted them. Under the live policy the replay gives 240/3,410 = 7.0% (persistent_counters_corrected.md, "counted"). Response now reports both and says the rates are not comparable with the live counts; Threats/Construct rewritten.
- Abstract and Table I "2 in 5.9 h" -> "3" (original labels, as the abstract states; corrected_headline.md section 5 old/persistent/k=10). Response gives corrected counts and says each original count is one higher; at k >= 5 the extra block is the .174 pair (verified list); k=3 not claimed.
- RF latency 58x -> 63x (baseline_temporal/report.md: 7.826 / 0.124 ms for the deployed edge tree; 58x was vs the other tree).
- Mirai evidence: "temporal Mirai recall 0.90" (contradicts Sec. V: those 10 flows are boundary-spanning) -> "at k=1 all 7 bots were blocked live".
- NFStream novelty narrowed: #215 (2024) diagnosed a different cause (blocking capture loop; maintainer confirmed on PR #227, 27 Jul 2026, GitHub API). Text: our keep-alive ping rules that out; "to our knowledge the LRU-ordering cause was previously undiagnosed". Footnote now cites #106, #120, #193 (symptom only). Contribution bullet reworded ("a previously undiagnosed cause of late flow export").
- Abstract: background defined as traffic not part of the attack; 90.9-98.5% in six of nine captures (Mirai 93.7% was inside the range but unnamed); Zeek clause attached to the right tree; "whose floods" attached to Mirai only; "evidence labels" (not "evidence-based").
- Labels: "91--98.5% ... web, brute-force and MITM-ARP" -> "90.9--98.5% ... six of the nine (web, brute force, MITM-ARP, Mirai)".
- Table VII caption explains 64 (simulation) vs 60 (enforced run) and the Time column (median over pairs blocked at that k).
- Statistics: exact Kruskal-Wallis permutation p = 0.004 (6/1680; groups do not overlap) replaces asymptotic p = 0.027; "responded materially"; OLS d.f. stated, one-core +16 s "not significant (p ~ 0.09)" (t = 2.11, 5 d.f.); replay-rate slope "driven mostly by one run"; audit point estimates with the 11-13% Wilson bound for zero-error strata (label_audit.md); host-pair intervals' missing-class artefact stated with present-class values (cluster_sensitivity_cic_present.md: temporal [0.650, 0.827], difference [0.026, 0.212]; capture [0.007, 0.221]; attacker device [-0.003, 0.225]); "general gap is small and not established" -> "+0.03 to +0.04 excludes zero under host-pair resampling but is not robust to coarser clustering, whose power is low"; Table IV caption: intervals over <= 6 pairs indicative only.
- Live: "sixteen repeat and CPU-budget runs ... (flow-weighted per run)"; "in these runs, at 63-68% ..." (pin_q50_r3 at 68% was +8.9%).

## Framing
- Sections renamed "Check 1-4"; intro uses "stages".
- Intro: NIDS defined; uncited "many report macro-F1 close to the maximum" -> "reported scores are often near the maximum"; Apruzzese 2026 SoK on operators acting on aggregated reports; unifying sentence (each check replaces an aggregate score with its unit: capture, host pair, flow, host-pair window).
- Contributions rewritten with numbers: background share; 78% of +0.14 gap; flow-level CIs several times too narrow (0.039 vs 0.177-0.254 wide); late-block gap 99.5% vs 11.1%.
- Table I: FPR/host pair defined in caption; late-block row; first column widened.
- Late blocks paragraph rewritten. The reviewer's stated cause ("simulation stamps verdict at flow start") was WRONG: tune_block_policy.py uses flow end (last_seen); the text says validation scores whole periods with verdicts at flow end, run-1 uses 60 s windows and logged live verdict times (block_curve.py uses verdict_ms).
- Response reordered (enforced runs before replay; ARP watcher after); Alahmadi et al. (USENIX Sec 2022) on false-alarm burden.
- Related: Fadel (concurrent, under review, CIC IoT-DIAD 2024 folder labels + splits); OVS and SDN defined; Apruzzese 2026; "Few works ... report how many benign hosts a blocking policy cuts off".
- Labels: released-CSV paragraph states its purpose.
- Live: split flows matter downstream (pieces counted separately); exporter generalisation sentence.
- Threats: one-model threat; statistical paragraph reworded. Conclusion: four recommendations + call to release CIC-IoT2023 flows with addresses/timestamps.

## New references (verified 3 Nov 2026)
apruzzese2026reshaping (Crossref, pp. 1028-1042), alahmadi2022falsepositives (USENIX page, pp. 2783-2800), fadel2026diad (GitHub README: "Under review at IJIES, 2026"), nfstream215, nfstream106, nfstream193 (GitHub API).

## Not adopted
- Figure replacing Table I, IEEEabrv, NSGA-II cut: not needed under the NOMS page rule.
- Optional RF file-label LOCO experiment: not run (no-new-experiments advice).
