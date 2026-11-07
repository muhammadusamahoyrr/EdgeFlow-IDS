# Final review: novelty, related work and positioning

Paper: "What Benchmark Scores Hide: Auditing a Flow-Based IoT Intrusion Detector from Labels to Live Blocking" (sections/*.tex, refs.bib, main.pdf as of 2 Nov 2026).
Reviewer focus: ML-based NIDS and IoT security. No paper file was edited.

## Sources checked

- Every candidate paper below was checked against a primary record: Crossref metadata for the DOI, the arXiv API or abstract page, or the publisher or repository page.
- Spot-checked citations were read in the source text: arXiv HTML or abstract pages, and the publisher or institutional-repository page.
- I list only papers I could verify.

---

## 1. Claimed contributions and novelty verdicts

The intro lists four contributions (intro.tex). The split analysis is not a bulleted contribution, but it is Step 2 and Check 2, so I judge it as well.

### C1. The cost of file-name labels, on two datasets (Sec. 4)

**What is claimed**
- The paper measures the background (benign) share in each CIC-IoT2023 attack capture: 91–98.5% for the web, brute-force and MITM captures.
- It reports the measured cost of training on file-name labels:
  - true macro-F1 0.396 against 0.725;
  - Benign FPR 71.8% against 3.8%.
- On IoT-23, a robustness test against the authors' Zeek labels shows 97–100% of background flows flagged.

**Prior work**
- Label and flow-construction errors in NIDS benchmarks are well established:
  - Engelen et al. 2021; Liu et al. 2022;
  - Lanvin et al. 2023 (missed); Rosay et al. 2021/2022 (missed);
  - Flood et al. 2024 (design smells).
- Garcia & Valeros 2023 explicitly predict the failure mode the paper measures, that one label per PCAP teaches the model to call benign OS traffic malicious.
- For CIC-IoT2023, Ramkumar et al. already state that the captures mix benign and attack packets, and they re-filter by MAC address.
- Vitorino et al. re-extract CIC-IoT2023 flows and explicitly assume that each capture holds only its named attack. They also relabel IoT-23 flows from malicious IP/port/protocol combinations.
- Pekar & Jozsa 2024 already rebuilt a benchmark (CICIDS2017) with NFStream to get "methodologically sound flow expiration and labeling". Today the paper cites them only in Sec. 6.

**What is new**
- A per-capture quantification of the background share for CIC-IoT2023. I found no published per-capture table for this dataset.
- A controlled same-model comparison that puts a number on the FPR cost of file-name labels.
- The observation that the released CIC-IoT2023 CSVs cannot be relabelled at all, because they have no addresses or timestamps and the merged files are shuffled. This is a useful, concrete, dataset-specific finding.

**Limits on the claim**
- The labels are produced by a single annotator, and they were revised once in the direction of the model's predictions (Threats).
- The IoT-23 "file labels" are the authors' own family-to-class mapping. Practitioners using IoT-23 normally take the Zeek labels, so the IoT-23 result is a sanity check of the mechanism, not evidence about common practice. The paper says this correctly; keep it that way.
- The mechanism (label noise from mixed captures inflates FPR) is the expected result of what Garcia & Valeros and Ramkumar et al. already describe.

**Verdict: incremental but useful (moderate novelty).** It is the strongest empirical contribution. Present it as "first quantification for CIC-IoT2023", not as discovering the problem. The related-work paragraph already says "Background traffic in attack captures is therefore not new", which is good.

### C2. Live-fidelity check and the failure modes it exposed (Sec. 6)

**What is claimed**
- Flow-by-flow matching of live against offline NFStream flows, with packet accounting.
- Three failure modes:
  - a MAC-learning forwarding pitfall;
  - quiet NFStream meters;
  - an NFStream LRU export-ordering defect that delays verdicts by up to 82.5 s.
- An upstream issue and PR (nfstream#262, #263).

**Prior work**
- Export delay from idle timeouts in flow-based IDS: Hofstede et al., CNSM 2013 (missed).
- Timeouts change flow records and detection: Velan & Jirsík, NOMS 2020 (missed).
- Exporters produce different flows: Vormayr et al., COMST 2020 (missed); Pinto et al. 2025; Vitorino et al.
- Model performance on partial vs complete flows in real time, by the same group the paper cites for NFStream: Pekar & Jozsa, WTMC/EuroS&PW 2025 (missed).
- Replaying archived traffic under a streaming arrival model to test real-time readiness: Zhao & Hassan, CCS 2026 (missed), for graph-based NIDS. They find that none of 18 detector–dataset pairs can alert as events arrive.

**What is new**
- Matching live to offline flows one by one (5-tuple plus order) on the same window, with packet ratios. I found no IoT-NIDS paper that does this.
- Diagnosing the NFStream `NFCache`/`meter_scan` ordering defect. The symptom was reported in nfstream#120 without a cause.

**Limits on the claim**
- The forwarding pitfall and quiet meters are testbed and engineering issues that a careful system builder would expect.
- The NFStream defect is a valuable contribution to practice and to the tool, but it is a software bug fix, not a research result in itself.

**Verdict: moderate novelty as methodology, low as science.** The fidelity check is the most distinctive idea in the paper. Frame it against Hofstede 2013, Velan & Jirsík 2020, Pekar & Jozsa 2025 and Zhao & Hassan 2026, so that it reads as a cheap, generic check that those works motivate but do not provide.

### C3. Response scored in false blocks, with a trade-off over k (Sec. 7)

**What is claimed**
- False blocks counted per host-pair window: 60/1,674 at k=1, 0 at k=10.
- A per-class trade-off over k: Mirai and web attackers are lost at high k.

**Prior work**
- The motivation is already in the sources the paper cites (Garcia & Valeros Sec. VI-C; ATMoS).
- Closed-loop "detect and block in SDN" evaluations exist. A recent example evaluates the time from flow availability to enforced block: Amaral et al., arXiv 2026 (missed).
- Aggregating several alerts before acting (k-of-n) is standard alert-correlation practice.
- Very few papers report collateral blocks per host. I found none that does it on replayed IoT traffic.

**Verdict: small but real novelty in the metric and the reporting.**
- The k-trade-off table is informative.
- The policy idea is not new.
- The evidence is thin: one session per class, one enforced run per policy, and open-loop replay.

### C4. A reusable four-check audit (Sec. 8.1)

**Prior work**
- Arp et al. (10 pitfalls) and Apruzzese et al. (pragmatic assessment) already give checklists for security ML.
- Flood et al. give a catalogue of dataset smells.
- Jacobs et al. (CCS 2022, missed) give a shortcut/underspecification audit for network-security ML.
- Zhao & Hassan (CCS 2026, missed) decompose evaluation into stages and list nine evaluation gaps.
- Catillo et al. (DSN-S 2023, missed) question NIDS benchmark progress.

**What is new**
- Checks 3 (live fidelity) and 4 (false blocks) extend the existing checklists past the offline boundary.
- Checks 1 and 2 overlap with Arp's P1 (sampling bias / label inaccuracy) and P2–P3 (data snooping / temporal), and with Flood's smells.

**Verdict: incremental.**
- The checklist packages known pitfalls plus two deployment-side checks.
- Its value is that it is implemented as scripts and run on two datasets (for Checks 1–2).
- State explicitly which checks are new (3, 4) and which apply known pitfalls (1, 2).

### (Implicit) Splits (Sec. 5)

**Prior work**
- Temporal pitfalls: TESSERACT; Arp et al.; INSOMNIA (Andresini et al., AISec 2021, missed).
- Temporal evaluation on CIC-IoT2023: Traffic-MoE Time-shift; BRIDGE; Rasheed & Alobaedy.
- Temporal evaluation on IoT-23: Lyon et al., CCNC 2026 (missed). They use rolling monthly windows and find degradation as new malware types appear.
- Telnet-to-RTSP brute-force non-generalisation: IoTGeM.

**What is new**
- The within-capture split.
- The boundary-spanning-connection measurement.
- The cluster-unit sensitivity analysis. This is good statistical practice and rarely seen in NIDS papers.

**Limits on the claim**
- The headline finding (BruteForce SSH→RTSP) rests on 3 host pairs.
- The IoT-23 gap does not replicate.
- The SSH→RTSP non-transfer mirrors IoTGeM's telnet→RTSP result, which the paper does acknowledge.

**Verdict: low novelty in finding, moderate in method.** Keep it framed as a method (Check 2), as the paper already does.

### Overall novelty verdict

The paper's novelty is **integrative and methodological, not conceptual**. Each failure mode it studies is known on its own, as the paper itself says in the intro. What is new is three things:

- following one detector end to end, from labels to OVS blocking, and measuring every step;
- the first per-capture background quantification for CIC-IoT2023;
- the live/offline flow-by-flow fidelity check, together with the concrete NFStream defect.

This is an appropriate contribution for a workshop or an experience/measurement track, for example:

- WTMC, the DIMVA or ACSAC experience track, or CNS workshops;
- the IEEE S&P Workshops (SPW/EuroS&PW) or a "Systematization/Experience" track.

It is borderline for a main-track security venue unless:

- the live and response steps are repeated on a second dataset;
- the labels are validated by a second annotator.

---

## 2. Missing related work (verified)

All entries were verified on a primary record (Crossref DOI metadata or the arXiv API/abstract page). The table gives where to cite each one, with a one-clause suggestion.

| # | Reference (verified) | Where | How to cite it |
|---|---|---|---|
| M1 | A. S. Jacobs, R. Beltiukov, W. Willinger, R. A. Ferreira, A. Gupta, L. Z. Granville, "AI/ML for Network Security: The Emperor has no Clothes," ACM CCS 2022, pp. 1537–1551. DOI 10.1145/3548606.3560609 | Intro / Labels | "...and models trained on such benchmarks often rely on shortcuts rather than attack behaviour~\cite{jacobs2022emperor}." |
| M2 | M. Lanvin, P.-F. Gimenez, Y. Han, F. Majorczyk, L. Mé, É. Totel, "Errors in the CICIDS2017 Dataset and the Significant Differences in Detection Performances It Makes," CRiSIS 2022, LNCS 13857, pp. 18–33, Springer 2023. DOI 10.1007/978-3-031-31108-6_2 | Related/Labels | add to "\cite{engelen2021troubleshooting,liu2022error}": "...and measurably change detection scores~\cite{lanvin2023errors}." |
| M3 | M. Rosay, D. Carlier, F. Cheval, P. Leroux, "From CIC-IDS2017 to LYCOS-IDS2017: A corrected dataset for better performance," IEEE/WIC/ACM WI-IAT 2021, pp. 570–575. DOI 10.1145/3486622.3493973 | Related/Labels | "...and corrected re-extractions have been released~\cite{rosay2021lycos}." |
| M4 | G. Andresini, F. Pendlebury, F. Pierazzi, C. Loglisci, A. Appice, L. Cavallaro, "INSOMNIA: Towards Concept-Drift Robustness in Network Intrusion Detection," ACM AISec 2021, pp. 111–122. DOI 10.1145/3474369.3486864 | Related/Splits | "...time-aware evaluation has been applied to NIDS as well~\cite{andresini2021insomnia}." |
| M5 | J. Lyon, E. Saeedizade, S. Sengupta, "Benchmarking Machine Learning Models for IoT Malware Detection under Data Scarcity and Drift," IEEE CCNC 2026, pp. 1–6. DOI 10.1109/CCNC65079.2026.11366512 (arXiv 2601.18736) | Related/Splits (**important**: the only IoT-23 temporal evaluation I found) | "...and on IoT-23, Lyon et al.\ train on earlier months and find performance degrading as new malware types appear~\cite{lyon2026iot23drift}." |
| M6 | R. Hofstede, V. Bartoš, A. Sperotto, A. Pras, "Towards real-time intrusion detection for NetFlow and IPFIX," CNSM 2013, pp. 227–234. DOI 10.1109/CNSM.2013.6727841 | Related/Live; Sec. 6 "Delay" | "...flow export timeouts are known to delay flow-based detection~\cite{hofstede2013realtime}." |
| M7 | P. Velan, T. Jirsík, "On the Impact of Flow Monitoring Configuration," IEEE/IFIP NOMS 2020, pp. 1–7. DOI 10.1109/NOMS47738.2020.9110361 | Related/Live; Setup (timeout choice) | "...and the choice of expiration timeouts changes both the flow records and detection results~\cite{velan2020impact}." |
| M8 | G. Vormayr, J. Fabini, T. Zseby, "Why are My Flows Different? A Tutorial on Flow Exporters," IEEE COMST 22(3), 2020, pp. 2064–2103. DOI 10.1109/COMST.2020.2989695 | Related/Live | add next to Hofstede 2014: "...and exporters disagree flow by flow~\cite{vormayr2020flows}." |
| M9 | A. Pekar, R. Jozsa, "Early-Stage Anomaly Detection: A Study of Model Performance on Complete vs. Partial Flows," 2025 IEEE EuroS&P Workshops (WTMC), pp. 153–163. DOI 10.1109/EuroSPW67616.2025.00024 | Related/Live; Conclusion (early classification) | "...and models trained on complete flows lose up to 30% precision/recall on the partial flows a live system sees~\cite{pekar2025early}." |
| M10 | R. Zhao, W. U. Hassan, "A First-Principles Evaluation of Graph-Based Network Intrusion Detection Systems," accepted at ACM CCS 2026; arXiv 2609.12263 | Intro / Related/Live / Checklist | "...a streaming replay of graph-based NIDS found that none of 18 detector–dataset pairs could alert as events arrive~\cite{zhao2026gidseval}." |
| M11 | A. Amaral, F. Moro, A. Malheiro, "Autonomous Cyber Defense: Real-Time Attack Detection and Mitigation in Software-Defined Networks Using Machine Learning," arXiv 2608.22075 (2026), preprint | Related/Response | "...recent closed-loop SDN work measures time to block~\cite{amaral2026autonomous}, but not false blocks." |
| M12 | R. Catillo, A. Pecchia, U. Villano, "Machine Learning on Public Intrusion Datasets: Academic Hype or Concrete Advances in NIDS?," IEEE/IFIP DSN-S 2023, pp. 132–136. DOI 10.1109/DSN-S58398.2023.00038 | Intro | add to "\cite{arp2022dos,apruzzese2023sok}" in the benchmark-gap sentence. |
| M13 | P. Goldschmidt, D. Chudá, "Network Intrusion Datasets: A Survey, Limitations, and Recommendations," Computers & Security 156 (2025) 104510. DOI 10.1016/j.cose.2025.104510 | Related/Labels | "...see Goldschmidt and Chudá for a survey of 89 NIDS datasets and their limitations~\cite{goldschmidt2025survey}." |
| M14 | G. D'hooge, M. Verkerken, B. Volckaert, T. Wauters, F. De Turck, "Establishing the Contaminating Effect of Metadata Feature Inclusion in Machine-Learned Network Intrusion Detection Models," DIMVA 2022, LNCS, pp. 23–41. DOI 10.1007/978-3-031-09484-2_2 | Setup (identifier exclusion) | add to "\cite{arp2022dos}": "...identifiers let a model memorise the capture~\cite{arp2022dos,dhooge2022metadata}." |
| M15 | M. M. Galal, "Provenance, Not Behaviour: A Serialisation Artifact in Edge-IIoTset and a Leakage-Free Benchmark for Precision-Agriculture Intrusion Detection," arXiv 2608.15761 (2026), preprint | Related/Labels | "...in another IoT benchmark the label is recoverable from a file-provenance artifact alone~\cite{galal2026provenance}." |
| M16 | A. Tolay, "Beyond Detection Accuracy: Measuring Explanation Cost, Stability, and Utility for Resource-Aware IoT Intrusion Detection," arXiv 2608.10349 (2026), preprint | Labels ("benchmark as distributed") | "...the released CIC-IoT2023 CSVs also contain exact duplicates and label collisions~\cite{tolay2026beyond}." (Confirmed in the abstract: "exact-feature deduplication, conservative label-collision removal".) |

Optional, lower priority:
- **Cantone, Marrocco, Bria**, "Machine Learning in Network Intrusion Detection: A Cross-Dataset Generalization Study," IEEE Access 12 (2024) 144489–144508, DOI 10.1109/ACCESS.2024.3472907. Cite next to `ali2026siamxbert` in External threats.
- **Ceschin et al.**, "Machine Learning (In) Security: A Stream of Problems," ACM DTRAP 5 (2024), DOI 10.1145/3617897. Cite for offline vs online evaluation criteria.

**Searches that found nothing.** Several gaps the paper could claim have no published counterpart that I could find (2023–Nov 2026):
- no published audit that quantifies per-capture background in CIC-IoT2023, other than Ramkumar et al. (qualitative);
- no paper that diagnoses NFStream export-timing behaviour;
- no IoT-NIDS paper that matches live flows to offline flows one by one.

These remain the paper's defensible "first" claims. Phrase them as "to our knowledge".

---

## 3. Citation spot-check (13 checked)

| Citation (where) | Claim in paper | Verdict |
|---|---|---|
| rasheed2026drift (related) | quote "specific behaviour changes, such as total blindness, sensitivity inflation and relatively stable detection" | **OK, verbatim** (MMU eprints 16573 abstract). Datasets: CIC-IoT-2023, Edge-IIoTset, UNSW-NB15. |
| rasheed2026drift (splits) | "blindness" analogy | OK. |
| pekar2024integrity (live) | maps NFStream to CICFlowMeter; quote "the specific mechanisms employed for updating and terminating flows"; out of scope | **OK, verbatim** (Sec. 7.2; Table 5 is the mapping). Also add a Labels mention (see C1). |
| garcia2023labeling (related) | "in files or directory names" (abstract) | OK. Source: "most analyzed datasets assigning labels in files or directory names". |
| garcia2023labeling (related) | "sometimes contain errors that require significant effort to correct" (Sec. 2.2) | OK verbatim. The arXiv numbering is II-B; Garcia & Valeros are themselves citing their ref. [33]. |
| garcia2023labeling (labels) | "may learn to detect operating system benign traffic as malicious" (Sec. 3.2) | OK verbatim (III-B in the arXiv HTML). |
| garcia2023labeling (response) | few FPs have strong consequences with IP blocking; earlier alerts only at controlled FPR (Sec. 6.3–6.4) | OK (VI-C: "a few false positives can have strong consequences for an organization"; VI-D: "...balanced with the detection performance (e.g., FPR)"). |
| akbari2020atmos (response) | dropping suspected traffic can have severe consequences | OK (Sec. II, verified in round 5 and consistent with the source). |
| vitorino2025revisiting (related) | re-extract CIC-IoT2023 flows and assume each capture holds only its attack | **OK**: "it was considered that the only traffic present in each capture is exclusively the one identified in its name" (arXiv 2511.08345). They also relabel IoT-23 by malicious IP/port/protocol combinations; mention this, since it is close to the paper's IoT-23 label join. |
| kostas2024iotgem (related, splits) | trains on telnet, tests on RTSP brute force; variants do not generalise | **OK** ("the training data involves telnet BF", "the test data involves a RTSP BF attack", "may limit the ability of telnet BF models to generalize to RTSP BF attacks"). |
| kostas2024iotgem (related, labels) | "IoTGeM reports benign packets inside the attack captures of another IoT dataset" | **WEAK / not found.** I read arXiv v2 (2401.01343) in full in three passes and found no explicit statement. The closest is an inference in the UDP-flood discussion ("if it is TCP, it is benign"). Either give the exact section/page in the Computer Networks version, or drop or soften the sentence. |
| zhou2026trafficmoe (related) | "per-class chronological split on packet bytes" on CIC-IoT2023 | **Mostly OK.** Appendix I "Time-shift": flows of each category sorted by timestamp, earliest 40% train / latest 40% test, middle 20% discarded. CICIoT2023 is in the fine-tuning set. However, the appendix does not name the Time-shift dataset; its example is DDoS sub-types, which CICIoT2023 has, but so does CICIoMT2024. Inputs are header-feature plus payload bytes, not raw packets. Check the results table before keeping "on CIC-IoT2023". |
| bridge2026tchnet (related) | early/late split in a pooled benchmark | OK (Sec. 5.8: "training on early windows, testing on later windows", on the combined dataset; single seed; ΔF1 −0.009). Whether CIC-IoT2023 rows enter that split is implied by the pooling but not stated. |
| schraven2026mawiflow (related) | tree classifiers degrade over time on MAWI flows | OK (abstract: tree models do well on static data but degrade significantly over time). |
| ramkumar2024diagnosing (related) | captures mix benign and attack traffic; re-filtered per device by MAC; did not quantify | OK (arXiv 2412.10738: original files "consisted of a mix of benign packets for devices not being attacked with attack packets"; re-filtered by MAC with tcpdump). |
| bawany2017ddos, yan2016sdn (related) | "gating a block on several verdicts appear[s] in SDN mitigation work" | **UNVERIFIED / likely over-attributed.** These are 2016/17 SDN-DDoS surveys. They support OpenFlow drop-rule mitigation, but I could not confirm that either describes requiring k verdicts before blocking. Keep them for drop rules only, and either cite a specific work for multi-verdict gating or present that gating as the paper's own design choice. |

No citation is clearly misused in the sense of contradicting its source. The two quotes fixed in round 5 (Rasheed, Pekar) are now verbatim. **Two claims need action:** the IoTGeM benign-packets claim and the Bawany/Yan multi-verdict claim. One needs a check: whether the Traffic-MoE Time-shift result is on CIC-IoT2023.

Minor points:
- The Garcia & Valeros section numbers use arabic numbering (2.2, 3.2, 6.3–6.4), while arXiv v1 uses roman (II-B, III-B, VI-C/D). This is acceptable, but "Sec. II-B" etc. would match the source exactly.
- Related work says "few works we found report false-block counts on replayed traffic". This is fine, but add Amaral et al. (M11) so the claim is visibly checked against the closest recent work.
- The intro says "Live prototypes rarely check that they classify the flows the model was evaluated on" without any citation. Support it with Zhao & Hassan (M10) and Pekar & Jozsa 2025 (M9), which show the offline/online gap from other angles.

---

## 4. Suggested positioning sentence for the intro

Use it after the "sources of this gap are usually studied one at a time" paragraph:

> Prior work has established each of these problems separately: benchmark label and flow errors~\cite{engelen2021troubleshooting,liu2022error,lanvin2023errors,flood2024smells}, mixed traffic in CIC-IoT2023 captures~\cite{ramkumar2024diagnosing}, time-unaware splits~\cite{pendlebury2019tesseract,arp2022dos,andresini2021insomnia}, exporter and timeout effects~\cite{hofstede2013realtime,velan2020impact,pinto2025flowexporter}, and the gap between benchmark and streaming operation~\cite{pekar2025early,zhao2026gidseval}. We do not claim a new failure mode. Our contribution is to measure all of them on one ordinary IoT detector, end to end. This yields three results we found nowhere else:
> - a per-capture quantification of background traffic in CIC-IoT2023, with the measured cost of file-name labels;
> - a flow-by-flow check that the live gateway classifies the same flows as the offline evaluation, which exposed a previously undiagnosed NFStream export-timing defect;
> - blocking scored in falsely blocked host pairs.

Shorter alternative for the abstract or the contributions lead-in:

> Each pitfall we examine is individually known; what is new is a single detector audited from labels to live blocking, with per-capture label costs for CIC-IoT2023, a live/offline flow-fidelity check, and false-block accounting.

---

## 5. Summary of recommended actions

1. Add M5 (Lyon et al., IoT-23 temporal, CCNC 2026) and M9/M10 (Pekar & Jozsa 2025; Zhao & Hassan CCS 2026). These are the closest missed works on splits and live evaluation. Add M6–M8 for exporter timeouts and M2/M1 for labels and shortcuts.
2. Fix or soften the IoTGeM "benign packets" sentence. Re-attribute or drop "gating a block on several verdicts" for Bawany/Yan. Confirm the Traffic-MoE Time-shift dataset.
3. Cite Pekar & Jozsa 2024 in the Labels paragraph as well, since they rebuilt CICIDS2017 with NFStream for sound labelling. Note Vitorino et al.'s IoT-23 IP/port relabelling next to your Zeek join.
4. In Sec. 8.1, state which checks are new (3 Live, 4 Response) and which apply known pitfalls (1, 2: Arp P1–P3, Flood smells).
5. Insert the positioning sentence (Sec. 4 of this review). Keep the "to our knowledge" qualifiers on the per-capture CIC-IoT2023 quantification and the NFStream diagnosis.
