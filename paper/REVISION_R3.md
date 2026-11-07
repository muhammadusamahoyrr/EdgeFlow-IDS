# Round-3 revision list (merged from Reviewer 2 round 2 + final fact-check + new checks)

Apply all MUST and SHOULD items. Each fact listed here has been verified against the result
files.

## MUST

1. **One false-block definition.** Use the pair-level definition everywhere: "a block is false if
   the blocked host pair carries no attack flow in that window".
   - The live counts are identical under both definitions (`results/round2_checks.md`):
     `enforce_k1` 79 pairs blocked / 60 false; `enforce_policy` 9 / 0.
   - Fix the Tab. VI caption and the Construct threat.

2. **Splits: the CI statement and the BruteForce framing.**
   - Host-pair intervals: random [0.735, 0.877] vs temporal [0.577, 0.823]. Write "overlap"
     (substantially), not "overlap slightly", in `splits.tex` and in the Conclusion threat.
   - Per-class host-pair CIs (`results/round2_checks.md`, edge tree, temporal):
     - BruteForce recall 0.053, CI [0.000, 0.842]. Only **3 host pairs** (one SSH pair seen in
       training, two RTSP pairs in the test period).
     - Mirai 0.90 [0.571, 1.000] (6 pairs).
     - MITM-ARP 0.16 [0.000, 0.375] (13 pairs).
     - Benign 0.962 [0.901, 0.990].
   - Under the random split BruteForce is 1.000 [1.000, 1.000] (3 pairs).
   - **Framing:** the brute-force change of target (SSH to RTSP) is a concrete mechanism shown on
     3 host pairs, a case study and not a statistically robust effect. Neither the macro-F1 gap nor
     the per-class drop is statistically robust under host-pair resampling. State this plainly.
     The step's lesson stays: a random split puts RTSP brute-force flows in training and hides the
     failure.

3. **Two trees and three live macro-F1 values.**
   - Use the deployed (validation-tuned) tree's numbers in the abstract and intro (0.725, FPR
     3.8%), or say once in §III that the unconstrained baseline tree gives 0.731 / 3.9% and the
     deployed tree 0.725 / 3.8%.
   - Add one sentence explaining that the live macro-F1 (0.804 on ten 60 s windows, with
     boundary-spanning connections removed; 0.914–0.918 on the three half-core windows) is computed
     on a different, smaller sample and is not comparable to the test-set 0.725.

4. **Replay rates** (`live.tex`, "Achieved replay rates"; `discussion.tex`, External).
   - DDoS-SYN window: 388,686 packets in 22.31 s, about 17,423 pps originally.
     - Achieved: no-limit runs 12,271 / 11,611 / 10,936; one core 13,434; half core 12,088 /
       11,831 / 12,401; `enforce_k1` 9,045; `enforce_policy` 12,068.
   - Mirai window: about 4,782 pps originally; achieved 2,664–3,685.
   - Write "9,045–13,434 packets/s (10,936–13,434 in the detection runs) … i.e. 52–77% of the
     original rates". Use 52–77% in `discussion.tex` External.
   - In `response.tex`, add: "In the block-on-first-verdict run the DDoS-SYN window was replayed at
     only 9,045 packets/s (52%); slower replay splits flows (Table repeats), so that run's
     DDoS-window flow and block counts may be inflated."

5. **Harness per run.** Only the FIRST no-limit run (`run1`) and the one-core run (`edge100`) used
   the earlier harness (fixed 30 s gap, no catch-up wait, no per-window reset). All other runs used
   the final harness, including `run1_r2`, `run1_r3`, `edge50` ×3 and both blocking runs.
   - Fix `live.tex` Harness and `discussion.tex` Internal.
   - Tab. cpu caption: "(first run per setting; repeats in Table~\ref{tab:repeats})".
   - The half-core catch-up time was 110–163 s over three runs (137.9, 162.7, 109.6). Add it.

6. **Abstract.**
   - Write "delayed verdicts … to up to 82.5 s" (one window; the other was 49.2 s).
   - Use the tightened abstract below (adapted; about 180 words max).
   - Use "91–98.5%" for the background share (XSS is 98.5%), and use it consistently everywhere
     (abstract, intro, labels, lessons).

## SHOULD

7. **Late blocks.**
   - Define the 11.1% as attack flows *starting* after their pair's block, "in the run-1
     simulation", dominated by DDoS-SYN flows.
   - Add the dropped-packet share in the enforced runs (`results/live/enforce_k1/enforcement.md`
     and `enforce_policy/enforcement.md`, column `dropped_share_of_window`): for example DDoS-SYN
     0.503 (k1) / 0.342 (policy), DoS-HTTP 0.707 / 0.698, Mirai 0.347 (k1).
   - Mirai: "blocked all 7 Mirai bots (about 100k packets, 35% of the window, dropped)".

8. **Time-to-block.** It is not monotonic because the set of blocked pairs changes with k. Either
   report it per class from `results/live/run1/block_curve.md` (if available) or add one clause
   explaining why.

9. **Thesis example.** In §VI-B, add: "Equal macro-F1 (0.804) across runs whose DDoS-SYN flow
   counts differed by up to 29% shows again that equal scores do not imply equal flows."

10. **Structure.**
    - Move "Model and size choices" from §V to §III.
    - Merge Tab. IV (cpu) and Tab. V (repeats) if it saves space, without losing the one-core
      column.
    - Add per-class columns to the k-curve table from `block_curve.md` (Web and BruteForce as well
      as Mirai).

11. **Figures.** Regenerate with `src/make_figures.py` (WSL: `/opt/edgeflow/bin/python
    src/make_figures.py`, run from `/mnt/d/EdgeFlow-IDS`).
    - Remove the in-plot titles (captions carry them).
    - Fonts ≥ 8 pt at column width.
    - `live_delay`: short x labels (Benign, CmdInj, DDoS, BruteF, DoS-HTTP, MITM, Mirai, Recon,
      SQLi, XSS), not overlapping; legend readable.
    - `split_recall`: legend below or compact.
    - Keep `figsize` suitable for `\columnwidth`.

## Accuracy fixes (from the fact-check)

- **Traffic-MoE** (`related.tex`): "a per-class chronological split on packet header and payload
  bytes, apparently including CIC-IoT2023" (Appendix I in v2; the dataset is implied, not named).
- **BRIDGE:** the early/late split could not be confirmed from the abstract. Verify in the full
  text of arXiv 2604.11324 (§5.8 "training on early windows, testing on later windows" was reported
  earlier). If it cannot be verified, soften the sentence to "BRIDGE also reports a time-ordered
  evaluation on a pooled benchmark that includes CIC-IoT-2023" or drop it.
- **IoTGeM:** the telnet→RTSP brute-force split is in §3.3 of the full text (quoted earlier:
  "training data involves telnet BF, the validation data involves password attacks and the test
  data involves a RTSP BF attack"). Keep it.
- **Stratified split:** write "draws 70% at random, stratified by class".
- **FPR:** 3.9% is the baseline tree, 3.8% the deployed tree. Say so once.
- **Peak RSS:** 980–1,025 MB including the repeats.
- **Batch latency:** "median batch latency 0.44 ms (median batch size 209)".
- **Web attackers in the k-curve:** "from k=5 (1/3, then 0/3 at k≥10)" (check against
  `block_curve.md`).
- **Validation simulation:** "the last packet of its k-th flow predicted as an attack".
- **Boundary-spanning flows:** "share a 5-tuple with a training flow of the same capture".
- **Overfull box:** fix the CmdInj row of Tab. background (shorter path text).

## Tightened abstract (from Reviewer 2; adapt the numbers to the rules above)

> Each step from benchmark to gateway exposed a problem the previous step hid, and a cheap check
> caught each one. We audit one ordinary detector, a decision tree on 54 NFStream flow features
> trained on CIC-IoT2023, from labels to live blocking on an emulated Open vSwitch gateway.
>
> - *Labels:* 91–98.5% of flows in the web, brute-force and MITM captures are background traffic.
>   Training on file-name labels yields a true macro-F1 of 0.396 and flags 71.8% of benign flows,
>   against 0.725 and 3.8% with evidence-based labels.
> - *Splits:* a random split hides that brute-force recall falls from 1.00 to 0.05 when the target
>   changes from SSH to RTSP within one capture.
> - *Live:* matching live to offline flows one by one exposed a forwarding pitfall, idle flow
>   meters and a previously undiagnosed NFStream ordering defect that delayed verdicts by up to
>   82.5 s, which offline evaluation cannot show.
> - *Response:* blocking on the first verdict blocked 60 benign host pairs; requiring 10 verdicts
>   blocked none but missed the Mirai and web attackers.
>
> Code and data are public.
