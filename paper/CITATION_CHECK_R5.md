# Citation check, round 5 (reviewer points)

Date: 2026-11-02. Only primary sources were used: arXiv PDFs and abstract pages, the publisher page or DOI landing page, Crossref metadata, the MMU eprints record, the dataset pages and the GitHub API. No paper file was edited.

Reference numbering comes from `main.bbl` in citation order: [1] sommer, [2] arp, [3] apruzzese, [4] tang, [5] engelen, [6] liu, [7] flood, [8] pendlebury, **[9] pinto2025flowexporter**, [10] vitorino, [11] aouini, [12] neto, [13] garcia2020iot23, [14] nfstream262, [15] nfstream263, [16] garcia2023labeling, [17] ramkumar, [18] kostas, **[19] schraven2026mawiflow**, [20] zhou, [21] bridge, **[22] rasheed2026drift**, **[23] ali2026siamxbert**, [24] realguard, [25] lantz, [26] pfaff, [27] hofstede, [28] pinto2025hera, [29] nfstream120, [30] bawany, [31] yan, [32] arpwatch, **[33] orsdemir2026sok**, [34] pedregosa, [35] deb, [36] blank, [37] efron, [38] pekar, [39] akbari.

---

## 1. Exact quotes

### 1a. Rasheed & Alobaedy [22] (related.tex l.5): **WRONG**
- Paper: drift yields ``total blindness, sensitivity inflation or stable detection''
- Source (abstract, publisher page accentsjournals.org paperinfo 1938 and MMU eprints 16573, identical): "The results show that concept drift doesn't lead to a consistent decrease in performance. In contrast, it results in specific behaviour changes, such as total blindness, sensitivity inflation and relatively stable detection."
- The paper changes "and relatively stable" to "or stable", so it is not an exact quote.
- Exact quote option: `Rasheed and Alobaedy find that drift causes no consistent decrease in performance but ``specific behaviour changes, such as total blindness, sensitivity inflation and relatively stable detection''~\cite{rasheed2026drift}.`
- Paraphrase option (no quote marks): `Rasheed and Alobaedy find that drift does not degrade performance uniformly but produces distinct behaviours, from total blindness to sensitivity inflation to relatively stable detection~\cite{rasheed2026drift}.`
- splits.tex l.35 uses the single word ``blindness'', which does appear in the source. It is fine.

### 1b. Pekar & Jozsa [38] (live.tex l.59): **WRONG** (the phrase is not in the source)
- Paper: ``how flows are updated and terminated''
- Source (arXiv 2401.16843v2, the accepted version; Sec. 7.2 "Feature Selection", PDF p.10): "It is worth to note that, even for features that appear similar, discrepancies in their calculated values may occur, as also evident in Tables 2 to 4. These differences can arise due to variations in how the features are computed and the specific mechanisms employed for updating and terminating flows. Understanding the reasons behind these discrepancies is not within the scope of our current work."
- The NFStream-to-CICFlowMeter mapping is confirmed: Table 5, "Flow feature mapping between NFStream and CICFlowMeter".
- Exact quote option: `... and leave the causes of value differences, such as ``the specific mechanisms employed for updating and terminating flows'', out of scope~\cite{pekar2024integrity}`
- Paraphrase option (no quote marks): `... and note that value differences may stem from how features are computed and how flows are updated and terminated, leaving the reasons out of scope~\cite{pekar2024integrity}`

### 1c. Garcia & Valeros [16] (related.tex l.3, arXiv 2305.01337v1): **CONFIRMED** (both quotes are verbatim), with one caveat
- ``in files or directory names'': Abstract, p.1: "There is no labeling ontology nor tools to help assign the labels, resulting in most analyzed datasets assigning labels in files or directory names."
  - Caveat: the source says "most *analyzed* datasets". Its own body tally (Sec. 2.2, Table 1) counts 11 of 36 datasets in flows, 9 in directory names, 7 in metadata, 5 in file names and 4 with no labels. That is only 14 of 36 in file or directory names. The paper's "most datasets" repeats the abstract's own claim, so it is attributable, but the safer wording is "most of the datasets they analysed".
  - Suggested wording: `Garcia and Valeros report that most of the datasets they analysed assign labels ``in files or directory names'' ...`
- ``sometimes contain errors that require significant effort to correct'': Sec. 2.2 "Network security datasets and labels", p.2: "In addition, published datasets sometimes contain errors that require significant effort to correct [33]." The quote is verbatim. Garcia and Valeros are themselves citing their ref. [33] here, so the paper could add "citing prior work". This is optional.

## 2. Garcia & Valeros on false positives and blocking: **CONFIRMED** (the passage exists, so the citation can stay)
- Sec. 6.3 "Blocking", p.8: "The third perspective is about the transition from IP address detections to IP blocking. Blocking is a critical action when traffic is stopped to or from the alerted IP address. This decision is important and prone to errors and few real-life systems implement it automatically, leaving the decision to humans. The main reason is that a few false positives can have strong consequences for an organization."
- Nuance: Garcia and Valeros write about IP-address detections leading to IP blocking, not flow detections. The source has "strong", not "severe".

## 3. Akbari et al., ATMoS, NOMS 2020 [39]: **CONFIRMED**
- Source: the author PDF (rboutaba.cs.uwaterloo.ca/Papers/Conferences/2020/AkbariNOMS20.pdf), Sec. II "Related Work", p.2: "Intrusion detection systems and traffic classifiers are highly prone to false positives. Thus, simply dropping the traffic that is suspected to be malicious can have severe consequences for the availability and functionality of the network."
- Supporting passage in Sec. III: "Even with proper rules, IDSs are highly prone to false positives. This makes it hard for a traditional mitigation system to impose restrictions on a host that is deemed suspicious, solely based on the IDS alerts."
- Akbari et al. do not say "a few" false positives.
- Bibliographic entry: Crossref confirms the title, the five authors, "NOMS 2020 - 2020 IEEE/IFIP Network Operations and Management Symposium", pp. 1-9, 2020, and DOI 10.1109/NOMS47738.2020.9110426. **CONFIRMED.**
- Suggested Response sentence (response.tex l.3): `Garcia and Valeros note that a few false positives can have strong consequences once detections drive IP blocking~\cite{garcia2023labeling}, and Akbari et al.\ that, because detectors are prone to false positives, simply dropping suspected traffic can have severe consequences for the network~\cite{akbari2020atmos}.`

## 4. References [9], [19], [22], [23], [33]
| # | key | Verdict | Primary-source facts |
|---|---|---|---|
| [9] | pinto2025flowexporter | **CONFIRMED** | Crossref 10.5220/0013131900003899: "Flow Exporter Impact on Intelligent Intrusion Detection Systems"; Pinto, Vitorino, Maia, Amorim, Praça; Proc. 11th ICISSP; pp. 289-298; 2025. arXiv 2412.14021 comment: "ICISSP 2025 conference". The bib's "Volume 2" was not visible in Crossref, so it is unchecked but plausible. |
| [19] | schraven2026mawiflow | **CONFIRMED** | Crossref 10.5220/0014463900004061 (the arXiv page also links this DOI): title as in the bib; Schraven, Windmann, Niggemann; Proc. 12th ICISSP; pp. 549-556; 2026. |
| [22] | rasheed2026drift | **CONFIRMED** (bibliographic entry; the quote is wrong, see 1a) | Publisher page and DOI 10.19101/IJATEE.2026.131340379: "Behavioral instability in anomaly-based intrusion detection systems under concept drift: from blindness to sensitivity inflation"; Mohammad M. Rasheed, Mustafa Muwafak Alobaedy; IJATEE 13(140):275-302, July 2026. |
| [23] | ali2026siamxbert | **CONFIRMED** (current title) | arXiv 2602.12183: v1 (12 Feb 2026) was titled "Unknown Attack Detection in IoT Networks using Large Language Models: A Robust, Data-efficient Approach", which is likely the title the reviewer saw. v2 (29 Oct 2026) is titled "Data-Efficient Unknown Attack Detection in IoT Networks Using Pretrained Language Models", matching the bib, which already pins "v2". Authors: Shan Ali, Feifei Niu, Paria Shirani, Lionel C. Briand. It is a preprint with no venue; Crossref has no published version. The cross-dataset "asymmetry" wording appears in the v2 text. |
| [33] | orsdemir2026sok | **CONFIRMED** | Crossref 10.1109/ACCESS.2026.3673172: "SoK: Software-Defined Networks Security With Machine Learning"; IEEE Access vol. 14, pp. 40769-40787, 2026; authors Örsdemir, Tefek, Esiner, Küpçü. Crossref shows dotless-ı spellings; the bib spelling is the usual form. |

## 5. Tang et al. [4], recall 0.0095 (intro.tex l.3): **CONFIRMED number; wording should be tightened**
- Source: arXiv 2609.24393v1, **Table VII "Labeled three-branch comparison on a common PCAP"**. Row ML (the RF-21 random forest): TP 1, FP 0, FN 104, TN 433, Precision 1.0000, **Recall .0095**, F1 .0189, FPR .0000. Row AND (strict Hybrid correlated branch): the same values, Recall .0095.
- This is the recall of the attack (positive) class in a binary evaluation on one labelled laboratory PCAP.
- Abstract: "RF-21 and the strict correlated branch achieved recall of only 0.0095" on "a labeled laboratory PCAP".
- Benchmark F1 0.97: Table IV gives RF-21 F1 = 0.970148 (RF-41 F1 = 0.971360) on the leakage-controlled hold-out set. This is consistent.
- Caveat: "in deployment" is looser than the source, which says "operational validation" on a labelled laboratory PCAP.
- Suggested wording: `... a random forest with hold-out F1 0.97 whose attack recall fell to 0.0095 on a labelled laboratory capture during operational validation~\cite{tang2026hybrid}.`
- Bib: the arXiv comment reads "Accepted for publication in the Proceedings of the 29th National Conference on Selected Issues of Information and Communication Technology (VNICT 2026), Hanoi, Vietnam, November 7-8, 2026". The authors and title match. **CONFIRMED.**

## 6. IoT-23 benign captures (setup.tex l.5): **WRONG (imprecise)**
- Zenodo 10.5281/zenodo.4743746 says the dataset "has 20 malware captures executed in IoT devices, and 3 captures for benign IoT devices traffic."
- stratosphereips.org/datasets-iot23 says "the benign scenarios was obtained by capturing the network traffic of three different IoT devices: a Philips HUE smart LED lamp, an Amazon Echo home intelligent personal assistant and a Somfy smart doorlock ... these three IoT devices are real hardware and not simulated". It also says the scenarios were "created by capturing network traffic data of not infected real IoT devices".
- The same page's capture list is: CTU-Honeypot-Capture-4-1 (Philips HUE), CTU-Honeypot-Capture-5-1 (Amazon Echo), CTU-Honeypot-Capture-7-1 (Somfy Doorlock).
- The capture READMEs say: 4-1 is the "honeypot device Philips hue Bridge" (originally "CTU-Honeypot-Bridge-Philips-Hue-1-2018-10-25"); 5-1 is "Device: Amazon Echo Dot"; 7-1 has six sub-captures, Somfy-01 to Somfy-06.
- The project's `src/iot23/download.py` uses only `CTU-Honeypot-Capture-7-1/Somfy-01` from 7-1.
- So "honeypot" is only the directory name. The dataset describes these as benign traffic of real, uninfected IoT devices.
- Suggested wording: `... and three benign captures of real, uninfected IoT devices: a Philips Hue bridge, an Amazon Echo and a Somfy smart door lock (CTU-Honeypot-Capture-4-1, 5-1 and the Somfy-01 part of 7-1).`
- Bib [13]: the Zenodo record gives authors Garcia, Parmisano and Erquiaga, publication date 2020-01-20, version 1.0.0, and the same title. **CONFIRMED.** The record was created on Zenodo in May 2021, but 2020 is its stated publication date.

## 7. CIC-IoT2023 CSV releases (labels.tex l.61): **CONFIRMED in substance; wording should name the folder and the source mirror**
- The CICIoT2023 distribution's `CSV/README.pdf` (part of the dataset, by Neto et al.) says: "This folder shows two sub-folders, MERGED_CSV and CSV folders. The CSV subfolder contains the .csv files for each of the corresponding .pcap file ... The MERGED_CSV folder contains the same exact data as within each of the attack folders under CSV subfolder, except they have been merged, shuffled and split into multiple files for easy loading into machine learning scripts. The files also have labels (feature named 'Label') attached to each data point".
- The UNB page (unb.ca/cic/datasets/iotdataset-2023.html) lists the top-level PCAP/CSV/Example/Supplementary directories only.
- Verified headers:
  - The per-pcap file `CSV/CSV/Benign_Final/BenignTraffic3.pcap.csv`, as downloaded by `src/analysis/download_official_csv.py`, has 39 columns from `Header_Length` to `Variance`, with **no Label, IP or timestamp column**.
  - `CSV/MERGED_CSV/Merged01.csv` (63 files) has the same 39 columns **plus `Label`**, for example `DDOS-PSHACK_FLOOD`.
- Caveat: the files were fetched from the Hugging Face mirror `bencorn/CIC-IoT-2023`, not directly from UNB. The mirror's folder layout matches the official README.pdf, but I could not check it byte-for-byte against the UNB download, which requires a form. That part is **UNVERIFIABLE**. "Official" should therefore be qualified, or the mirror named.
- Suggested wording: `The per-pcap CSV files of the CIC-IoT2023 release (folder \texttt{CSV/CSV}, one file per pcap; 483,053 rows for our ten captures, obtained from a public mirror of the UNB distribution) hold 39 packet-window features and no addresses, timestamps or label column; the label is the file name. The release's \texttt{MERGED\_CSV} files do carry a \texttt{Label} column, but they are merged and shuffled across captures, so they cannot be traced back to a capture or relabelled from evidence either.`
- The last clause is an inference from README.pdf ("merged, shuffled and split"); the paper can drop it if it prefers.

## 8. Other bib entries (problems flagged only where confirmed)
- **[15] nfstream263, title WRONG.** The bib title is "Fix for issue #262: refresh the LRU position of updated flows in NFCache". The GitHub API gives the actual PR title: "Keep LRU order on flow update so idle flows expire on time (#262)" (opened 2026-11-02, open).
- **[18] kostas2024iotgem, outdated.** It has been published: Computer Networks vol. 270, article 111550, Oct. 2025, DOI 10.1016/j.comnet.2025.111550 (Crossref; the arXiv page links this DOI). It should cite the journal version, with year 2025. The current entry says "arXiv ..., 2023".
- **[10] vitorino2025revisiting, outdated.** It has been published: "Revisiting Network Traffic Analysis: Compatible Network Flows for ML Models", Foundations and Practice of Security (FPS 2025), LNCS, pp. 150-166, 2026, DOI 10.1007/978-3-032-20026-6_9 (Crossref; same five authors).
- **[17] ramkumar2024diagnosing, outdated.** It has been published: IEEE Transactions on Software Engineering vol. 51, no. 11, pp. 3117-3137, Nov. 2025, DOI 10.1109/TSE.2025.3610540 (Crossref; same six authors).
- **[28] pinto2025hera, outdated.** It has been published: 2024 IEEE 23rd Int. Conf. on Trust, Security and Privacy in Computing and Communications (TrustCom), pp. 1850-1856, 2024, DOI 10.1109/TrustCom63139.2024.00255 (Crossref; same four authors).
- [21] bridge2026tchnet has an SSRN record (10.2139/ssrn.6590314) but no journal version. The arXiv entry is fine.
- [20] zhou2026trafficmoe has no published version on Crossref; arXiv v2 is dated 8 Jul 2026. Fine.
- **CONFIRMED against Crossref or the DOI** (title, venue, volume, pages, year): [1] sommer (SP 2010, 305-316), [3] apruzzese (EuroS&P 2023, 592-614), [5] engelen (SPW 2021, 7-12), [6] liu (CNS 2022, 254-262), [7] flood (EuroS&P 2024, 658-675), [11] aouini (Comput. Netw. 204, 108719, 2022), [12] neto (Sensors 23(13) 5941, 2023), [24] realguard (Sensors 22(2) 432, 2022), [25] lantz (HotNets-IX 2010, 1-6), [27] hofstede (COMST 16(4) 2037-2064, 2014), [30] bawany (AJSE 42(2) 425-441, 2017), [31] yan (COMST 18(1) 602-622, 2016), [35] deb (TEVC 6(2) 182-197, 2002), [36] blank (IEEE Access 8, 89497-89509, 2020), [38] pekar (Comput. Netw. 251, 110617, 2024).
- [14] nfstream262 is **CONFIRMED**: same title, opened 2026-11-01 by muhammadusamahoyrr. [29] nfstream120 is **CONFIRMED**: same title, opened 2022-04-20. [32] the arpwatch URL resolves (HTTP 200).
- **UNVERIFIABLE online in this pass** (no DOI in the bib, and dblp was unreachable): [2] arp (USENIX Sec 22, 3971-3988), [8] pendlebury (USENIX Sec 19, 729-746), [26] pfaff (NSDI 15, 117-130), [34] pedregosa (JMLR 12, 2825-2830), [37] efron. No error is apparent; the values match the commonly cited records.

## Summary of required fixes
1. related.tex: correct the Rasheed quote (1a).
2. live.tex: replace the invented Pekar quote with the exact phrase or a paraphrase (1b).
3. related.tex: optionally change "most datasets" to "most of the datasets they analysed" (1c).
4. response.tex: keep both citations, but use each source's own wording, since Garcia & Valeros talk about IP blocking (2, 3).
5. intro.tex: change "in deployment" to "operational validation on a labelled laboratory capture" (5).
6. setup.tex: change "honeypot captures" to benign captures of real, uninfected Philips Hue, Amazon Echo and Somfy devices, noting that only Somfy-01 of 7-1 is used (6).
7. labels.tex: name the `CSV/CSV` per-pcap folder versus the labelled `MERGED_CSV` files, and qualify "official", since the files came from a mirror (7).
8. refs.bib: fix the PR #263 title; update [10], [17], [18] and [28] to their published versions (8).
