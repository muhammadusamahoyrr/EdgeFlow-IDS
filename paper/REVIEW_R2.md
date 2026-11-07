# Reviewer 2 report on draft v1 (summary of required changes)

Scores: TMA weak reject; workshop weak accept → clear accept if M1–M3 are fixed and the paper is refocused.

## Major issues
- **M1. Live = offline is largely expected by construction.** The fix is now done
  (results/live/run1/flow_match.md): a flow-by-flow match. Reframe C3 as a fidelity *check* plus
  the failure modes it exposed (packet loss through the MAC-learning pitfall, quiet meters, the
  exporter defect), not as a finding. Note also that tcpreplay reached only 69–77% of the original
  rate.
- **M2. Statistical rigour.** Single live runs; the flow-level bootstrap ignores clustering.
  - The fix is now done: host-pair bootstrap (results/cluster_ci.md). Live repeats are running.
  - Lead with per-class F1 and support, and macro-F1 over classes with ≥50 test flows (0.814).
- **M3. C1/C2 novelty and evidence.**
  - Add the file-label baseline (done: results/file_label_baseline.md).
  - Cite IoTGeM and Traffic-MoE (done: FACTS revision).
  - "Temporal drift" overclaims: it is a change of attack target/variant within one session, so
    call it that.
  - A temporal split of a trimmed file covers only its first minutes.
- **M4. The NFStream defect is an engineering bug report.**
  - Its research value is methodological: offline evaluation flushes at end of file, so exporter
    timing bugs are invisible to scores.
  - Cut §5.4 to about half a column and move the issue history (#120/#193/#196/#215/PR #227) to a
    footnote.
  - The XSS case is late, not lost.
- **M5. Blocking comparison.**
  - Add k=1 with MITM verdicts ignored and the full k-curve per class (done: run1 block_curve.md).
  - Add time-to-block.
  - The selection criterion is dominated by DDoS flows; say so.
- **M6. Coherence.**
  - Cut NSGA-II, the tree-limit search and the ARP watcher to 1–2 sentences each (drop the NSGA
    figure).
  - Organise the paper around one thesis.
- **M7. Threats to validity.** Add a structured section (internal / construct / external /
  conclusion), about half a column:
  - Same author labels and chooses.
  - Macro-F1 with tiny classes.
  - Single runs.
  - WSL2 timing, with the replayer sharing the CPU.
  - One capture session per class.
  - Trimmed pcaps.

## Presentation
- **Title:** shorter, no "temporal drift". Chosen title: "What Benchmark Scores Hide: Auditing a
  Flow-Based IoT Intrusion Detector from Labels to Live Blocking".
- **Abstract:** state the thesis in the first two sentences: each step from benchmark to gateway
  exposed a problem the previous step hid, and a cheap check catches each one.
- **Intro:** shorter contribution list (1–2 lines each). Three lead contributions:
  1. Evidence-based labels with the measured cost of file-name labels.
  2. A live-fidelity check (per-flow matching, packet accounting, verdict delay under CPU
     budgets) and the exporter defect it exposed.
  3. Response evaluation scored in false blocks, with the full trade-off.
- **C2** becomes supporting evidence: what a random split hides.
- **Target length:** 8 pages IEEE two-column including references.
  - Remove the NSGA figure.
  - Shrink the ARP watcher.
  - Fold the evidence table.
  - Merge the repeated "Lessons" into one Lessons subsection.
- **Overclaims to remove:** "live fidelity" as a general claim (it holds at the tested rates
  only); "loses no flows" (one run, buffer never filled); "the first" (say "to our knowledge,
  previously undiagnosed").
- **Jargon to define or replace:** "ticker" (use "background ping"), "n/r", "edge pick", and one
  consistent term for boundary-spanning connections.
