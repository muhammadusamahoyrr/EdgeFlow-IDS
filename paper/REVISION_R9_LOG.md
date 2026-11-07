# Round 9 (review 6): small edits, done directly

Backup: paper\backup_r8\ (sections, main.tex, refs.bib; refs_before_trim.bib).

## Garcia & Valeros (arXiv 2305.01337v1), checked against the PDF page images
The PDF numbers sections in Arabic (2.2, 3.2, 6.3); the arXiv HTML renders them in Roman.

| Location | Verbatim text |
|---|---|
| Abstract, p.1 | "...resulting in most analyzed datasets assigning labels in files or directory names." |
| Sec. 2.2, p.2 | "published datasets sometimes contain errors that require significant effort to correct" |
| Sec. 3.2, p.4 | "If the same label is used for the whole PCAP file, then machine learning models may learn to detect operating system benign traffic as malicious." |
| Sec. 6.3, p.8 | "The main reason is that a few false positives can have strong consequences for an organization." |
| Sec. 6.4, p.8 | "A method that can alert about an IP address after 10 detections would be better than a method that needs 20 detections. However, this should always be balanced with the detection performance (e.g., FPR)..." |

- Table 1 lists CTU IOT-23 as style B (in flows). CIC-IoT2023 is not among the 36 datasets.
- "Thought experiment" was not found on the pages read (p.4, p.8), so it is not used.

## Edits
- **labels.tex:** cite Sec. 3.2. Its prediction is what we measure on the two datasets.
- **response.tex:** Sec. 6.3–6.4 cited: earlier alerts help only at a controlled FPR.
- **splits.tex:**
  - "both coarse" was added for the attacker and capture units.
  - "probably positive" became "Its sign is thus likely positive but not established under coarser clustering".
- **discussion.tex:**
  - Construct now reads "cluster intervals, with their sensitivity to the cluster unit".
  - The conclusion recap was shortened, since it repeated the abstract.
- **refs.bib:**
  - Dropped arXiv notes on entries that are now published, and dropped the publisher fields for USENIX/SciTePress/Springer, the LNCS series and the Efron reprint note.
  - No author, title, venue, year, pages or DOI was changed.

## Result
- 8 pages.
- No undefined references, no overfull boxes, no bare %.
- check_refs: no missing, unused or TODO entries.
