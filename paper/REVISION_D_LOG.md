# Revision D log: final-review plan section D (new experiments)

Backup: `paper\backup_r10\` (sections\, main.tex, refs.bib), taken before any edit.

**Result**
- 8 pages including references. Abstract 250 words (same counter as before).
- No undefined references or citations, no overfull boxes, no bare `%`.
- check_refs.py: 47 cited, 47 in bib.
- No font, margin or `\vspace` changes. One table removed (old Table VIII, enforced blocking); its numbers are now in the text.

## D1 (M7): CPU budget without the confounds

**New experiment.** `src/run_pinned.sh`: 9 live runs on 3 Nov 2026 (`results/live/pin_{none,q100,q50}_r{1,2,3}`).
- Same final harness, same three windows (DDoS-SYN, Mirai, DoS-HTTP), budgets interleaved.
- tcpreplay on core 0, keep-alive ping on core 1, gateway on cores 2–5. New option `--pin` in `topology/live_experiment.py`.

**Analysis.** `src/analysis/cpu_factorial.py` → `results/final/cpu_factorial.md`.
- DDoS-SYN delay with no limit is 17.5–18.6 s, with one core 22.3–37.5 s, with half a core 38.8–89.1 s. Kruskal–Wallis H = 7.26, p = 0.027.
- OLS on the pinned runs: half core +43.04 s (s.e. 7.50); one core +16.15 s (7.66); −14.56 s per +1,000 pps (3.82). The unpinned runs gave half core +60.23 s.
- In the DoS-HTTP and Mirai windows the budgets differ by ≤ 0.1 s.
- **Pinning did not stabilise the replay rate** (11,848–14,189 pps). pin_q50_r3 ran at 68% of the original rate: live/offline flows 1.0885, same packets 0.912.
- Catch-up wait after the gap was up to 174.1 s with half a core. Zero kernel drops in all runs. Peak RSS ≤ 1,038.6 MB.

**Fidelity re-run.** `final_fidelity.py` was re-run so that `fidelity_all_runs.md` now includes the 9 pinned runs.
- Pinned runs: match rate 1.0000, same verdict ≥ 0.9998. So "sixteen runs without enforcement" is sourced.
- All earlier rows are unchanged (diff checked). Only the pooled correlation line changed, and the paper does not cite it.

**Paper**
- Live: the "CPU budget" paragraph was rewritten as "CPU budget, without the confounds".
- Fig. live_delay was removed. It showed the confounded runs, and this also settles the stale "1/2 core" legend issue.
- Threats: the "tcpreplay shares the CPU" caveat was removed from External. Statistical now reads "each pinned CPU budget three times".

## D3 (M5): persistent verdict counters

**Analysis.** `src/analysis/persistent_counters.py` → `results/final/persistent_counters.md`.
- Deployed tree on the offline temporal test period, per capture.
- Exposure 354.8 min (5.9 h). 55 attacker pairs, 3,410 benign-only pairs.
- Horizons: reset every 60 s, sliding 60/300/900 s, persistent.

**Findings (MITM-ARP verdicts ignored)**
- **Mirai:** persistent counters block 1/6 at k = 3 and 0/6 from k = 5. Only 10 Mirai-labelled test flows on 6 pairs (label_audit.md population), so the miss belongs to the detector.
- **Web:** at k = 5, persistent 7/8 vs reset 3/8. At k = 10, 2/8 vs 1/8. This miss belongs to the harness.
- **False blocks:** at k = 5, 1 → 7 (0.2 → 1.2/h); at k = 3, 3 → 22.

**Paper.** New Response paragraph "Persistent counters". Construct threat updated. Conclusion's future work now reads "a blocking criterion that weighs attack volume".

## D2 (M8): blind label audit

**Analysis.** `src/analysis/label_audit.py` → `results/final/label_audit.md`, `label_audit_sample.csv` (blind) and `label_audit_key.csv`.
- **Protocol.** 47 strata × up to 30 flows = 975 flows, seed 0. The rater is a fixed program: it sees packets, scenario and label-free context, never the label, the attacker list or the prediction.
- **Pre-registered rater.** 91 disagreements. 67 of them were rater defects: 57 RTSP, 6 DoS-HTTP mid-connection pieces, 4 Mirai truncated payloads.
- **Amendments R1–R4** (listed in the script and in the .md; both verdicts reported):
  - R1: payload truncation bug;
  - R2: request direction bug;
  - R3: RTSP route dictionary, the only criterion change and post-hoc;
  - R4: a response-only fragment is rated undetermined.
- **Amended rater.** Decides 630 of 975.
  - Attack labels: 2/265 wrong (0.8%, Wilson [0.2, 2.7]%). Both are UPnP `GET /description.xml` from .178 to .154, a non-victim.
  - Benign labels: 22/365 wrong, all `.66 → .174:80` HTTP flood. .174 is not in the victim list.
- **FN direction.** The 537 BruteForce FNs are attack (RTSP), the 21 MITM FNs are consistent, and the 2 SQLi FNs are label errors where the model was right.
- **Macro-F1 without MITM-ARP:** 0.8259 (dropped from the average), 0.8260 (flows removed too); 0.7249 with all classes.

**Corrections.** `src/analysis/label_corrections.py` → `results/final/label_corrections.md`. attackers.json and flows.parquet are NOT changed.
- C1: 2,269 flows .66 → .174:80 relabelled DoS-HTTP. All are in the temporal test period; .186:80 (10 flows) fails the flood criterion.
- C2: 2 Web flows relabelled Benign.
- Sanity check: the old labels reproduce 0.7249 / 0.8669 and BruteForce 78%.
- Corrected: temporal 0.7294 (DoS-HTTP F1 0.919 → 0.946), random 0.8744, gap +0.1420 → +0.1450, BruteForce share 75%.

**Paper**
- Labels: "A label error found by the model" became "Label audit".
- Splits: the RTSP traffic is described as a stream-path dictionary: "change of target and method".
- Abstract: "when the attack moves from SSH passwords to RTSP stream paths".
- Threats: Internal (audit, rater is a program, amendments) and Construct (0.826).

## Cuts made for space (no numbers lost that are not in a results file)
- Live:
  - run-1 per-window match ranges (96.62–100%, 97.63–100%);
  - "packet accounting" and "delay" merged into one paragraph;
  - the one-core Mirai explanation;
  - the shortened Pekar & Jozsa quote.
- Response:
  - Garcia and Valeros / Akbari motivation condensed to one cited sentence;
  - window shares 12.5% / 6.8% and "14 outside the MITM window";
  - the per-hour extrapolation caveat (it stays in Threats);
  - packet shares 0.503 / 0.342 / 0.707 / 0.698 summarised as 34–71%.
- Response: Table VIII removed. The text gives 79 blocked, 19/26, 326,268 dropped; 9 blocked, 163,546 dropped (blocking_rates.md / Table source as before).
- Labels: "the released format forces file-name labels".

## Not done / open
- The audit rater is a program. A human spot check of `label_audit_sample.csv` (blind, no labels) would make the M8 answer stronger.
- R3 is a post-hoc criterion; the paper says so.
- Table VI (repeats) still lists only the unpinned runs; the pinned runs are summarised in text. A table of the pinned runs would need space we do not have.
- `src/run_pinned.sh`, the four new analysis scripts and the `--pin` harness option are untracked, like the other files of section C (git not touched).
