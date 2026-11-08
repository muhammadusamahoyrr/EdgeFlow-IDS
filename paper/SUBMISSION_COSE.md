# Submission record: Computers & Security (Elsevier)

## Summary

| Item | Value |
|---|---|
| Paper | What Benchmark Scores Hide: Auditing a Flow-Based IoT Intrusion Detector from Labels to Live Blocking |
| Journal | Computers & Security (Elsevier), hybrid journal |
| Manuscript number | **COSE-D-26-07156** |
| Submitted | 8 November 2026, 08:11 PKT (Editorial Manager shows 7 Nov 2026, US time) |
| Article type | Full Length Article |
| File submitted | `paper/main.pdf` (IEEE conference format, 9 pages, built from LaTeX) |
| Authors | Muhammad Usama (corresponding), Ahmad Kamran Malik |
| Corresponding email | muhammadusamahoyrr@gmail.com |
| Publishing option | **Subscription** (no fee). Open access APC is about USD 3,190, so do not choose it. |
| Preprint | SSRN free preprint: **YES** (goes public after desk review passes) |
| Tracking | https://www.editorialmanager.com/COSE/ → Author Login → Submissions Being Processed. The username is in the Elsevier email of 8 Nov 2026. Never write the password here. |

## Why this journal

- The user wanted a zero-cost venue. In hybrid Elsevier journals the subscription route is free.
- The topic (evaluation of ML-based IoT intrusion detection) is core to Computers & Security.
- Fallback if rejected: **Computer Networks** (Elsevier), same subscription route.
- Avoid: IEEE Access and MDPI (APC), IEEE conferences (registration fee), predatory "conferences" that email you.

## What was entered in the submission form

**Title:** What Benchmark Scores Hide: Auditing a Flow-Based IoT Intrusion Detector from Labels to Live Blocking

**Abstract:** plain-text copy of `paper/sections/abstract.tex` (LaTeX symbols replaced: `--` → `–`, `\,s` → ` s`, `\emph{}` removed).

**Keywords:** intrusion detection; Internet of Things; evaluation methodology; dataset labeling; flow export; CIC-IoT2023

**Classifications (5):** Intrusion Detection and Prevention; AI/ML (defensive use of); Evaluation/Standards; Network Security; Embedded Systems

**CRediT roles (suggested; confirm with the supervisor):**
- Muhammad Usama: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Validation, Visualization, Writing – original draft, Writing – review & editing
- Ahmad Kamran Malik: Supervision, Writing – review & editing (plus Conceptualization / Methodology / Resources if he contributed these)

**Co-author details:** Ahmad Kamran Malik, ahmad.kamran@comsats.edu.pk, Department of Computer Science, COMSATS University Islamabad, Pakistan

**Competing interests:** "no competing interests" checkbox (the system generated `Declaration of competing interests.docx` itself)

**Generative AI:** declared "yes". The statement sits in the paper, directly before the references, under the heading Elsevier requires: "Declaration of Generative AI and AI-Assisted Technologies in the Manuscript Preparation Process".

**Research data:** Yes, original data, https://github.com/muhammadusamahoyrr/EdgeFlow-IDS ("EdgeFlow-IDS: code, attacker evidence, results and audit scripts for 'What Benchmark Scores Hide'")

**Funding:** none.

**Editorial Manager profile:** Title "Mr."; personal keywords: intrusion detection, Internet of Things security, machine learning for security, network security, flow-based traffic analysis, evaluation methodology.

**MaRS reference check:** showed "Reference Checking could not be completed due to an error" for main.pdf and the declaration .docx. This is a tool limitation with LaTeX PDFs, not a problem with the paper, so no action is needed. References were checked earlier (`CITATION_CHECK_FINAL.md`, `check_refs.py`).

## Layout changes made just before submission (8 Nov 2026)

Backup of the state before these changes: `paper/backup_r22/` (plus `backup_r22/intro_before_move.tex`).

1. **Figures** (`src/make_figures.py`): Times-like serif font at 8 pt, thinner lines and markers, so Fig. 1 (`gap_units`) and Fig. 2 (`late_blocks`) match the tables. Only these two figures were regenerated.
2. **Table I** (`sections/intro.tex`): the "4 Response" cell was shortened. The removed details are in Section VII. The table moved after the first intro paragraph so it floats to page 1.
3. **Float spacing** (`main.tex`): `\textfloatsep` 10pt, `\floatsep` 8pt, `\dbltextfloatsep` 10pt.
4. **`\raggedbottom`** (`main.tex`): removes stretched gaps between paragraphs.
5. **Tables:** `booktabs` rules (`\toprule`, `\midrule`, `\bottomrule`) with `\cmidrule` under spanning headers. The Table IV header column that had no label is now labeled "value". There is no bold inside tables; the user asked for that, because bold broke the layout.
6. **Title gap:** `\IEEEaftertitletext{\vspace{-1.5\baselineskip}}`.
7. **Bold section headings:** `\section` redefined with `\bfseries`.
8. **Acknowledgment** replaced by Elsevier's AI declaration section.

Note: items 3, 4, 6 and 7 modify the IEEE template. If the paper goes back to an IEEE venue, check that venue's rules.

## Still to do

- [ ] Commit today's paper changes to git (not done yet).
- [x] Check that the GitHub repo is **public** and that the tag `v1.0-paper` (cited in the paper) exists. Both confirmed on 8 Nov 2026 via the GitHub API. Note: the tag predates the two figures' code (`gap_units`, restyled `late_blocks`); at revision, cite a new tag that includes them.
- [ ] Do **not** submit this paper anywhere else (e.g. NOMS 2027, deadline 9 Nov 2026) while it is under review at Computers & Security: that is a dual submission. The SSRN preprint is allowed.
- [ ] Forward the confirmation email to Ahmad Kamran Malik.
- [ ] Check the status weekly in Editorial Manager.

## What happens next

1. **Submitted to Journal** → **With Editor** (desk review, about 1–3 weeks) → **Under Review** → **Required Reviews Completed** → **Decision in Process**.
2. After desk review passes, the SSRN preprint goes public and gives a DOI link. Use it for the CV and LinkedIn.
3. At revision: upload the LaTeX source; probably convert to the Elsevier template (elsarticle); answer each reviewer comment in a response letter.
4. At acceptance: choose **Subscription** again (final publishing decision).
5. If rejected: submit to Computer Networks (Elsevier) the same way.

CV entry until the paper is published:
> M. Usama and A. K. Malik, "What Benchmark Scores Hide: Auditing a Flow-Based IoT Intrusion Detector from Labels to Live Blocking," submitted to *Computers & Security*, 2026.
