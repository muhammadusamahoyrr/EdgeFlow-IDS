# Facts sheet for the paper (single source of truth)

Every number in the paper must come from this sheet, which points to the result file that proves
it. Do not round differently from what is written here. Do not invent numbers, citations, venues
or results. If something is needed that is not here, write `\todo{...}` instead.

## Setting
- **Dataset.** CIC-IoT2023 (Neto et al., *Sensors* 23(13), 5941, 2023, doi:10.3390/s23135941).
  - 10 pcaps: Benign, DDoS-SYN, DoS-HTTP, Recon-PortScan, MITM-ArpSpoofing, DictionaryBruteForce,
    SqlInjection, XSS, CommandInjection, Mirai-udpplain. About 5.17 GB in total.
  - Files over 300 MB are trimmed to their first 1M packets (`src/trim_pcaps.sh`).
  - 8 classes: Benign, BruteForce, DDoS-SYN, DoS-HTTP, MITM-ARP, Mirai, Recon, Web (SQLi + XSS +
    CmdInj).
- **Flows.** NFStream 6.6.0 with `statistical_analysis=True`, idle_timeout 15 s, active_timeout
  120 s, and identical settings offline and live.
  - 54 statistical features. Identifiers (IPs, MACs, ports, protocol, timestamps) are excluded.
  - Total 857,206 labelled flows. Of these, DDoS-SYN accounts for 511,527 (a consequence of
    trimming).
- **Splits.**
  - Temporal: within each pcap, the first 70% of flows by start time form the training set.
  - Stratified: draws 70% at random, stratified by class (70/30).
  - Validation for every choice (tree limits, NSGA-II, blocking policy) is the last 20% of each
    pcap's training period.
- **Testbed.**
  - Mininet 2.3.0 + Open vSwitch on WSL2 Ubuntu 24.04 (kernel 6.6), on a laptop with an
    i5-8350U and no GPU.
  - Topology: h1 -- s1 -- gw -- s2 -- h2.
  - tcpreplay replays at original speed (x1.0). An OVS rule forwards everything from h1 to gw.
  - The gateway runs NFStream live capture (n_meters=1, 64 MB capture buffer), micro-batched
    decision-tree inference (≤256 flows or 50 ms), and optional OVS drop rules for both
    directions of a host pair.
  - A 200 packet/s ping ticker runs between h1 and h2 on a management subnet that is never scored
    or blocked.
  - Each live window is 60 s per pcap, cut just after the train/test boundary.
  - Connections that a training flow was still part of are removed from both the offline and the
    live side.
  - Between windows: a 30 s gap, then a wait until the gateway has caught up, then OVS blocks,
    verdict counts and ARP state are cleared, because each window comes from a different capture
    session that reuses the same IPs.
  - The CPU budget is a cgroup quota (systemd-run): none, 100% (one core) or 50% (half a core).

## C1 Labels (results/label_shares.md, data/attackers.json)
Background (benign) share of the flows in each attack pcap, after evidence-based labelling:

| pcap | Background share |
|---|---|
| XSS | 0.985 |
| CommandInjection | 0.983 |
| MITM-ArpSpoofing | 0.976 |
| SqlInjection | 0.948 |
| Mirai | 0.937 |
| DictionaryBruteForce | 0.909 |
| Recon | 0.302 |
| DoS-HTTP | 0.230 |
| DDoS-SYN | 0.001 |

- In the web, brute-force and MITM captures, 91–98.5% of flows are background (XSS 0.985).
- Evidence used to confirm attackers:
  - HTTP payloads on DVWA: `SLEEP(5)`/`UNION SELECT` from .178 for SQLi; `<script>` from .147 for
    XSS; `/vulnerabilities/exec/` from .147 for CmdInj.
  - Ports: brute force from .65 on SSH :22, then RTSP :554.
  - Top talkers: DDoS-SYN from 6 sources to .245:4070; DoS-HTTP from .66 to .71/.141:80; Mirai
    from 7 bots to .191 (UDP); the port scan from .178 (1,001 ports, 58 hosts).
  - ARP: MAC dc:a6:32:dc:27:d5 claims both the router IP .1 and its own .65.
- **Labelling rule:** a flow is labelled as an attack only if:
  - one end is a confirmed attacker and the other a victim, on the attack's port where known; or
  - (for ARP spoofing) its first packet was sent from or to the attacker's MAC and the attacker's
    own IP is not an endpoint.

  Every other flow is Benign.
- **Error analysis found a label bug.** 65,525 "Benign" flows predicted as DDoS-SYN came from a
  sixth DDoS attacker (.36) that joins after the first 300k packets. All flood victims were then
  re-checked over the whole trimmed file.
- **Prior work.**
  - Ramkumar et al. (arXiv 2412.10738) noted benign/attack mixing in the CIC-IoT2023 pcaps but did
    not quantify it.
  - Vitorino et al. (FPS 2025, arXiv 2511.08345) re-extract CICIoT23 flows and assume each capture
    contains only its named attack.

## C2 Random vs temporal split (results/baseline_*/report.md, metrics.json)
Decision tree (unconstrained), macro-F1 with 95% bootstrap CI over test flows (200 resamples):

| Split | Macro-F1 [95% CI] | Benign FPR |
|---|---|---|
| Stratified random | 0.869 [0.861, 0.875] | 1.1% |
| Temporal | 0.731 [0.712, 0.742] | 3.9% |

- BruteForce recall is 1.00 under the random split and 0.05 under the temporal split. Training saw
  SSH brute force (.67:22, 13:21–13:43); the test period is RTSP brute force on cameras
  (.11/.140:554, 13:43–15:01).
- Temporal test support:

  | Class | Test flows |
  |---|---|
  | Benign | 52,993 |
  | BruteForce | 605 |
  | DDoS-SYN | 153,402 |
  | DoS-HTTP | 10,110 |
  | MITM-ARP | 25 |
  | Mirai | 10 |
  | Recon | 39,819 |
  | Web | 192 |

- Macro-F1 over classes with at least 50 test flows (temporal, decision tree): 0.814.
- Model comparison, temporal split:

  | Model | Macro-F1 [95% CI] | Size | Single-flow predict |
  |---|---|---|---|
  | Decision tree | 0.731 [0.712, 0.742] | 227 KB | 0.136 ms |
  | Random forest | 0.737 [0.718, 0.747] | 21.3 MB | 7.826 ms |
  | Hist. gradient boosting | 0.714 [0.693, 0.730] | 1,012 KB | 4.5 ms |

  - Benign FPR for HGB is 7.6%.
  - The forest is about 94x larger and about 58x slower per call than the decision tree.
- MITM-ARP from flow features: precision 0.01, recall 0.16 (temporal, decision tree).
- **Connections spanning the boundary** (results/split_overlap.md):
  - 36.1% of temporal test flows (92,766 of 257,156) continue a connection whose earlier flows are
    in training.
  - Edge tree macro-F1: 0.725 [0.702, 0.741] on all test flows vs 0.604 [0.598, 0.610] with these
    flows removed. The second figure is depressed because Mirai then has no test flows.
  - Over the 7 classes that keep test flows: 0.700 vs 0.690.
  - DoS-HTTP F1 goes from 0.919 to 0.851.
  - All 10 Mirai test flows are continuations, so the Mirai test score is not evidence of
    generalisation.
- **Known context:** temporal or spatial bias in security ML (Arp et al. USENIX Sec 2022; Pendlebury
  et al. TESSERACT 2019). Prior temporal evaluation on CIC-IoT2023 exists: Traffic-MoE (arXiv 2601.00357) uses a per-class chronological Time-shift split (session byte features), and BRIDGE (arXiv 2604.11324) uses a pooled early/late split. Ours differs: a within-capture split on evidence-relabelled flows, with the cause of the gap (SSH to RTSP brute force). IoTGeM (arXiv 2401.01343) found telnet vs RTSP brute-force variants do not generalise (by design) and reported benign packets inside IoT-NID attack pcaps.

## Edge model and NSGA-II (results/edge_tree_tuning.md, results/nsga/summary.md)
- **Tree limits tuned on validation.** Limiting the tree (depth 16, leaf 10) raised the validation
  Benign FPR from 1.3% to 5.7%. The chosen setting is max_depth 32, min_samples_leaf 1, which is
  effectively unconstrained.
- **The deployed edge tree** (`decision_tree.pkl`, 54 features): temporal test macro-F1 0.725
  [0.702, 0.741]; 1,767 nodes; 222 KB.
- **NSGA-II (pymoo 0.6.2).**
  - Population 40, 30 generations.
  - Objectives: 1 − validation macro-F1, number of features, node count.
  - Edge pick (chosen on validation): 14 of 54 features; test macro-F1 0.723 [0.703, 0.734] vs
    0.725 [0.702, 0.741]; 1,681 vs 1,767 nodes; 211 vs 222 KB.
  - Conclusion: NSGA-II reduces inputs, not model size.

## C3 Live fidelity and CPU budget (results/live/run1, edge100, edge50)
- **run1** (no CPU limit, 10 windows):
  - Offline 148,779 flows vs live 148,884 flows. Macro-F1 offline 0.804 [0.710, 0.845], live 0.804
    [0.715, 0.844].
  - Packet ratio (live/offline) in each window: 0.9919–1.0064. NFStream kernel drops: 0.
  - DDoS window offered load: 12,271 packets/s (5.9 Mbps). Mirai window: 3,685 packets/s
    (16.2 Mbps).
  - Inference: batch p50 0.44 ms, median batch 209 flows, about 0.004 ms per flow.
  - Verdict after the flow's last packet: about 15 s (idle timeout), 17.8 s in the DDoS window.
  - First verdict per attacker pair: 15–35 s after its first packet.
  - Gateway CPU in the DDoS window: mean 120%, max 196%. Max RSS 990 MB.
- **edge100** (one core, 10 windows):
  - Live macro-F1 0.810 [0.752, 0.845]; 0 drops.
  - DDoS window: 13,434 pps; packet ratio 1.00; verdict after flow end 21.5 s; CPU mean 69%, max
    104%; RSS 1,025 MB.
- **edge50** (half a core; DDoS, DoS-HTTP and Mirai windows):
  - DDoS window: 12,088 pps; packet ratio 1.00; 0 drops; verdict after flow end 75.9 s; the gateway
    needed 138 s after the window to classify its backlog; CPU mean 50%, max 55%; RSS 981 MB;
    attack recall 1.00.
  - The DoS-HTTP window that followed was unaffected (verdict after flow end 15.4 s).
  - Offline macro-F1 0.914 vs live 0.918 on these 3 windows.
- **Contrast:** Tang et al. (VNICT 2026, arXiv 2609.24393): an RF with F1 0.97 on a benchmark had
  recall 0.0095 in deployment.

## NFStream 6.6.0 defect (results/nfstream_bug_check.md; issue nfstream#262)
- **Cause.**
  - `NFCache` (an LRU OrderedDict) moves a key to the MRU end only in `__setitem__`.
  - In `consume()`, a normal update (`cache[key].update(...)`) leaves the entry in place, so the
    cache stays in creation order.
  - `meter_scan()` expires flows from the LRU head and stops at the first non-idle flow, so a
    long-lived active flow blocks the idle expiry of every flow behind it until its
    active_timeout.
- **Fix:** one line, `cache.move_to_end(flow_key)` in the update branch. Flow boundaries and
  features are unchanged.
- **Measured** on two live windows (idle 15 s):

  | Window | Original: verdict after flow end | Patched: verdict after flow end |
  |---|---|---|
  | SQLi | 82.5 s | 15.6 s |
  | XSS | 49.2 s (packet ratio 0.645: flows not exported before the capture stopped) | 15.5 s |

- **Minimal offline reproduction** (2 UDP flows): export order A B A with the original code, B A A
  with the patch.
- **Upstream:** the symptom was reported before without a root cause (nfstream #120, 2022; #193).
  It is different from #196/#215/PR #227 (timer not advancing without packets). Reported as #262.

## C4 ARP and blocking (results/arp_eval.md; results/live/enforce_k1, enforce_policy)
- **ARP watcher**, rule "the router IP (.1) announced by a MAC other than its known MAC":
  - In the MITM window: 1 high alert, 1.7 s into the window, naming dc:a6:32:dc:27:d5.
  - In the other 9 windows: 0 high alerts.
  - Each live blocking run raised exactly 1 high alert.
  - The info rules ("one MAC, several IPs" and "IP moved to a new MAC") are noisy and are only
    logged.
- **Blocking.** Counts are per window, with blocks cleared between windows:

  | Policy | Pairs blocked | Correct | False blocks | Packets dropped |
  |---|---|---|---|---|
  | Block on the first attack verdict | 79 | 19 | 60 | 326,268 |
  | k=10 verdicts per pair, MITM-ARP flow verdicts ignored (chosen on validation) | 9 | 9 | 0 | 163,546 |

  - The k=10 policy blocks all 6 DDoS attackers (133k packets dropped), the DoS-HTTP attacker
    (30k), the brute-force attacker (217) and the port scanner (0, because the scan had ended).
  - It misses the 7 Mirai bots and the 3 web attackers (few flows per pair).
  - Block-on-first-verdict stopped Mirai (about 100k packets) but blocked 60 innocent pairs.
- **Validation simulation** (results/block_policy.md):
  - k=1: 128 false blocks.
  - k=10 with MITM ignored: 1 false block, while still blocking traffic that covers 0.995 of the
    attack flows arriving after a block.
- **Context:** k-of-n gating and confidence gating exist in prior SDN prototypes. Few works report
  false-block counts.

## Limitations (must appear)
- One dataset, and one capture session per attack class, so the evaluation measures
  within-session generalisation.
- Trimmed pcaps.
- Small test classes: Mirai 10 and MITM-ARP 25 test flows.
- A verdict needs the flow to end (idle 15 s), so detection is not per-packet real time.
- Blocking is per host pair.
- The gateway uses about 1 GB of memory.
- No-limit and half-core settings were run three times; one-core and blocking settings once.
- The testbed is an emulated laptop, not a physical edge device.

## Author and links
- Author: Muhammad Usama, Department of Computer Science, COMSATS University Islamabad, Pakistan.
  muhammadusamahoyrr@gmail.com
- Code and data: https://github.com/muhammadusamahoyrr/EdgeFlow-IDS (MIT)

## REVISION RESULTS (2 Nov 2026) — these extend or override the sections above

### File-name labels vs evidence labels (results/file_label_baseline.md)
13.4% of all 857,206 flows have a file label that differs from the evidence label. Edge tree:

| Split | Trained on | Apparent macro-F1 (scored vs file labels) | True macro-F1 (vs evidence labels) | True Benign FPR | Background flows called attack |
|---|---|---|---|---|---|
| Temporal | file labels | 0.537 | 0.396 | 71.8% | 38,034 / 52,993 |
| Temporal | evidence labels | 0.409 | 0.725 | 3.8% | 2,030 / 52,993 |
| Stratified | file labels | 0.617 | 0.426 | 70.2% | 33,939 / 48,323 |
| Stratified | evidence labels | 0.439 | 0.867 | 1.1% | 555 / 48,323 |

- Training on file labels flags about 7 in 10 background flows as attacks.
- The apparent score (0.537/0.617) also overstates the true score (0.396/0.426).

### Host-pair (cluster) bootstrap (results/cluster_ci.md)
Resampling 1,000 times over (capture, host pair) clusters:

| Split | Model | Macro-F1 | Flow-bootstrap CI | Host-pair CI | Clusters |
|---|---|---|---|---|---|
| Temporal | Decision tree | 0.731 | [0.712, 0.742] | [0.577, 0.823] | 3,465 |
| Temporal | Edge tree | 0.725 | [0.702, 0.741] | [0.568, 0.822] | 3,465 |
| Stratified | Decision tree | 0.869 | [0.861, 0.875] | [0.735, 0.877] | 3,858 |
| Stratified | Edge tree | 0.867 | [0.860, 0.873] | [0.733, 0.875] | 3,858 |

- Flow-level intervals are far too narrow.
- Under the host-pair bootstrap, the random and temporal intervals overlap substantially ([0.735, 0.877] vs [0.577, 0.823]). The gap rests on a few host pairs, mainly brute force. State this honestly. The SSH→RTSP finding rests on 3 host pairs (temporal BruteForce recall 0.053, host-pair CI [0.000, 0.842]; results/round2_checks.md): a case study, not a statistically robust effect (neither the macro-F1 gap nor the per-class drop is robust).

### Flow-by-flow match, live vs offline, run1 (results/live/run1/flow_match.md)
Flows are matched by 5-tuple and their order of appearance within that 5-tuple.

- Matched: 148,756. Offline-only: 23. Live-only: 128 (of 148,779 offline / 148,884 live flows).
- Per window, the share of matched flows with identical packet counts (bytes identical in the same share):

  | Window | Identical packets/bytes | Identical verdict |
  |---|---|---|
  | Benign | 0.9881 | 0.9763 |
  | CmdInj | 0.992 | 0.988 |
  | DDoS-SYN | 0.9998 | 1.000 |
  | BruteForce | 1.000 | 0.9967 |
  | DoS-HTTP | 0.9662 | 0.9921 |
  | MITM | 0.9927 | 0.983 |
  | Mirai | 0.9821 | 0.994 |
  | Recon | 1.000 | 0.9987 |
  | SQLi | 1.000 | 0.9978 |
  | XSS | 1.000 | 1.000 |

- Macro-F1 with host-pair CI: offline 0.804 [0.457, 0.823], live 0.804 [0.456, 0.822] (1,327 live clusters).
- Interpretation: live extraction is near-identical but not identical. A few percent of flows in some windows differ in packet counts (flow-boundary timing), and verdicts agree for ≥97.6% of matched flows in every window.

### Blocking trade-off on the live verdict stream, run1 (results/live/run1/block_curve.md)
Simulated per window. This only describes the trade-off; the policy was chosen on validation data. There are 26 attacker pairs in the windows.

| k | Ignore MITM verdicts | Pairs blocked | False blocks | Attacker pairs blocked |
|---|---|---|---|---|
| 1 | no | 83 | 64 | 19/26 |
| 1 | yes | 56 | 37 | 19/26 |
| 2 | yes | 23 | 5 | 18/26 |
| 3 | yes | 14 | 1 | 13/26 |
| 5 | yes | 10 | 0 | 10/26 |
| 10 | yes | 9 | 0 | 9/26 |
| 20 | yes | 8 | 0 | 8/26 |

- MITM-ARP attacker pairs: 0/7 are blocked at every k (the flow model cannot see them).
- Mirai pairs blocked: 7/7 at k=1, 6/7 at k=2, 1/7 at k=3, 0/7 at k≥5. DDoS-SYN: 6/6 at every k.
- Only 11.1% of attack flows in the windows start after their pair is blocked, at every k. Most attack flows come before any block can act, because a verdict needs the flow to end.

### Replay rate and backlog (from the fact-check)
- tcpreplay at ×1.0 could not reach the original rate of the heaviest windows on this laptop:
  - DDoS-SYN window: 388,686 packets in 22.31 s, about 17,423 pps originally; achieved 9,045–13,434 pps (10,936–13,434 in the detection runs; enforce_k1 9,045, enforce_policy 12,068).
  - Mirai: about 4,782 pps originally; achieved 2,664–3,685 pps.
  - Achieved rates are 52–77% of the original. Never write "original speed".
- **edge100 (one core):** a backlog formed. Gateway CPU stayed about 100% for 45–60 s after the DDoS replay ended, into the BruteForce window (mean CPU 40.6% there vs 0.8% in run1), yet that window's median verdict delay was 15.7 s.
- Only run1 (the first no-limit run) and edge100 used the earlier harness: a fixed 30 s gap, no catch-up wait, no per-window reset. All other runs (run1_r2, run1_r3, edge50 x3, enforce_k1, enforce_policy) used the final harness. Half-core catch-up time after the gap: 137.9, 162.7, 109.6 s (110–163 s).
- **XSS "packet ratio 0.645" in the unpatched bug check:** flows were not yet exported when the run stopped. On a continuously running gateway they would be exported late (at the blocking flow's active timeout), not lost. Call it "late, not lost".

### Prior work corrections
- **Temporal splits on CIC-IoT2023 exist.** Traffic-MoE (arXiv 2601.00357, App. E.6): a per-class chronological "Time-shift" split, first 40% / last 40% of each class's time span, on session byte features. BRIDGE/TCH-Net (arXiv 2604.11324): a pooled early/late split that includes CIC-IoT-2023. Do NOT claim the first temporal split.
- **IoTGeM** (Kostas, Just, Lones, arXiv 2401.01343) does not use CIC-IoT2023. It reports benign packets inside IoT-NID attack pcaps (App. A.3), and its brute-force split (telnet train, RTSP test) is related evidence that brute-force variants do not generalise.
- **Ramkumar et al.** (§4.3) re-filtered the CICIoT2023 pcaps per device by MAC address with tcpdump, using a device–attack mapping obtained from the dataset authors. They did not quantify the mixing.
- **Live repeats** are done (see Repeats below, results/repeats.md).

### Repeats (results/repeats.md)
- No-limit runs x3: live macro-F1 0.804 each time; half-core x3: 0.917-0.918 (offline 0.914). Kernel drops 0 and DDoS packet ratio 1.00 in all six.
- DDoS-SYN live flows vs replay rate: >=12,088 pps -> within 0.02% of offline 142,724; 11,611-11,831 pps -> +12%; 10,936 pps -> +29% (slower replay stretches gaps past the 15 s idle timeout and splits connections).
- DDoS-SYN verdict delay: 17.8-34.0 s (no limit), 60.3-97.0 s (half core).
- Peak RSS over all detection runs including repeats: 980–1,025 MB.
- False block (pair-level, use everywhere): the blocked host pair carries no attack flow in that window. enforce_k1 79/60, enforce_policy 9/0 (identical under the trigger-flow definition; results/round2_checks.md).

## REVISION R4 RESULTS (2 Nov 2026)

### IoT-23 pipeline (results/iot23/match_rates.md; src/iot23/download.py, extract_label.py)
- Dataset: IoT-23, Garcia, Parmisano, Erquiaga, Zenodo doi 10.5281/zenodo.4743746 (`garcia2020iot23`).
- 10 scenarios: 7 malware (1-1 Hide&Seek, 3-1 Muhstik, 8-1 Hakai, 20-1 and 21-1 Torii, 34-1 Mirai,
  42-1 Trojan) + 3 benign captures of real, uninfected IoT devices (4-1 Philips Hue bridge, 5-1 Amazon Echo, 7-1-Somfy-01 Somfy door lock; "Honeypot" is only the directory name, never call them honeypot traffic). Okiru captures are all >= 1 GB and
  are left out (src/iot23/download.py docstring).
- Same NFStream settings (config.STREAMER_KW) and the same edge-tree hyperparameters (depth 32,
  leaf 1, balanced), retrained on IoT-23.
- Labels: the dataset's Zeek conn.log.labeled, joined on unordered 5-tuple + nearest start within
  +-2 s; otherwise the flow's start inside a Zeek connection.
- 756,306 flows; matched 99.99% (start rule alone 97.89%); 38 unmatched flows dropped.
- Classes: Benign 468,575; PortScan 266,148; C&C 15,334; Attack 5,994 (only scenario 3-1);
  DDoS 211; FileDownload 6.
- DDoS (34-1): 14,394 Zeek connections on 211 distinct 5-tuples (unordered-key join; R5 correction, was 317 under a different tuple definition) become 211 NFStream flows (results/iot23/zeek_agreement.md).

### IoT-23 background share (results/iot23/label_shares.md; Zeek label Benign)
| Capture | Background share |
|---|---|
| Trojan 42-1 | 0.999 |
| Torii 20-1 | 0.818 |
| Torii 21-1 | 0.822 |
| Hide&Seek 1-1 | 0.696 |
| Hakai 8-1 | 0.347 |
| Mirai 34-1 | 0.241 |
| Muhstik 3-1 | 0.055 |

### IoT-23 file-label baseline (results/iot23/file_label_baseline.md)
- File label = family's main behaviour (our choice): Hide&Seek, Muhstik -> PortScan; Torii, Hakai
  -> C&C; Mirai -> DDoS; Trojan -> FileDownload; benign-device captures (4-1, 5-1, 7-1) -> Benign.
- 63.1% of 756,268 flows have a file label that differs from the Zeek label.

| Split | Trained on | Apparent macro-F1 | True macro-F1 | True Benign FPR | Background called attack |
|---|---|---|---|---|---|
| Temporal | file | 0.649 | 0.169 | 98.5% | 141,590 / 143,796 |
| Temporal | Zeek | 0.157 | 0.649 | 3.4% | 4,884 / 143,796 |
| Stratified | file | 0.692 | 0.149 | 98.4% | 138,323 / 140,573 |
| Stratified | Zeek | 0.167 | 0.863 | 3.7% | 5,170 / 140,573 |

### IoT-23 splits (results/iot23/splits.md) -- the CIC-IoT2023 temporal gap does NOT replicate
| Split | Macro-F1 | Flow CI | Host-pair CI | Macro-F1, 4 common classes | Boundary-spanning share |
|---|---|---|---|---|---|
| Temporal | 0.649 | [0.648, 0.650] | [0.613, 0.655] | 0.973 | 0.041 |
| Stratified | 0.863 | [0.764, 0.923] | [0.638, 0.939] | 0.956 | 0.058 |

- Common classes: Attack, Benign, C&C, PortScan. Temporal: DDoS has 0 training flows and
  FileDownload 0 test flows, so both score F1 = 0 by construction.
- Stratified rests on 63 DDoS (2 host pairs) and 2 FileDownload (1 host pair) test flows.
- C&C temporal: F1 0.945, 7 host pairs, host-pair CI [0.731, 0.983] vs flow CI [0.941, 0.949]
  (stratified: 10 host pairs).
- Boundary-spanning C&C share: 0.365 temporal, 0.68 stratified. Without spanning flows:
  stratified 0.863 -> 0.809; temporal stays 0.649.
- Lessons: check class presence in both halves; use host-pair CIs; report the spanning share.
  Never write "the temporal-split result replicates".

### Official CIC-IoT2023 CSVs, file labels (results/official_csv_baseline.md; src/analysis/official_csv_baseline.py)
- 483,053 rows, 39 packet-window features, ten per-pcap CSVs matching our captures; no IPs,
  timestamps or label column (label = file name), so they cannot be relabelled from evidence.
- Stratified random 70/30: macro-F1 0.749 (tree) / 0.803 (RF); accuracy 0.82 / 0.873;
  BruteForce recall 0.434 / 0.41; Web recall 0.374 / 0.353.
- Row order per file 70/30 (assumes rows follow capture order, undocumented): 0.727 / 0.778.
- Do NOT claim the official CSV gives "~99%".

### Upstream
- Fix + regression test submitted as PR nfstream/nfstream#263 (under review); bib `nfstream263`.
  Write "submitted", never "merged".

### Citations added in R4 (copied verbatim from refs_candidates.bib)
garcia2023labeling, pekar2024integrity, pinto2025flowexporter, akbari2020atmos, rasheed2026drift,
schraven2026mawiflow, orsdemir2026sok, ali2026siamxbert (= arXiv 2602.12183). Not used:
Biswas, Amaral, Ramkumar on "inconsistent labels".

## REVISION R5 RESULTS (2 Nov 2026) — extend or override the sections above

### Citation corrections (paper/CITATION_CHECK_R5.md)
- Rasheed & Alobaedy exact quote: "specific behaviour changes, such as total blindness, sensitivity inflation and relatively stable detection". The SSH->RTSP change is a change of target, not drift; only "analogous to" their blindness.
- Pekar & Jozsa exact quote: "the specific mechanisms employed for updating and terminating flows". Our defect changes export timing only, not flow boundaries or features, so it does not explain their feature-value differences.
- Garcia & Valeros: "most of the datasets they analysed"; blocking passage says "strong consequences" (IP blocking). Akbari et al.: "severe consequences".
- Tang et al. recall 0.0095: "in operational validation on a labelled laboratory capture", never "in deployment".
- CIC-IoT2023 CSVs: we used the per-pcap files (CSV/CSV), 39 features, no label/IP/timestamp; MERGED_CSV adds Label but rows are merged and shuffled, label = attack name. Files came from the Hugging Face mirror bencorn/CIC-IoT-2023 (layout matches README). Do not write "official".
- Bib: nfstream263 title "Keep LRU order on flow update so idle flows expire on time (#262)", open, "submitted". IoTGeM: Comput. Netw. 270:111550, 2025. Vitorino: FPS 2025, LNCS, pp. 150-166, 2026. Ramkumar: IEEE TSE 51(11):3117-3137, 2025. HERA: TrustCom 2024, pp. 1850-1856.

### IoT-23 per-capture Benign FPR (results/iot23/fpr_per_capture.md), temporal split
- Capture 1-1 supplies 95% (0.9515) of Benign test flows; pooled 98.5% is dominated by it.
- File-label tree: 97-100% of background flows flagged in every malware capture (mean 0.993; stratified 0.993 too); 4.6% in the three benign-device captures; macro-avg over captures 0.709. Zeek-label tree: 0.049.
- IoT-23 is a robustness test of the file-label claim with labels that are not ours, not evidence of practice on IoT-23.

### IoT-23 Zeek agreement (results/iot23/zeek_agreement.md)
- 35.2% of flows overlap >1 Zeek row; only 270 flows (0.04%) overlap rows of >1 class.
- DDoS 34-1: 14,394 rows on 211 5-tuples -> 211 flows; one flow covers 14,159 rows.

### IoT-23 common-class CIs (results/iot23/common_class_ci.md)
- Common-class macro-F1: temporal 0.973 [0.919, 0.983], stratified 0.956 [0.904, 0.969].
- Paired stratified - temporal: -0.017 [-0.039, -0.009] (temporal slightly but consistently higher).
- All six classes: +0.214 [-0.014, 0.293], not reliably above zero.

### CIC-IoT2023 paired random - temporal (results/paired_diff.md)
- Edge (deployed) tree +0.142 [0.025, 0.287]; decision tree +0.137 [0.024, 0.278]; 0.1% of resamples <= 0 for both.

### Blocking accounting (results/blocking_accounting.md)
- enforce_k1: 60 false blocks / 1,674 eligible benign host-pair windows = 3.6%; DDoS-SYN window 12.5%, DoS-HTTP window 6.8%.
- By trigger verdict: DoS-HTTP 32, MITM-ARP 21, DDoS-SYN 5, Mirai 1, Recon 1. By role: 56 uninvolved benign hosts, 2 attacker host's other traffic, 2 DDoS victim's other traffic.
- enforce_policy: 0 false blocks / 1,675. Attackers: k=1 19/26 (BF 1/1, DDoS-SYN 6/6, DoS-HTTP 1/1, MITM 0/7, Mirai 7/7, Recon 1/1, Web 3/3); policy 9/26 (Mirai 0/7, Web 0/3).
- DDoS-SYN, DoS-HTTP and Recon blocked at every k; k trades Mirai/Web/BruteForce coverage against false blocks.

### One-core run 0.810 vs 0.804 (results/blocking_accounting.md (d); results/live/edge100/live_vs_offline.json)
- edge100 Mirai window replayed at 2,664 pps (run1 3,685) -> 5 Mirai flows instead of 4; extra flow correct; Mirai F1 0.75 -> 0.80, +0.006 macro-F1. Flow splitting, not CPU.
- No-limit runs: live macro-F1 0.8038-0.8043.

## REVISION R6 RESULTS (2 Nov 2026) — extend or override the sections above

### IoT-23 spanning flows, common classes (results/iot23/spanning_common.md; src/iot23/spanning_common.py)
- Temporal: common-class macro-F1 0.973 -> 0.974 without spanning flows (host-pair CI [0.874, 0.982]); all-class 0.649 -> 0.649.
- Stratified: common-class 0.956 -> 0.918 [0.735, 0.955]; all-class 0.863 -> 0.809.
- The stratified drops come from C&C (F1 0.885 -> 0.733; precision 0.799 -> 0.583; 3,127 of 4,600 C&C test flows removed, 1,473 left) and FileDownload (1 of 2 test flows removed; F1 0.571 -> 0.400). Contributions to the all-class change: FileDownload -0.0286, C&C -0.0253. DDoS has NO spanning flows (63 left, F1 0.783 unchanged). NOTE: the R6 spec's "driven by DDoS and FileDownload" is wrong; it is C&C and FileDownload.
- No class loses all its test flows in either split.
- Composition facts: C&C test flows temporal 5,152 vs stratified 4,600; flows predicted C&C 5,683 vs 5,714; C&C precision 0.901 vs 0.799.

### Per-class live counts (results/live/perclass_counts.md; src/analysis/perclass_counts.py)
- Live Mirai flows 4 in every run except one-core (5); MITM-ARP 2, Web 12, BruteForce 25 in every ten-window run.
- One Mirai flow (TP 3, FN 1, FP 1): +1 detected -> +0.0063 macro-F1 over 8 classes, +0.0125 over the 4 half-core classes; one detected flow missed -> -0.0223 (8 classes), -0.0446 (4 classes).

### Blocking details (results/blocking_accounting_r6.md; src/analysis/blocking_r6.py)
- Eligible benign host-pair window: per run and window, an unordered IP pair seen in that run's live flows in the window (eval_live.in_window) with no attack-labelled flow there; summed over the ten windows.
- 1,674 (enforce_k1) vs 1,675 (enforce_policy) [run1 simulation 1,673]: the runs differ only by ICMPv6 (protocol 58) pairs to ff02::2 from two link-local sources that change every run (10 such sources are in every run, i.e. from the pcaps); they fall into different windows per run.
- MITM-ARP-triggered false blocks (21, enforce_k1): MITM window 7; the other 14 in eight other windows (Benign 2, CmdInj 2, DDoS-SYN 2, DictBF 1, DoS-HTTP 3, Recon 1, SQLi 1, XSS 2); none in Mirai. Roles: 20 uninvolved, 1 attacker host's other traffic.
- 11.1% at every k (run1): 212,965 attack flows, DDoS-SYN 0.9814 of them; 10.46% of DDoS-SYN flows start after block (0.1026 of the 0.1111), DoS-HTTP 0.0084; six DDoS-SYN pairs blocked at every k. Share 0.1108/0.1107 at k=20.

### Paired bootstrap (method, results/paired_diff.md, results/iot23/common_class_ci.md)
- Union clusters: CIC 4,641 (temporal 3,465, random 3,858, shared 2,682); IoT-23 348,350 (207,778 / 202,938, shared 62,366).

## REVISION R7 RESULTS (2 Nov 2026) — extend or override the sections above

### IoT-23 cluster sensitivity (results/iot23/cluster_sensitivity.md; src/iot23/cluster_sensitivity.py)
- Paper intervals use host-pair clusters = (capture, unordered host pair). Host-pair rows reproduce common_class_ci.md exactly.
- Cluster definitions: capture (10); originator = (capture, NFStream src_ip = sender of the flow's first packet); local host = (capture, private/link-local endpoint, else src_ip) [supplementary].
- Clusters (temporal / stratified / union): host pair 207,778 / 202,938 / 348,350; originator 350 / 4,997 / 5,212; local host 42 / 37 / 45; capture 10 / 10 / 10.
- Host-pair singletons: 91.5% of temporal test flows (207,509 singleton clusters), 88.8% stratified; Benign 94.2%, PortScan 95.1% of their temporal flows in singletons; C&C 7 clusters (median 620 flows), DDoS 3, Attack 65 (temporal).
- Common-class macro-F1 95% CI, temporal / stratified: host pair [0.919, 0.983] / [0.904, 0.969]; originator [0.576, 0.983] / [0.643, 0.979]; capture [0.469, 0.984] / [0.474, 0.976]; local host [0.460, 0.982] / [0.479, 0.978].
- All-class macro-F1 CI, temporal / stratified: host pair [0.613, 0.655] / [0.638, 0.939]; originator [0.384, 0.655] / [0.489, 0.908]; capture [0.312, 0.656] / [0.446, 0.906]; local host [0.307, 0.655] / [0.416, 0.904].
- C&C F1 (0.945 / 0.885) CI: host pair [0.731, 0.983] / [0.679, 0.940]; originator [0.780, 0.995] / [0.585, 0.989]; capture [0.819, 0.997] / [0.573, 0.978]; local host [0.782, 0.998] / [0.489, 0.991].
- Paired stratified - temporal, common classes (-0.017): host pair [-0.039, -0.009] (share <=0 0.991); originator [-0.130, 0.114] (0.738); capture [-0.078, 0.005] (0.886); local host [-0.081, 0.005] (0.888). => sign NOT robust to clustering.
- Paired all-class (+0.214): host pair [-0.014, 0.293]; originator [-0.037, 0.283]; capture [-0.032, 0.272]; local host [-0.034, 0.273].
- Paired C&C F1 (-0.060): host pair [-0.150, -0.028]; originator [-0.267, 0.032]; capture [-0.308, 0.014]; local host [-0.319, 0.014].
- Share of resamples missing a common class (temporal/stratified): capture 0.35/0.347 (0.9^10 = 0.35 analytically); originator 0.131/0.057; local host 0.377/0.353; host pair 0/0. Capture bootstrap is coarse (10 clusters; Attack, DDoS, FileDownload each in one capture).
- CIC-IoT2023 host-pair clusters: temporal 3,465 clusters, 1,072 singletons, 0.4% of test flows in singletons; random 3,858, 1,531 singletons, 0.6%. Floods: DDoS-SYN 6 clusters, DoS-HTTP 1 (temporal) / 2 (random), BruteForce 3, Recon 18/57.

### Same-window live baseline (results/live/same_window.md; src/analysis/same_window.py)
- Windows DDoS-SYN_Flood, DoS-HTTP_Flood, Mirai-udpplain (classes Benign, DDoS-SYN, DoS-HTTP, Mirai). Recomputation over each run's own windows reproduces every live_vs_offline.json exactly.
- Live macro-F1 on these 3 windows: run1 0.9171, run1_r2 0.9155, run1_r3 0.9175 (no limit); edge100 0.9284 (one core; the extra 5th Mirai flow); edge50 0.9175, edge50_r2 0.9172, edge50_r3 0.9173 (half core). Offline 0.9145 (json 0.91448 -> 0.914).
- => half core is not more accurate; 0.804 vs 0.917 is a different class set (8 vs 4 classes).

### Artifact
- Seeds: all 0 (train_baseline.SEED: train_test_split random_state, model random_state, flow bootstrap; config.EDGE_TREE random_state 0; tune_edge_tree random_state 0; nsga_select --seed 0 for pymoo and per-class subsampling; extract_flows sample random_state 0; cluster/paired bootstraps default_rng(0)). Live runs not seeded (timing).
- patches/nfstream-6.6.0-lru.diff: one added line `cache.move_to_end(flow_key)` in nfstream/meter.py (hunk @@ -254,6 +254,7 @@). Original obtained by patch_nfstream.py --revert on a temp copy; identical to meter.py in the PyPI wheel nfstream-6.6.0-cp312 manylinux. Live install untouched (marker count 1 before and after). Generator: src/make_nfstream_diff.sh.
- Tagged release / Zenodo DOI: NOT minted; placeholder LaTeX comment in discussion.tex.

## REVISION R8 RESULTS (2 Nov 2026) — extend or override the sections above

### CIC-IoT2023 cluster-unit sensitivity (results/cluster_sensitivity_cic.md; src/analysis/cluster_sensitivity_cic.py)
- Units: host pair (paper; rows reproduce paired_diff.md and cluster_ci.md exactly); attacker host = (capture, attacker IP) for every flow involving a confirmed attacker of its capture (attackers.json IP rule, src checked first; MAC rule for ARP spoofing -> .65), else the benign host pair; label not used for the key; attacker device = attacker IP across captures (supplementary, assumes IP = device); capture (10).
- Attacker assignment: all attack-labelled test flows assigned (temporal 204,163, random 208,839); benign-labelled flows assigned to an attacker 2,384 / 814.
- Clusters temporal / random / union: host pair 3,465 / 3,858 / 4,641; attacker host 3,413 / 3,738 / 4,520; attacker device 3,409 / 3,734 / 4,516; capture 10 / 10 / 10.
- Paired random - temporal (decision tree +0.137 / deployed tree +0.142), 95% CI, share <= 0:
  host pair [0.024, 0.278] / [0.025, 0.287] (0.001 / 0.001); attacker host [0.002, 0.165] / [0.004, 0.179] (0.017 / 0.007); attacker device [-0.004, 0.164] / [-0.002, 0.176] (0.057 / 0.036); capture [0.001, 0.151] / [0.004, 0.153] (0.022 / 0.013).
- Share of paired resamples missing a class (temporal / random): host pair 0.399 / 0.178; attacker host 0.829 / 0.827; attacker device 0.759 / 0.757; capture 0.971 / 0.971. => "76-97%" for the coarse units in the paper.
- Marginal macro-F1 CIs (own clusters), decision tree temporal / random: host pair [0.577, 0.823] / [0.735, 0.877]; attacker host [0.460, 0.739] / [0.487, 0.879]; attacker device [0.372, 0.741] / [0.468, 0.884]; capture [0.361, 0.726] / [0.469, 0.858]. Deployed tree: host pair [0.568, 0.822] / [0.733, 0.875]; attacker host [0.449, 0.734] / [0.487, 0.877]; attacker device [0.365, 0.738] / [0.468, 0.882]; capture [0.360, 0.719] / [0.468, 0.858]. Marginal missing-class share, host pair: 0.407 temporal / 0.176 random (already under the paper's scheme).
- Robustness variant, macro-F1 over classes present in the resample (results/cluster_sensitivity_cic_present.md; src/analysis/cluster_sensitivity_cic_present.py; same draws, zero-convention columns reproduce the above): paired CI decision tree / deployed: host pair [0.026, 0.202] / [0.026, 0.212]; attacker host [0.002, 0.202] / [0.007, 0.216]; attacker device [-0.007, 0.216] / [-0.003, 0.225]; capture [0.002, 0.223] / [0.007, 0.221]. Shares <= 0 identical to zero convention.
- => Paper: gap "probably positive but not robust to the cluster unit"; lower bound barely above 0 (attacker host, capture), includes 0 (attacker device).

### Random-split seed spread (results/random_seed_spread.md; src/analysis/random_seed_spread.py)
- Seeds 0-4; seed 0 reproduces baseline_stratified/metrics.json (0.868712 / 0.866912).
- Decision tree, joint (split = model seed): 0.8687, 0.8535, 0.8609, 0.8726, 0.8616; SD 0.0074, range 0.0191 (min 0.8535, max 0.8726). Split seed only: SD 0.008, 0.8523-0.8722. Model seed only: SD 0.001, 0.8663-0.8687.
- Deployed tree, joint: 0.8669, 0.8526, 0.8591, 0.8728, 0.862; SD 0.0077, 0.8526-0.8728. Split only: SD 0.0064, 0.8535-0.8697. Model only: SD 0.0011, 0.8666-0.8692.
- => spread comes from the split, not the tree seed. Paper: "0.8535-0.8726 over split and tree seeds 0-4" next to 0.869.

### One-core 3-window 0.9284 (results/live/same_window.md)
- Mirai F1 0.75 -> 0.80 with the 5th (correct) Mirai flow; 0.05/4 = 0.0125 over the four classes; other classes slightly lower (Benign 0.939, DoS-HTTP 0.975), net 0.9284 vs 0.9155-0.9175 for all other runs.

## FINAL REVISION RESULTS (2 Nov 2026) — extend or override the sections above

### Deployed tree everywhere
- The paper now reports only the deployed tree (results/models/decision_tree.pkl, EDGE_TREE, 54 features). The baseline "decision tree" (0.731 / 0.869 / +0.137) no longer appears; RF 0.737 and HGB 0.714 are compared against the deployed tree's 0.725.
- Deployed tree, CIC-IoT2023: temporal 0.725 host-pair CI [0.568, 0.822], flow CI [0.702, 0.741]; random 0.867 [0.733, 0.875] (results/cluster_ci.md).

### File-label FPR decomposition and LOCO (results/final/filelabel_decomposition.md)
- CIC temporal, file-label tree: pooled 71.8% (38,034/52,993); background in attack captures 86.1% (33,685/39,124); Benign capture 31.4% (4,349/13,869); 88.6% of FPs from background. Evidence-label tree: 3.8% / 4.8% (1,897/39,124) / 1.0% (133/13,869). Random split pooled 70.2% vs 1.1%.
- CIC LOCO on held-out attack captures: file-label 71.4–87.8%, evidence-label 0.5–5.4%; held-out Benign capture: file-label 100% by construction (no Benign training flow), evidence-label 1.5%.
- IoT-23 temporal: file-label background 99.97% (141,483/141,525), benign-device captures 4.7% (107/2,271); Zeek-label 3.4% (4,880/141,525), 0.18% (4/2,271).
- IoT-23 LOCO: benign devices file 23.4–46.7% vs Zeek 0–17.5%; malware-capture background file 9.4–99.95% vs Zeek 0–49.1% (3-1 49.1%, 42-1 42.0%).

### CIC gap decomposition, deployed tree (results/final/gap_decomposition.md, sign_test.md)
- Per-class F1 random/temporal and host pairs as in paper Table perclass; BruteForce 78.1% of the summed difference (1.136).
- Paired random − temporal: all 8 +0.142 [0.025, 0.287]; without BruteForce +0.036 [0.007, 0.199]; ≥5 host pairs in both test sets (6 classes) +0.030 [0.004, 0.098].
- Capture-level sign test, deployed tree: 6/9 positive, sign p 0.5078, permutation p 0.1758. Capture-cluster marginal CI of the temporal score [0.360, 0.719] excludes 0.725 (cluster_sensitivity_cic.md).
- BruteForce temporal test: .67:22 SSH 38 flows (475 in training), .11:554 356 and .140:554 211 RTSP (none in training); decision_tree.pkl detects 32/38 SSH, 0/567 RTSP.

### Live fidelity on every run (results/final/fidelity_all_runs.md)
- Seven non-enforced runs (run1, run1_r2, run1_r3, edge100, edge50, edge50_r2, edge50_r3): match rate ≥ 0.9998, same verdict ≥ 0.9997.
- DDoS-SYN window, original 17,423.6 pps: replay ≥ 69.4% of it → live flows within 0.02% of 142,724; at 62.8–67.9% → +12.3% to +29.3% flows, same packets 0.708–0.877. One-core live flows 142,725.
- Unpatched bug check: XSS window 118 of 224 flows logged.

### Blocking rates (results/final/blocking_rates.md)
- Enforced k=1: 60 false blocks = 360 per hour of capture time; 90 unique IPs; 9 of 10 windows. Policy: 0.
- run1 simulation per hour, MITM-ARP not ignored: k=1 384, k=2 84, k=3 12, k≥5 0; ignored: 222, 30, 6, 0.
- Selection rule degenerate: all 10 policies within 0.0012 of the best coverage → largest k in grid.
