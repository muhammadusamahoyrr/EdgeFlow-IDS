# Citation check (final), 2026-11-02

Scope: the candidate references in FINAL_REVIEW_novelty.md, Sec. 2, and the three open items in Sec. 3. No paper files were edited. Verified BibTeX is in `refs_final_candidates.bib`.

**Sources.** Bibliographic metadata comes from Crossref (`api.crossref.org/works/<doi>`) and arXiv abstract pages. Claims were checked against full text where an open copy existed (arXiv PDFs). ACM DL, IEEE Xplore, SpringerLink, ScienceDirect, HAL, DBLP and the university repositories returned 403 or bot walls. For those items, the abstract text was taken from the Semantic Scholar or OpenAlex record, which mirrors the publisher abstract. These cases are marked "(abstract via S2/OpenAlex)".

Verdicts: **CONFIRMED** (metadata and claim supported), **WRONG** (contradicted or misattributed), **UNVERIFIABLE** (could not be checked against an accessible primary text).

---

## 1. New candidate references

### lyon2026iot23drift: CONFIRMED
- Crossref: "Benchmarking Machine Learning Models for IoT Malware Detection under Data Scarcity and Drift". Authors: Jake Lyon, Ehsan Saeedizade, Shamik Sengupta. Venue: 2026 IEEE 23rd Consumer Communications & Networking Conference (CCNC). Pages 1–6. Published 2026-01-09. DOI 10.1109/CCNC65079.2026.11366512. arXiv 2601.18736 (v1, 26 Jan 2026) has the same title and authors.
- Claim: "train on earlier months and find performance degrading as new malware types appear". Supported by arXiv Sec. IV-D "Temporal Analysis":
  - "models are trained on data from earlier months and evaluated on traffic from subsequent months"
  - "As new malware types appear in later months, performance begins to degrade."
  - The dataset is IoT-23 (abstract).
- Nuance: the paper uses a rolling window and reports that RF "has a more stable performance over time". The proposed sentence is accurate.

### pekar2025early: CONFIRMED, with a wording fix
- Crossref: "Early-Stage Anomaly Detection: A Study of Model Performance on Complete vs. Partial Flows". Authors: Adrian Pekar, Richard Jozsa. Venue: 2025 IEEE European Symposium on Security and Privacy Workshops (EuroS&PW). Pages 153–163. Published 2025-06-30. DOI 10.1109/EuroSPW67616.2025.00024.
- arXiv 2407.02856 v3 carries the comment "accepted for presentation at WTMC 2025".
- Claim "up to 30% precision/recall" is supported:
  - Abstract: "precision and recall dropping by up to 30% under certain conditions when models trained on complete flows are tested against partial flows"
  - Sec. 1 repeats it ("up to 30% drop in precision/recall under certain conditions"), and so does Sec. 5.
- The study uses a single model (Random Forest) and one evaluated dataset. Keep the qualifier. Proposed: "...models trained on complete flows lose up to 30% precision and recall, under certain conditions, when tested on partial flows~\cite{pekar2025early}."

### zhao2026gidseval: CONFIRMED (as arXiv preprint, accepted to CCS 2026)
- arXiv 2609.12263 v1 (10 Sep 2026): "A First-Principles Evaluation of Graph-Based Network Intrusion Detection Systems". Authors: Rui Zhao, Wajih Ul Hassan.
- The arXiv comment reads: "Full version of the paper accepted to the ACM Conference on Computer and Communications Security (CCS) 2026."
- The PDF's ACM reference block gives CCS '26, The Hague, 15–19 Nov 2026, DOI 10.1145/3830454.3846576. That DOI is **not yet registered**: Crossref and doi.org both return 404. So the bib cites the arXiv version with an acceptance note. Switch to @inproceedings with the DOI once it resolves.
- Claim "none of 18 detector–dataset pairs could alert as events arrive" is supported:
  - Abstract: "none of the 18 detector-dataset pairs we replay can alert as events arrive"
  - Sec. 4, EG9 "Missing Real-Time Detection": "Across 54 replay jobs covering 18 detector-dataset pairs ... none of the 18 pairs is real-time ready"
- Caveat: these are graph-based NIDS (GIDS), and 4 of the 18 pairs are "near real-time". Say "graph-based NIDS" explicitly, as the review's sentence already does.

### hofstede2013realtime: CONFIRMED (abstract via S2/OpenAlex)
- Crossref: "Towards real-time intrusion detection for NetFlow and IPFIX". Authors (Crossref spelling): Rick Hofstede, Vaclav Bartos, Anna Sperotto, Aiko Pras. Venue: Proc. 9th Int. Conf. on Network and Service Management (CNSM 2013). Pages 227–234. Published Oct 2013. DOI 10.1109/CNSM.2013.6727841.
- Claim "flow export timeouts delay flow-based detection" is supported by the abstract: "the analysis is performed after certain timeouts, which generally delays the intrusion detection for several minutes."

### velan2020impact: CONFIRMED (abstract via S2/OpenAlex)
- Crossref: "On the Impact of Flow Monitoring Configuration". Authors (Crossref spelling): Petr Velan, Tomas Jirsik. Venue: NOMS 2020 – IEEE/IFIP Network Operations and Management Symposium. Pages 1–7. Published Apr 2020. DOI 10.1109/NOMS47738.2020.9110361.
- Claim "choice of expiration timeouts changes both the flow records and detection results" is supported by the abstract:
  - "We analyse their effect on the number of created flow records"
  - "the choice of the flow expiration timeouts can have a severe impact on the network data analytics"
  - The paper uses Slowloris detection as its use case.
- Precise wording: "...and the choice of flow expiration timeouts changes the flow records and can severely affect detection~\cite{velan2020impact}."

### jacobs2022emperor: CONFIRMED, with a wording fix (abstract via S2)
- Crossref: title "AI/ML for Network Security", subtitle "The Emperor has no Clothes". Authors: Arthur S. Jacobs, Roman Beltiukov, Walter Willinger, Ronaldo A. Ferreira, Arpit Gupta, Lisandro Z. Granville. Venue: Proc. 2022 ACM SIGSAC CCS. Pages 1537–1551. Published 2022-11-07. DOI 10.1145/3548606.3560609.
- The abstract supports shortcuts: Trustee is used to identify "evidence of shortcut learning, presence of spurious correlations, and vulnerability to out-of-distribution samples" in published models.
- "Often" is stronger than the source. The paper shows instances in a few reproducible models, not prevalence. Proposed: "...models trained on such benchmarks can rely on shortcuts rather than attack behaviour~\cite{jacobs2022emperor}."

### lanvin2023errors: CONFIRMED (abstract via S2)
- Crossref (book chapter): "Errors in the CICIDS2017 Dataset and the Significant Differences in Detection Performances It Makes". Authors: Maxime Lanvin, Pierre-François Gimenez, Yufei Han, Frédéric Majorczyk, Ludovic Mé, Éric Totel. In: Risks and Security of Internet and Systems (CRiSIS 2022), LNCS, Springer Nature Switzerland (Cham). Pages 18–33. Year 2023. DOI 10.1007/978-3-031-31108-6_2.
- Neither Crossref nor the book record gives the LNCS volume number. The review's "LNCS 13857" could not be confirmed because DBLP and Springer are behind bot walls, so the bib omits the volume.
- Claim "measurably change detection scores" is supported:
  - Abstract: "we assess the impact of these different corrections on the evaluation of supervised intrusion detection approaches"
  - The title states "Significant Differences in Detection Performances".

### andresini2021insomnia: CONFIRMED (abstract via S2)
- Crossref: title "INSOMNIA", subtitle "Towards Concept-Drift Robustness in Network Intrusion Detection". Authors: Giuseppina Andresini, Feargus Pendlebury, Fabio Pierazzi, Corrado Loglisci, Annalisa Appice, Lorenzo Cavallaro. Venue: Proc. 14th ACM Workshop on Artificial Intelligence and Security (AISec, co-located with CCS '21). Pages 111–122. Published 2021-11-15. DOI 10.1145/3474369.3486864.
- Claim "time-aware evaluation applied to NIDS" is supported by the abstract: "we extend TESSERACT - a framework originally proposed for performing sound time-aware evaluations of ML-based malware detectors - to the network intrusion domain."

### vormayr2020flows: CONFIRMED (abstract via S2/OpenAlex)
- Crossref: "Why are My Flows Different? A Tutorial on Flow Exporters". Authors: Gernot Vormayr, Joachim Fabini, Tanja Zseby. Venue: IEEE Communications Surveys & Tutorials 22(3). Pages 2064–2103. Year 2020. DOI 10.1109/COMST.2020.2989695.
- Claim "exporters disagree flow by flow" is supported by the abstract:
  - "the flow output of distinct flow exporters ... varies substantially on identical network packet stream input"
  - "we present a flow-by-flow comparison of the analyzed flow exporters' output"

---

## 2. Existing paper claims

### a. kostas2024iotgem, "benign packets inside the attack captures of another IoT dataset": CONFIRMED (arXiv v2); exact location in the journal version UNVERIFIABLE

**Found in arXiv 2401.01343 v2**, Appendix A.3 "Issues with the IoTID20 Dataset" (p. 20 of the preprint PDF). This is the supplementary appendix, which earlier read-throughs may have missed:

> "distinct pcap files are apparent, each corresponding to a specific attack and session. However, these files encompass not only malicious packets but also benign ones within each attack file."

The appendix goes on to say that IoTID20 appears to have disregarded the IoT-NID packet-labelling rules, "resulting in the mislabelling of all pcap files as attacks".

- The "another IoT dataset" is the IoT-NID raw captures, and the derived IoTID20 CSVs mislabel them. The main text points to this at the "Appendix A.3) identified anomalies" line in the dataset section.
- ScienceDirect (10.1016/j.comnet.2025.111550) returned 403, so the appendix label and page in the published Computer Networks version could not be checked.
- arXiv v2 (12 Jun 2025) is the "Preprint submitted to Elsevier", and its journal-ref is "Computer Networks, Volume 270, October 2025, Article 111550". It almost certainly matches.

Proposed replacement (more precise):
> "Kostas et al.\ note that the attack pcaps of IoT-NID also contain benign packets, and that the derived IoTID20 flows label all of them as attacks~\cite[App.~A.3]{kostas2024iotgem}."

### b. bawany2017ddos / yan2016sdn for "gating a block on several verdicts": UNVERIFIABLE for gating (likely over-attributed); CONFIRMED for SDN drop-rule mitigation

- Metadata is correct per Crossref:
  - Bawany, Shamsi, Salah, Arab. J. Sci. Eng. 42(2):425–441, 2017, DOI 10.1007/s13369-017-2414-5.
  - Yan, Yu, Gong, Li, IEEE COMST 18(1):602–622, 2016, DOI 10.1109/COMST.2015.2487361.
- Full texts are paywalled (SpringerLink redirects to login; IEEE returns 403). The publisher has elided Bawany's abstract from S2.
- Yan's abstract covers SDN's ability for "dynamic updating of forwarding rules" to "detect and react to DDoS attacks". It says nothing about requiring several detections or a count threshold before blocking.
- No accessible text supports the multi-verdict gating attribution.

Proposed wording:
> "Blocking via OpenFlow/OVS drop rules is standard in SDN DDoS mitigation~\cite{bawany2017ddos,yan2016sdn}. Our requirement of $k$ verdicts before a block is a design choice that we evaluate in Sec.~7. Our ARP rule is the classic arpwatch idea~\cite{arpwatch}."

If a prior-art citation for k-of-n gating is wanted, it needs a specific, checked source. None was verified here.

### c. zhou2026trafficmoe, Time-shift on CIC-IoT2023: CONFIRMED

arXiv 2601.00357 v2 (8 Jul 2026), Sec. V-H "Evaluation under Distribution Shifts", **Fig. 8** "Performance under different distribution shifts". The Fig. 8 panels are titled "CICIoT2023: Time-shift" and "CICIoMT2024: Time-shift" and report Macro-Recall and Macro-F1. The results are in a figure, not a table.

Sec. V-H text:
> "we construct three OOD benchmarks: Time-shift (simulating concept drift over time) ... Figure 8 visualizes the performance comparison"

and Traffic-MoE outperforms "the runner-up by 32.31%–60.18% across datasets".

Appendix I "Detailed Evaluation under Distribution Shifts": flows of each category are sorted "by timestamp", with "the first 40% of the time span as the training domain and the last 40% as the testing domain, discarding the middle 20%".

- The input comes from Traffic2Token, a byte-level representation that combines "protocol metadata with selective payload segments".
- Proposed wording:
  > "Traffic-MoE evaluates a per-class chronological split (first 40\% of each class's time span for training, last 40\% for testing) on CIC-IoT2023 and CICIoMT2024, using byte-level flow tokens~\cite{zhou2026trafficmoe}."
- If v1 was the version read before, cite v2 or check v1, since the figure location is v2's.

---

## Summary

| Item | Verdict |
|---|---|
| lyon2026iot23drift | CONFIRMED |
| pekar2025early (incl. up to 30%) | CONFIRMED; keep "under certain conditions" |
| zhao2026gidseval (CCS 2026, 18 pairs) | CONFIRMED; ACM DOI not yet registered, so cite arXiv |
| hofstede2013realtime | CONFIRMED |
| velan2020impact | CONFIRMED |
| jacobs2022emperor | CONFIRMED; change "often" to "can" |
| lanvin2023errors | CONFIRMED; LNCS volume 13857 unverified, so omitted |
| andresini2021insomnia | CONFIRMED |
| vormayr2020flows | CONFIRMED |
| kostas2024iotgem benign-packets | CONFIRMED in arXiv v2 App. A.3; journal page/label UNVERIFIABLE (paywall); make the sentence more specific |
| bawany2017ddos / yan2016sdn multi-verdict gating | UNVERIFIABLE (no support found); keep them for drop rules only and present k-gating as own design |
| zhou2026trafficmoe Time-shift on CIC-IoT2023 | CONFIRMED (v2, Fig. 8, App. I) |

None of the checked citations is WRONG in the sense of contradicting its source. The Bawany/Yan gating attribution is the only one that should be removed.
