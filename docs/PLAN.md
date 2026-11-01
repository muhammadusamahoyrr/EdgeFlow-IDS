# Plan (started 1 Nov 2026, target finish 15 Nov 2026)

> **Working log, kept for history.** Numbers here were recorded as the work went on and many were
> later superseded: the 0.97/0.98 table came from 5 small pcaps, the "17–26 KB" tree from that run,
> and the early live tests used an older gateway. The current, reproducible results are in
> `README.md` and `results/`.

## Environment (checked on this laptop, 1 Nov 2026)
| Item | Status |
|---|---|
| WSL2 Ubuntu 24.04.4, kernel 6.6.87.2 | OK |
| `modprobe openvswitch` | OK (OVS kernel module available) |
| `modprobe sch_netem` | OK (link emulation available) |
| veth | built into kernel |
| Python in WSL | 3.12.3 |
| CPU / RAM for WSL | 6 threads / ~9 GB |
| Disk | project on D: (~93 GB free); C: has only ~33 GB free |
| Docker Desktop | installed (29.3.1), not running |

## Research done (details in VERIFIED_TOOLCHAIN.md and DATASETS.md)
- [x] Mininet: apt package 2.3.0-1.1, `--switch ovsbr --controller none`
- [x] NFStream 6.6.0 has a Python 3.12 wheel; run in a venv inside the gateway namespace
- [x] tcpreplay: tcprewrite dst MAC to gateway, `--mtu-trunc --fixcsum`, replay at `-x 1.0`
- [x] Dataset: CIC-IoT2023 subset (~5.1 GB, mirror URLs checked) + IoT-23 (~265 MB)
- [x] Related work list
## Local progress
- [x] 1 Nov: apt install (mininet 2.3.0, tcpreplay 4.4.4, tshark); venv /opt/edgeflow (nfstream 6.6.0, sklearn 1.9.1, pymoo 0.6.2) via `src/setup_venv.sh`
- [x] 1 Nov: `topology/edge_topo.py --test` → pingall 0% loss through the gateway
- [x] 1 Nov: small pcaps downloaded (PortScan, BruteForce, SQLi, XSS, CmdInj; ~280 MB)
- [x] 1 Nov: attacker IPs confirmed from payloads → `data/attackers.json`
- [x] 1 Nov: `extract_flows.py` → 234,903 labelled flows (Recon 143,144 · Benign 89,950 · BruteForce 1,145 · Web 664)
- **Finding:** in the web and brute-force files, 95–98% of flows are background benign traffic, not attacks. File-name labelling would be badly wrong.
- [x] 1 Nov: labels tightened with victim ports (brute force 22/554, web 80) → Recon 143,144 · Benign 90,123 · BruteForce 1,080 · Web 556
- [x] 1 Nov: baseline training (`src/run_baseline.sh`), 54 features, results in `results/baseline_*`

| Split | Decision tree | Random forest | Hist. gradient boosting |
|---|---|---|---|
| Stratified random 70/30 | 0.972 | 0.982 | 0.978 |
| Temporal 70/30 per pcap | 0.743 | 0.757 | 0.739 |
(macro-F1, 1 Nov, 5 small pcaps)

- **Finding 2:** the 0.23 macro-F1 drop comes almost entirely from BruteForce (recall ~0.05 temporal vs ~0.98 random). Training only saw SSH brute force on .67:22; the test period is RTSP brute force on cameras (.11/.140:554). A random split hides this: same story as the FIT paper ("in-distribution gains do not transfer").
- Decision tree: 17–26 KB, ~0.2–0.3 ms per flow; random forest: ~2 MB, 10–18 ms per flow (single-thread, single-flow predict). The tree is the edge candidate.
- [x] 1 Nov: large files downloaded (resumable script); files > 300 MB trimmed to their first 1M packets (`src/trim_pcaps.sh`)
- [x] 1 Nov: attackers for DDoS-SYN (6 sources → .245:4070), DoS-HTTP (.66 → .71/.141:80), Mirai (7 bots → .191), MITM-ARP (MAC dc:a6:32:dc:27:d5 claiming .1) confirmed (`src/quick_talkers.sh`, `src/victim_sources.sh`)
- **Finding 3:** a 6th DDoS attacker (.36) joins after the first 300k packets; it was found because the model "misclassified" 65k of its flows as DDoS. Error analysis caught a label bug, not a model bug.
- [x] 1 Nov: full baseline, 857,206 flows, 8 classes (`src/run_all.sh`). Temporal macro-F1: DT 0.731, RF 0.737, HGB 0.714.
- **Finding 4:** MITM-ARP recall is low (0.12–0.16): relayed traffic looks statistically normal, so flow features cannot see ARP spoofing. Needs an ARP-layer rule (one MAC claiming two IPs).
- **Finding 5:** Mirai UDP floods collapse into very few long flows (41 flows from 1M packets).
- [x] 1 Nov: live pipeline (`src/gateway.py`, `topology/live_experiment.py`, `src/eval_live.py`), quick test on SQLi+XSS windows: capture ratio 1.00 / 0.996, macro-F1 live 0.969 vs offline 0.968
- **Bug fixes during live testing:**
  1. OVS MAC learning sent replayed frames back to h1 (capture 0.03–14%) → forward everything from h1 to the gateway.
  2. Several NFStream meters: quiet meters never expire flows → `n_meters=1`.
  3. **NFStream 6.6.0 LRU bug:** updated flows are not moved to the MRU end, so a long-lived flow at the LRU head blocks idle expiry of every flow behind it (verdicts ~70 s after flow end with idle_timeout 15 s). Patched with `src/patch_nfstream.py` → verdict 15.7 s after flow end. Worth reporting upstream.
- [ ] Full live run (10 windows) + NSGA-II (`src/run_live.sh`)

## Steps
### Week 1 (1–7 Nov)
1. Install toolchain in WSL; smoke test: 3-host Mininet topology, ping, tcpreplay one pcap through the gateway.
2. Download the dataset subset into `data/raw/`.
3. Extract flows offline with NFStream; attach labels; save to `data/processed/`.
4. Train baseline models (all features); record macro-F1, per-class recall.

### Week 2 (8–15 Nov)
5. NSGA-II feature selection: objectives = F1, inference latency, model size; plot the Pareto front.
6. Live gateway: NFStream on the gateway interface + model + drop rules.
7. Benchmark: replay rates sweep; measure throughput, detection latency, CPU/RAM (CPU-limited run to mimic an edge device).
8. Offline vs live F1 comparison.
9. README results, figures, 2-minute demo GIF.

## CV bullets (fill with real numbers only when done)
- Built a Mininet-emulated IoT gateway that extracts flow features live with NFStream and classifies them with a lightweight model, sustaining [X] Mbps at [Y] ms median detection latency on a CPU-limited edge setup.
- Used NSGA-II feature selection to cut model size by [A]% and latency by [B]% at a [C] pp macro-F1 cost, and measured a [Δ] macro-F1 gap between offline and live-extracted features.
