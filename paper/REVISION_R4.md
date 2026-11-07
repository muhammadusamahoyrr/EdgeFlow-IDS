# Round-4 revision: second dataset, benchmark-as-distributed, verified citations, upstream PR, toolkit framing

Source of truth: result files. Do not invent numbers. Keep the paper at **8 pages or fewer**,
IEEE two-column, including references. To make room, shorten older material: the CPU table
(fold it into the repeats table or cut rows), long harness text, and repeated numbers.

## A. Second dataset: IoT-23 (results/iot23/*.md)
IoT-23: Garcia, Parmisano, Erquiaga, Zenodo doi 10.5281/zenodo.4743746 (key `garcia2020iot23`,
already in refs.bib).

- **Pipeline.**
  - 10 scenarios: 7 malware, 3 honeypot/benign.
  - Same NFStream settings and edge tree.
  - Labels come from the dataset's own Zeek `conn.log.labeled`, joined on unordered 5-tuple plus
    nearest start (±2 s), otherwise the flow start inside a Zeek connection.
  - 756,306 flows; match 99.99%; 38 unmatched flows dropped.
- **Background share per malware capture** (Zeek label Benign):

  | Capture | Background share |
  |---|---|
  | Trojan 42-1 | 0.999 |
  | Torii 20-1 | 0.818 |
  | Torii 21-1 | 0.822 |
  | Hide&Seek 1-1 | 0.696 |
  | Hakai 8-1 | 0.347 |
  | Mirai 34-1 | 0.241 |
  | Muhstik 3-1 | 0.055 |

- **File-label baseline.**
  - The file label is the family's main behaviour, e.g. Hide&Seek→PortScan, Torii→C&C,
    Mirai→DDoS. 63.1% of flows have a file label that differs from the Zeek label.
  - Temporal split, file labels: true macro-F1 0.169, Benign FPR 98.5%, apparent 0.649. Zeek
    labels: 0.649 and 3.4%.
  - Stratified split, file labels: 0.149 and 98.4%, apparent 0.692. Zeek labels: 0.863 and 3.7%.
- **Splits (results/iot23/splits.md). Report honestly: on IoT-23 this does NOT replicate the
  CIC-IoT2023 temporal gap.**
  - Temporal macro-F1 is 0.649 and stratified is 0.863, but the gap comes from missing classes.
    Under the temporal split DDoS has 0 training flows and FileDownload has 0 test flows, so both
    score 0 by construction.
  - On the 4 classes present in both splits, temporal scores 0.973 and stratified 0.956.
  - The stratified macro-F1 rests on 63 DDoS and 2 FileDownload test flows from 1–2 host pairs.
    Its host-pair CI is [0.638, 0.939], against a flow CI of [0.764, 0.923].
  - C&C has 7–10 host pairs: F1 0.945 has a host-pair CI of [0.731, 0.983], against a flow CI of
    [0.941, 0.949].
  - Boundary-spanning test flows: 4.1% temporal and 5.8% stratified; for C&C, 36.5% and 68%.
    Without them, stratified falls from 0.863 to 0.809 and temporal stays at 0.649.
  - **Lessons to state:**
    - A per-class temporal split must check class presence in both halves.
    - Flow-level CIs understate uncertainty; host-pair CIs are the honest ones.
    - Stratified leakage via boundary-spanning flows recurs (C&C 68%).
  - Treat this as a nuance, and don't claim "the temporal split result replicates".
- **Other IoT-23 facts:**
  - Okiru is excluded (≥1 GB); "Attack" comes only from scenario 3-1.
  - DDoS: 14,394 Zeek rows on 317 tuples become 211 NFStream flows.
  - Mapping a family to its main behaviour for file labels is our choice; say so.
- **The difference from CIC-IoT2023 must be stated:** here the labels are the dataset authors'
  Zeek labels, not ours, so the audit uses the benchmark's own ground truth. That strengthens the
  file-label finding: it does not depend on our labelling.
- **Placement.** IoT-23 is replication evidence for Steps 1–2 (Labels, Splits). Add it as a
  compact table and paragraph per step, or as one subsection "Replication on IoT-23". Do not run
  the live steps on it.

## B. The benchmark as distributed (results/official_csv_baseline.md)
- The official per-pcap CIC-IoT2023 CSVs hold 39 packet-window features. They have no IPs, no
  timestamps and no label column; the label is the file name. They cannot be relabelled from
  evidence.
- On the same ten captures with file labels, a stratified random split gives macro-F1 0.749
  (decision tree) and 0.803 (random forest), accuracy 0.82 and 0.87. BruteForce recall is
  0.43/0.41 and Web recall 0.37/0.35.
- A row-order split gives 0.727 and 0.778.
- **Use:** in Step 1 (Labels). The format of the released benchmark forces file-name labelling,
  and even then the background-heavy classes (BruteForce, Web) score poorly.
- Do NOT claim the official CSV gives "~99%".

## C. Verified citations (D:\EdgeFlow-IDS\paper\refs_candidates.bib; copy the needed entries into refs.bib)

**MUST:**
- **garcia2023labeling** — Garcia & Valeros, "Towards a Better Labeling Process for Network
  Security Datasets", arXiv 2305.01337, preprint.
  - Most datasets assign labels "in files or directory names", and "published datasets sometimes
    contain errors that require significant effort to correct". Use in Related Work/Labels.
  - It also argues that per-IP blocking from flow detections is "prone to errors… a few false
    positives can have strong consequences". Use in Response.
- **pinto2025flowexporter** — Pinto, Vitorino, Maia, Amorim, Praça, "Flow Exporter Impact on
  Intelligent IDS", ICISSP 2025, pp. 289–298, doi 10.5220/0013131900003899. The exporter choice
  changes results. Use in Related Work (exporters).
- **pekar2024integrity** — Pekar & Jozsa, "Evaluating ML-Based Anomaly Detection Across Datasets
  of Varied Integrity: A Case Study", Computer Networks 251:110617 (2024), doi
  10.1016/j.comnet.2024.110617.
  - They map NFStream to CICFlowMeter features and say the reasons for value differences ("how
    flows are updated and terminated") are out of their scope.
  - Our defect diagnosis supplies one such mechanism. Use in Live/defect.
- **akbari2020atmos** — Akbari, Tahoun, Salahuddin, Limam, Boutaba, "ATMoS: Autonomous Threat
  Mitigation in SDN using Reinforcement Learning", NOMS 2020, doi 10.1109/NOMS47738.2020.9110426.
  "IDSs and traffic classifiers are highly prone to false positives; simply dropping the
  traffic… can have severe consequences". Use in Response.

**SHOULD (one clause each, if space allows):**
- **rasheed2026drift** — Rasheed & Alobaedy, IJATEE 2026. Temporal evaluation on CIC-IoT-2023,
  Edge-IIoTset and UNSW-NB15; drift yields "total blindness, sensitivity inflation or stable
  detection". Our BruteForce collapse is a "blindness" case. Use in Splits/Related Work.
- **schraven2026mawiflow** — MAWIFlow, ICISSP 2026: tree classifiers degrade over time.
- **orsdemir2026sok** — SoK: SDN Security with ML, IEEE Access 2026; reviews 50 papers' evaluation
  practice. Supports "few works report false blocks".
- **ali2026unknown** (arXiv 2602.12183) — cross-dataset asymmetry between IoT-23 and CICIoT2023.
  Supports the IoT-23 replication and the threats section.
- **Do NOT use** these unverified claims:
  - Biswas: the cause it gives is feature drift, contrary to what was suggested.
  - Amaral: the "1 FP of 15" figure was not found.
  - Ramkumar on "inconsistent labels": that remark is about IoT-23.

## D. Upstream PR
The NFStream fix plus regression test is submitted as PR nfstream/nfstream#263 (under review).
Add a misc bib entry `nfstream263` (url https://github.com/nfstream/nfstream/pull/263, 2026,
author Muhammad Usama). Write "fix submitted as PR #263", never "merged".

## E. Audit-toolkit framing
- Present the paper's contribution as a **reusable four-check audit** that others can run on
  their own detector and data:
  1. Labels: measure the background share and the cost of file labels.
  2. Splits: time-ordered within captures, per-class F1 with host-pair CIs, boundary-spanning share.
  3. Live: flow-by-flow match, packet accounting, replay rate, delay vs CPU.
  4. Response: false blocks per pair and the k-curve.
- Name the checks once (e.g. a numbered "audit checklist" table or list in the Discussion,
  replacing the current Lessons list rather than adding to it).
- Say that every check is implemented as a script in the repository (src/analysis/*, src/iot23/*)
  and that two datasets were audited with it.
- Small edits to title/abstract wording are allowed (e.g. "an audit"); keep the title unless a
  clearly better short one emerges.
- Update intro contributions:
  - The labels result now holds on two datasets.
  - The toolkit is the reusable artifact.
