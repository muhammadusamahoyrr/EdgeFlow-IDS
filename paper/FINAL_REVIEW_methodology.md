# Methodology and Statistics Review

**Paper:** "What Benchmark Scores Hide: Auditing a Flow-Based IoT Intrusion Detector from Labels to Live Blocking"
**Reviewer angle:** experimental design, statistics and whether the evidence supports the claims. Writing, novelty and related work are out of scope.
**Material checked:** `main.tex`, `sections/*.tex`, `results/*.md`, `results/iot23/*.md`, `results/live/perclass_counts.md`, `src/tune_block_policy.py`, `src/analysis/file_label_baseline.py`.

## Summary

1. The paper audits one decision tree on 54 NFStream features across four steps (labels, splits, live replay gateway, blocking). It uses CIC-IoT2023 throughout and repeats the label and split steps on IoT-23.
2. The statistics are unusually careful for this venue: cluster bootstraps, paired differences, a sensitivity analysis over cluster units, an honest null replication on IoT-23 and a flow-by-flow live/offline match.
3. Several headline numbers do not measure what the text says they measure:
   - the file-label FPRs are largely tautological;
   - the CIC split gap is about 80% one class from three host pairs;
   - the blocking policy was in effect chosen by the upper end of the grid;
   - the k trade-off is set by the 60 s per-window counter reset;
   - the live "stability" is shown with a metric that cannot detect the flow-splitting the runs actually show.

## Scores

- **TMA (full paper): 2/5, weak reject.** The measurement work is sound, but the main quantitative claims (abstract: 71.8%, 97–100%, 60/1,674 = 3.6%, "requiring 10 verdicts ... missed the Mirai and web attackers") need to be re-scoped or re-measured before they can carry a full paper.
- **IEEE workshop on ML for networking security: 3/5, weak accept.** It is acceptable if M1–M4 are fixed in the text. Most fixes need only re-analysis of data the authors already have.

---

## MAJOR issues

### M1. The file-label FPRs are largely tautological. They measure capture memorisation, not that "benign traffic is learned as malicious"

**Location:** Abstract ("flags 71.8% of benign flows"; "flags 97–100% of background flows in every malware capture"); Sec. Labels, "The cost of file-name labels" and "Robustness test on IoT-23"; Table `tab:filelabel`; Intro, contribution 1.

**Problem:**
- The temporal split takes the first 70% of *each capture*. Under file labels, the background flows in the first 70% of, say, the Recon capture are labelled Recon. The model is then tested on the background flows of the last 30% of the *same capture*, recorded on the same devices.
- Predicting "Recon" for them is the model doing exactly what it was trained to do. The stratified split makes this even more direct.
- On CIC-IoT2023, the 52,993 temporal Benign test flows are about 26% Benign-capture flows (~13.9k) and about 74% attack-capture background (~39k). The model flags 38,034, which is almost exactly the attack-capture background. So the 71.8% is very likely "attack-capture background was called by its capture's name", with a low FPR on the Benign capture itself.
- `results/file_label_baseline.md` and `src/analysis/file_label_baseline.py` have no per-capture breakdown, so the reader cannot check this.
- On IoT-23 the per-capture table (`results/iot23/fpr_per_capture.md`) shows the same thing explicitly:
  - FPR 0.97–1.00 in malware captures, whose own background was trained as the attack class;
  - 0.046 on the three benign-device captures. That is the only out-of-capture benign traffic, against 0.0015 for the Zeek-label model.
- The Garcia & Valeros prediction the paper cites ("may learn to detect operating system benign traffic as malicious") is a claim about *generalisation* to benign traffic in general. It is tested only by the benign-capture numbers, which the abstract does not report.

**Why it matters:**
- "97–100% in every malware capture" is close to a definitional outcome of the protocol (train and test on the same capture under a label that calls the whole capture malicious). It is presented as the headline robustness result.
- The "true macro-F1 0.396 vs 0.725" comparison is also partly by construction. The second model was trained on the very labels used for scoring.

**Concrete fix:**
- (a) Split every Benign FPR in Table `tab:filelabel` into (i) Benign-capture flows and (ii) attack-capture background, on both datasets.
- (b) Lead the abstract with the out-of-capture number: IoT-23 honeypots 4.6% vs 0.15%, plus the CIC Benign-capture FPR.
- (c) Add a leave-one-capture-out evaluation of the file-label model, in which the background traffic of a held-out capture was never seen under any label. Only this design tests the generalisation claim.
- (d) Reword "true macro-F1" as "macro-F1 against evidence labels". The comparison is asymmetric by construction, and this should be stated.

**Fixable without new experiments?**
- (a), (b) and (d): yes. These are re-scoring of existing predictions.
- (c): needs retraining (minutes of CPU), but no new data or testbed runs.

### M2. The CIC-IoT2023 split gap is about 80% one class from three host pairs, and the "≥50 test flows" filter is on the wrong unit

**Location:** Sec. Splits, "What a random split hides"; Table `tab:perclass`; Abstract ("a random split hides that brute-force recall falls...").

**Problem:**
- From Table `tab:perclass`, the per-class F1 gaps (random minus temporal) are:
  - Benign 0.02, BruteForce 0.89, DoS-HTTP 0.07, MITM-ARP 0.09, Mirai 0.05, Web −0.02.
  - The sum is 1.10, i.e. 0.1375 macro-F1 points over 8 classes.
- BruteForce contributes 0.89/1.10 ≈ 81% of the gap. Without it, the gap is about 0.21/7 ≈ 0.03 — inside the range that the random-split seed spread and the MITM-ARP noise produce.
- BruteForce has **3 host pairs** in the temporal test set (`results/round2_checks.md`; recall CI [0.000, 0.842]).
- The robustness filter "macro-F1 over classes with at least 50 test flows is 0.814" keeps BruteForce (605 flows, 3 pairs) and drops Mirai (10 flows, 6 pairs). A flow-count threshold is the wrong unit in a paper whose whole argument is that host pairs, not flows, are the independent unit.
- The text says "rests mainly on the brute-force host pairs" but never gives this decomposition. As a result, the paired CI [0.024, 0.278] reads as evidence about splits in general. It is really evidence about one capture's change of target.

**Why it matters:** The reusable claim (Check 2: "random splits hide...") is supported on CIC-IoT2023 by n = 1 capture and 3 pairs, and it does not replicate on IoT-23. The paired-bootstrap machinery then gives false precision about a single event.

**Concrete fix:**
- Report the per-class decomposition of the gap.
- Report the paired difference with BruteForce excluded, and a macro-F1 restricted by **host-pair** support (e.g. ≥5 pairs in both test sets).
- State in the abstract that the CIC gap is essentially the BruteForce target change.
- Re-scope Check 2 as "per-class temporal recall with pair counts" rather than "temporal–random macro-F1 gap".

**Fixable without new experiments?** Yes. This is re-analysis of existing predictions.

### M3. The percentile cluster bootstrap with the zero convention is biased, and the paper's interpretation of the coarse-cluster intervals is not supported

**Location:** Sec. Setup, "Metrics"; Sec. Splits, first paragraph ("barely excludes zero ([0.002, 0.165], [0.001, 0.151])"); Sec. Discussion, Threats, "Conclusion".

**Problem:**
- Macro-F1 under the "absent class has F1 = 0" convention is strongly non-linear under cluster resampling. With host-pair clusters, 39.9% of temporal resamples already miss a class. With attacker-host clusters it is 83%, and with capture clusters 97% (`results/cluster_sensitivity_cic.md`).
- The percentile intervals are therefore mostly a distribution of *which classes are missing*, not sampling variability of the score.
- The clearest symptom: under capture clusters, the temporal marginal CI [0.361, 0.726] **does not contain its own point estimate 0.731**. Under attacker host it is [0.466, 0.740], and under attacker device the point estimate of the paired difference sits near the upper end.
- A percentile interval that excludes the plug-in estimate is not a valid 95% interval. The paper nevertheless reports "[0.001, 0.151] barely excludes zero" as if it were evidence.
- A bootstrap over 10 captures, where 6 of the 8 attack classes each sit in a single capture, cannot estimate the variance of a between-capture effect. The authors' own result file calls it "a stress test, not a calibrated interval"; the paper text calls it "coarse".
- For one-cluster classes, the host-pair bootstrap gives zero-width intervals: DoS-HTTP temporal recall [0.985, 0.985] from 1 pair; DDoS-SYN [1.000, 1.000] from 6 pairs. These are degenerate, not precise. They should not be printed as CIs.

**Why it matters:**
- The paper's nuanced conclusion ("sign likely positive but not established under coarser clustering") is built on intervals whose coverage is unknown and, in some cells, demonstrably broken.
- The "present-classes" variant changes the upper bounds a lot (0.165 → 0.202; 0.151 → 0.223). The interval is therefore driven by a convention, not by the data.

**Concrete fix:**
- (a) Make per-class recall/F1 with host-pair counts the primary statistic. Print "n pairs = 1, no interval" instead of zero-width CIs.
- (b) For the coarse units, drop the percentile bootstrap. Instead report the per-capture (or per-attacker) paired differences themselves, with an exact sign or permutation test over clusters. With 10 captures this is honest and small enough to tabulate.
- (c) If bootstrap intervals are kept, use BCa or a studentised interval, and report the coverage problem (point estimate outside the interval) explicitly.
- (d) Fix one primary cluster unit before reporting, and justify it as the unit of independence: the attacking host/device is the natural one. Report the others only as sensitivity analyses. At present the host pair is the default even though it is near-singleton on IoT-23 (91.5%), which makes it almost a flow-level bootstrap there.

**Fixable without new experiments?** Yes. All of this is computable from the saved predictions.

### M4. The blocking policy was "chosen on validation", but the selection criterion is degenerate, so the grid's upper end picked it

**Location:** Sec. Response, "Policies"; `results/block_policy.md`; `src/tune_block_policy.py` (`KS = [1, 2, 3, 5, 10]`; rule at lines 64–67).

**Problem:**
- The rule is "fewest false blocks among policies within 0.005 of the best share of attack flows after block".
- On validation, *every* policy scores 0.995–0.996 (`block_policy.md`). The coverage constraint is therefore never active, and the rule reduces to "minimise false blocks". False blocks fall monotonically in k, so the rule picks the largest k in the grid: k = 10, because the grid stops at 10.
- With k = 20 in the grid, k = 20 would have been chosen, and it also loses the brute-force attacker (Table `tab:kcurve`).
- The validation table already showed the cost the criterion ignores: attacker pairs blocked fell from 29/42 (k = 1) to 20/42 (k = 10).
- The paper admits that DDoS-SYN dominates the criterion. It does not admit that this makes the "validation-chosen" label carry no information.
- The simulation also sorts by `bidirectional_last_seen_ms` with no export delay. That is why validation reports 0.995 while live reports 11.1% of attack flows after block — a 90-point mismatch between selection and test conditions.

**Why it matters:** The headline "requiring 10 verdicts blocked none but missed the Mirai and web attackers" is presented as a validation-selected operating point. It is an artefact of the grid and of a flow-weighted criterion. The real finding is the k trade-off curve (Table `tab:kcurve`), not the chosen policy.

**Concrete fix:**
- Replace the criterion with a pair-level, class-balanced one, e.g. "fewest false blocks subject to blocking ≥ X% of attacker pairs in every class present in validation", or a macro-average of per-class pair coverage.
- Simulate with the measured export delay (idle timeout plus the measured median lag).
- Re-select on validation and report the test outcome of the re-selected k from the existing run-1 verdict stream (Table `tab:kcurve` already contains it).
- State plainly that the current rule is equivalent to "the largest k considered".

**Fixable without new experiments?** Yes for the re-selection and the simulated test outcome. A new enforced live run is needed only if the authors want an *enforced* number for the new policy. The simulated one is adequate for a workshop if labelled as such.

### M5. The k trade-off and the false-block rate are set by the 60 s windows and the per-window counter reset

**Location:** Sec. Live, "Windows and harness"; Sec. Response, Tables `tab:blocking` and `tab:kcurve`; Abstract ("requiring 10 verdicts ... missed the Mirai and web attackers").

**Problem:**
- Each test window is 60 s, and "per-pair verdict counts" are cleared after each window. The low-rate attackers produce very few flows in 60 s: Mirai has 4–5 live flows in its whole window (`results/live/perclass_counts.md`), and Web has 12 flows from 3 attackers. Under these conditions, k = 10 is *unreachable by construction*.
- In a deployed gateway, counters persist or decay over a configured horizon. Whether k = 10 "misses Mirai" therefore depends on the harness's 60 s horizon, not on the detector.
- The reset also suppresses false blocks at high k, because benign pairs cannot accumulate verdicts either. Both sides of the trade-off are biased, in opposite directions.
- Validation (M4) simulated over the whole validation period with no reset, so selection and test differ in the counting horizon as well.
- The false-block denominator (1,674 "eligible benign host-pair windows") counts every pair seen in a window, including single-flow ICMPv6 link-local pairs (`blocking_accounting_r6.md`) that could only ever be blocked at k = 1. A rate per eligible pair is therefore not comparable across k, or across settings with different background mixes.

**Why it matters:**
- The abstract's trade-off sentence, the 3.6% rate and the Response check in Table `tab:checklist` all depend on the 60 s horizon.
- The total test exposure is 10 minutes of traffic. 60 false blocks in 10 minutes is about 360 per hour, an operationally relevant figure that the per-pair-window rate hides.

**Concrete fix:**
- (a) Re-simulate the k curve on the full temporal test period of each capture (offline flows plus the measured export delay), with counters that persist, or that decay over an explicit horizon (e.g. 60 s, 5 min, 30 min). Report the curve for each horizon.
- (b) Report false blocks per hour of traffic and the number of *distinct benign hosts* affected, next to the per-pair-window rate.
- (c) In the abstract, qualify the Mirai/web miss as "within 60 s windows".

**Fixable without new experiments?** Yes, (a)–(c) are simulations on existing flows. A longer live enforced run would strengthen it but is not required.

### M6. Live "stability" is shown with a metric that cannot detect the fidelity failures the runs actually have

**Location:** Sec. Live, "Repeats and CPU budget" and Table `tab:repeats`; Sec. Live, "Flow-by-flow match".

**Problem:**
- The flow-by-flow match (148,756 of about 148,800) was done **only for run 1**.
- In runs r2/r3 the live DDoS-SYN flow count is 12% and 29% above offline (160,242 and 184,483 vs 142,724), and DoS-HTTP has +2–4.5% extra flows even in run 1 (`perclass_counts.md`: 1,955 live vs 1,871 offline).
- These are exactly the flow-construction divergences the paper's Check 3 exists to catch. Yet the paper reports that "live macro-F1 was stable" (0.8038–0.8043). Macro-F1 cannot see them: the extra DDoS-SYN flows are all trivially classified as DDoS-SYN (recall 1.00), and all other classes are unchanged.
- This is the paper's own thesis ("scores hide problems") applied to its own live results.
- Replay at 52–77% of the original rate also stretches IAT and duration *feature values*. Verdict agreement under time dilation was measured only in run 1.

**Why it matters:** The claim that the live gateway "classifies the flows the model was evaluated on" is established for one run at one replay rate. The repeats then show that this does not hold at other rates. The stability conclusion follows only for macro-F1, which is the least sensitive statistic available.

**Concrete fix:**
- Run the existing `match_live_offline.py` on every run (r2, r3, half-core ×3, one-core, both enforced runs). Report match rate, the share of identical packet/byte counts and verdict agreement per window.
- Replace "live macro-F1 was stable" with the per-run match statistics.
- Plot flow-count ratio against achieved replay rate. The paper already has 7–9 points for this.

**Fixable without new experiments?** Yes, if the `flows.csv` files of those runs are kept (they appear to be, under `results/live/<run>/`).

### M7. CPU budget is confounded with replay rate, harness version and window set

**Location:** Sec. Live, "Repeats and CPU budget", Fig. `fig:delay`, Table `tab:repeats`; Threats ("tcpreplay shares the CPU with the gateway").

**Problem:**
- (i) tcpreplay and the gateway share one laptop CPU under WSL2, and the cgroup quota limits only the gateway. The achieved replay rate is therefore itself a function of the gateway's load:
  - half-core runs reached 11,831–12,401 pps;
  - no-limit runs reached 10,936–12,271 pps;
  - the one-core run reached the highest rate, 13,434.
- (ii) The one-core run used the *old* harness (no quiet wait, no reset); the half-core runs used the new one.
- (iii) Half-core was run on 3 windows, the others on 10.
- (iv) n = 1 (one core) and n = 3 per setting.
- "The CPU budget mattered only in the DDoS-SYN window" and "CPU pressure caused lag, not loss" therefore compare settings that differ in at least three factors at once.
- The DDoS-SYN delay with no limit already ranges from 17.8 to 34.0 s across the three runs. That is about as large as some between-setting differences.

**Why it matters:** The CPU-budget conclusion is the only "edge" result in the live section, and it cannot be separated from replay-rate variance.

**Concrete fix:**
- Report delay as a function of achieved replay rate, with points coloured by CPU budget, and fit or at least show both factors.
- Re-run one-core with the final harness.
- At minimum, rewrite the claim as "in these runs" and list the confounds explicitly in Sec. Live, not only in Threats.
- Pinning tcpreplay and the gateway to disjoint cores (`taskset`) would remove (i).

**Fixable without new experiments?** Partially. The re-plot and re-wording need no new runs. Removing the confound needs about 3–6 new runs, a few hours.

### M8. The evidence labels have no independent error estimate, and the one revision was asymmetric

**Location:** Sec. Labels, "Evidence-based labels" and "A label error found by the model"; Threats, "Internal".

**Problem:**
- All CIC-IoT2023 scores (including "true" F1) are against labels produced by a single author's endpoint rule: "attacker ↔ victim, on the attack's port where known".
- The rule labels all attacker↔victim flows as attack, including any benign protocol traffic between them, and all attacker↔non-victim flows as Benign: 2,384 Benign-labelled temporal test flows involve a confirmed attacker (`cluster_sensitivity_cic.md`).
- No sampled manual audit or estimated label-error rate is reported.
- The single revision came from error analysis of *false positives* only (the sixth DDoS source). No symmetric search of false negatives is reported. Correcting labels only in the direction of the model's predictions biases the scores upward.
- The MITM-ARP label is *defined* as a victim's relayed traffic, which is by construction indistinguishable from benign traffic in flow features. "Flow features cannot see MITM" is then partly a consequence of the label definition, and MITM-ARP still enters macro-F1 as one of 8 equal classes.

**Why it matters:** Every CIC number depends on these labels. The paper's own argument is that labels drive results.

**Concrete fix:**
- (a) Draw a stratified random sample (e.g. 50 flows per class × label-disagreement stratum). Check it against packet evidence, blind to the model's predictions, and report the label error rate with Wilson CIs.
- (b) Run the same error analysis on false negatives (attack-labelled, predicted Benign), and report whether any revision resulted.
- (c) Report macro-F1 without MITM-ARP, as the class is unlearnable by definition and is covered by the ARP watcher in the deployed system.

**Fixable without new experiments?** (b) and (c): yes. (a): needs a few hours of manual inspection, but no new data.

---

## MINOR issues

1. **Abstract, "delayed verdicts by up to 82.5 s".** 82.5 s is the *median* delay after flow end in the SQLi window (Sec. `sec:defect`), not a maximum. The true maximum can approach the 120 s active timeout. Say "median delay of up to 82.5 s per window".
2. **Abstract and Sec. `sec:defect`: what exposed the defect.** The defect was exposed by the delay and packet-accounting measurements (64.5% of packets exported), not by the flow-by-flow match. The text credits the match.
3. **Sec. Splits, boundary-spanning paragraph.** "0.700 to 0.690" over seven classes is given without an interval. `results/split_overlap.md` uses a *flow-level* CI for this comparison, contradicting Sec. Setup's argument that flow CIs are far too narrow. Give a host-pair paired CI or drop the inference.
4. **Sec. Setup, baselines.** "Close to a random forest (0.737)" and NSGA-II "at no measurable cost (0.723)" are single test-set point estimates with no paired interval. Given the ±0.1–0.15 host-pair widths, "no measurable cost" is literally true but uninformative. Use "not distinguishable at this sample size". State whether RF and HGB were tuned on validation like the tree was.
5. **Sec. Setup, Metrics.** The flow bootstrap uses 200 resamples (`cluster_ci.md`) and the host-pair bootstrap 1,000. Use the same number, or say why they differ.
6. **Bootstrap scope.** The bootstrap only covers test-set sampling, with the model fixed. The random-split seed spread (range 0.019, `random_seed_spread.md`) is reported only for random. Say that the temporal split has no split randomness, and that training variability is not in any interval.
7. **Paired design (Sec. Setup).** The temporal and random test sets are different flows. Only 2,682 of 4,641 CIC clusters are shared, and only 62,366 of 348,350 on IoT-23. On IoT-23 the "paired" bootstrap is therefore mostly unpaired. Report the shared-cluster share in the paper, not only in results files.
8. **IoT-23, "local host" clustering** (42 temporal clusters; paired common-class CI [−0.081, 0.005]) is computed in `results/iot23/cluster_sensitivity.md` but not reported. It is arguably the most defensible unit (the infected device). Report it, or explain why originator was preferred.
9. **IoT-23 Zeek labels** are themselves rule-based labels from the dataset authors, not ground truth. "Labels that are not ours" is correct, but the text in places treats them as true labels ("true F1"). Use "Zeek-label F1".
10. **Table `tab:kcurve`, "Time" column.** The median time to block is over a *different set of blocked pairs* at each k (survivorship). It falls from 19.0 s (k = 1) to 15.3 s (k = 5–20) only because slow pairs drop out. Report it per class, or flag that it is not comparable across rows.
11. **Table `tab:blocking`, k = 1 vs k = 10.** The two enforced runs differ in k *and* in MITM-ignore, and they are separate replays: the k = 1 DDoS window ran at 52% of the original rate, which the text says may inflate counts. This 3.6% is the abstract's headline. Use the same-stream simulation (Table `tab:kcurve`) for the comparison and the enforced runs as confirmation, or re-run k = 1.
12. **"0/1,675 false blocks" at k = 10.** For a single run, give the rule-of-three upper bound (≤ 3/1,675 ≈ 0.18%, ignoring dependence) and state that host-pair windows are not independent.
13. **ARP watcher (Sec. Response).** 1 true alert and 0 false alerts in nine 60 s windows. The paper already says this is not an FPR, but Table `tab:checklist` should not list it as a validated component.
14. **Context of the Benign FPR.** Live false blocks concentrate in the DDoS-SYN (12.5%) and DoS-HTTP (6.8%) windows. This suggests benign flows recorded *during* floods have attack-distorted features (IATs, retransmissions). Report the offline Benign FPR per capture, to separate "detector FPR" from "background perturbed by the attack".
15. **Sec. Live, "Windows and harness".** Taking the first 60 s after the training period is the test data closest in time to training, i.e. the most favourable slice of the temporal test set. Say so, or sample windows across the test period.
16. **Sec. Setup, trimming.** DDoS-SYN is 511,527 of 857,206 flows "as a consequence of trimming", and the temporal split covers only the first 10^6 packets of large captures. Any pooled number (pooled Benign FPR, "11.1% after block", 98.1% DDoS-SYN share) is an artefact of the trimming. Give per-class or per-capture versions wherever a pooled figure is quoted.
17. **Fig. `fig:delay` / Table `tab:repeats`.** The "Delay" column is a single median per run. Give an IQR or 90th percentile; the operational question is the tail.
18. **Run 1 used the old harness** (no quiet wait, no reset), yet it is the basis of both the fidelity check and Table `tab:kcurve`. Spill-over of the DDoS backlog into the next window could move flows across window boundaries. State whether the per-window assignment was checked.

---

## Things done well

- **Cluster-aware uncertainty with explicit sensitivity.** Sec. Setup and Sec. Splits report flow-level vs host-pair intervals, and `cluster_sensitivity_cic.md` and `iot23/cluster_sensitivity.md` give four cluster units, with the share of resamples missing a class. Few NIDS papers show how much the unit of independence matters (CIC: flow [0.712, 0.742] vs host pair [0.577, 0.823]).
- **Honest null replication.** Sec. Splits, IoT-23 states plainly that the temporal gap does not replicate, and attributes the IoT-23 gap to missing classes rather than spinning it.
- **The boundary-spanning analysis** (36.1% of temporal test flows continue a training connection; all 10 Mirai test flows) is a concrete, reusable leakage check. The observation that it inflates stratified C&C on IoT-23 is valuable.
- **The flow-by-flow live/offline match with packet accounting** (Sec. `sec:fidelity`) is the right check, and rarely done. Reporting achieved replay rates rather than nominal ×1.0 is commendable.
- **The NFStream defect** is diagnosed to the line, reproduced with a two-flow synthetic pcap and upstreamed with a regression test. The paper correctly notes that it changes timing only, not features.
- **False blocks counted per host-pair window**, with the policy fixed before the test windows, a trigger-flow vs pair-level definition check (`round2_checks.md`) and the full per-class k table, is a better response evaluation than the usual "attack traffic dropped %".
- **The released format** (Sec. Labels, "The benchmark as distributed") is shown to *force* file-name labels. This is a useful, checkable observation about CIC-IoT2023.
- **Threats to Validity** is specific rather than boilerplate. Every number traces to a script and a results file, and seeds are fixed.
