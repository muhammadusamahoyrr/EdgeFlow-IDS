# Final review: combined fix plan (5 reviewers)

Reports: FINAL_REVIEW_{methodology,claims,writing,novelty,artifact}.md

## A. Must fix: errors or over-claims (text only, data already exists)

**A1. BruteForce (checked by me).**
- The test period contains SSH .67:22 (38 flows) as well as RTSP (567 flows).
- Deployed tree: SSH 32/38 detected, RTSP 0/567. Recall 0.053 (32/605) comes entirely from SSH.
- Fix the sentence and give this table. It makes the target-change claim stronger.

**A2. Claims mismatches (claims review).**
- Mirai/Web loss points in the k-table: Mirai is 0/7 from k=5 (1/7 at k=3); Web is 0/3 from k=10.
- Table repeats, one-core live flows: 142,725 (not "not recorded").
- "up to 82.5 s" is a per-window *median* delay.
- Intro: the audit was "run on two datasets"; in fact only checks 1–2 ran on both.
- "Code, data public" must name what is released.
- O1 "mostly-background classes handled worst": Mirai contradicts it. Drop or qualify.
- O4 "background" vs Benign test flows.
- O5: say the 0.396/71.8% figure is from the temporal split.
- Splits: the recall CIs come from the deployed tree, beside the baseline-tree table. Say so.
- CPU "only in DDoS-SYN window" vs the spill-over into BruteForce.

**A3. M1 file-label FPR (methodology).**
- Split each FPR into (i) in-capture background, trained under the attack name, and (ii) out-of-capture benign: the CIC Benign capture and the IoT-23 benign devices.
- Lead with (ii), e.g. IoT-23 4.6% vs 0.15%.
- Rename "true macro-F1" to "macro-F1 against evidence/Zeek labels".
- Optional, minutes of CPU: leave-one-capture-out.

**A4. M2: decompose the CIC gap.** BruteForce gives 0.89 of the 1.10 summed per-class drop. Report the gap with BruteForce excluded. Change the robustness filter from flows to host pairs.

**A5. M3: intervals.**
- Do not read the coarse-cluster percentile CIs as evidence; at least one excludes its own point estimate.
- Print "1 pair, no interval" instead of zero-width CIs.
- Optional: per-capture paired differences with a sign test.

**A6. M4/M5: blocking.**
- State that the selection rule reduces to "largest k in grid" because the coverage criterion was flat.
- Qualify the Mirai/Web miss as "within 60 s windows".
- Add false blocks per hour / distinct hosts.

**A7. Citations (novelty review).**
- IoTGeM "benign packets in attack captures": not found. Drop or soften.
- Bawany/Yan for multi-verdict gating: not supported. Present gating as our design choice.
- Traffic-MoE Time-shift dataset: not named in their appendix. Soften to "on a pooled benchmark including CIC-IoT2023" or verify.

## B. Should do: strengthens acceptance

**B1. Missing related work.** The reviewer reports these as verified on Crossref/arXiv; re-check each before adding.
- Lyon et al. CCNC 2026 (IoT-23 temporal)
- Pekar & Jozsa 2025 (partial flows)
- Zhao & Hassan CCS 2026 (streaming replay)
- Hofstede 2013 and Velan & Jirsík 2020 (timeouts and delay)
- Jacobs CCS 2022 (shortcuts)
- Lanvin 2023 (label errors)
- Andresini INSOMNIA 2021

**B2. Positioning.** Add a sentence saying each pitfall is known and the end-to-end audit is new. Say which checks are new (3, 4) and which apply known pitfalls (1, 2).

**B3. Writing.**
- Show the audit/checklist early, in the intro.
- One term per concept.
- Define table abbreviations (Blk., BF/DS/...).
- Cut the four repeated caveats on the gap.

**B4. M6: match on every run.** Run match_live_offline on every run from the existing flows.csv. Report flow-count ratio vs replay rate.

## C. Artifact (needs the user's OK for git/push)

**C1. Add the untracked files.** About 67 paper-critical files: src/iot23, patches, 10 analysis scripts, results/iot23, ...

**C2. README rewrite.** Paper-to-artifact map, datasets plus hashes, environment, deterministic parts.

**C3. Code fixes.**
- Script-relative paths.
- Generator for Table repeats.
- Remove or mark the stale mislabelled file.

**C4. Release.** Tagged release plus a Zenodo DOI (user's account), with flows/models/flows.csv in the Zenodo bundle.

## D. Optional, needs new runs (state as limits instead)
- M7: CPU confound (pin cores, re-run one-core).
- M8: blind label audit sample.
- Persistent-counter k simulation.
