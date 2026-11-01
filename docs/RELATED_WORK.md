# Related work and what is (not) new (searched 1 Nov 2026)

[V] = abstract or relevant passage read · [A] = abstract or snippet only · [K] = background knowledge, not re-fetched.

## Not new: do not claim
- **Benign/background traffic inside CIC attack captures.**
  - Ramkumar et al., arXiv 2412.10738 (2024) [V]: CIC-IoT2023 pcaps mix benign packets with attack packets; they split by device MAC.
  - Fadel 2026, IoT-DIAD [A].
  - Engelen et al. 2021, CIC-IDS2017 [K].
- **Temporal split scoring lower than a random split.**
  - Arp et al., USENIX Security 2022 [K].
  - Pendlebury et al., TESSERACT, USENIX Security 2019 [K].
- **A decision tree being as good as a random forest for an edge IDS, and GA/NSGA-II feature selection.**
  - Computer Networks 2020 (NSGA2-LR) [A].
  - arXiv 2406.09180 [A].
  - Mathematics 2025, CICIoT2023 [A].
  - Scientific Reports 2025 [A].
- **Live NFStream + ML IDS, and Mininet/OVS ML IDS.**
  - Realguard, Sensors 2022 [A].
  - PDGC 2024, NFStream → Kafka → Spark [A].
  - About 12 GitHub prototypes.
- **ARP-spoofing rule:** arpwatch and Snort's ARP preprocessor [K]. FlowIoMT 2025 [A] reports flow features *can* detect ARP spoofing, so we say only that *our* NFStream feature set did not.
- **OVS/OpenFlow automatic blocking:** many SDN prototypes. SDN-IoT-Sentinel uses a 2-of-3 verdict gate.

## Deep search (1 Nov 2026, ~45 queries, GitHub issues read in full): every item below is PARTLY NEW
Method precedents to cite: Engelen et al. SPW 2021 and Liu et al. CNS 2022 (CIC-IDS2017/2018 relabelling);
Flood et al. EuroS&P 2024 (dataset design smells); Pinto/Vitorino et al. ICISSP 2025 and "Flow timeout
matters" (FGCS 166, 2025) on exporters and timeouts (offline only); Wu et al. arXiv 2609.12605 (eBPF/XDP
on Raspberry Pi 5, CIC-DDoS2019 replay); ML Defender arXiv 2604.04952 (replay of one CTU scenario);
arXiv 2004.06432 (zero false-positive IPS trade-off); nfstream issues #120 (same symptom, 2022, no root
cause) and #193 (closed as expected).

## Appears new (to our knowledge)
1. **Measured** background share (91–98%) in the CIC-IoT2023 web and brute-force pcaps, with per-flow labels from evidence: payloads, attacker/victim IPs, ports, ARP. Contrast: Vitorino et al., FPS 2025, arXiv 2511.08345 [V] still assume each capture contains only its named attack.
2. A temporal-split evaluation on CIC-IoT2023 with a root cause for the drop: brute force moving from SSH to RTSP.
3. A controlled offline-vs-live test on identical held-out windows, measuring:
   - packet capture ratio
   - NFStream drop counters
   - cgroup CPU limits (no limit, one core, half a core)

   Contrast: Tang et al., VNICT 2026, arXiv 2609.24393 [V, abstract]: RF F1 0.97 on a benchmark but recall 0.0095 in deployment.
4. False-block counts for automatic blocking (59 of 77 pairs with block-on-first-alert), and a policy chosen on validation data.
5. **NFStream 6.6.0 idle-expiry bug.**
   - **The bug:** in `meter.py`, a flow that a packet updates is not moved to the most-recent end of the LRU cache, so a long-lived flow blocks idle expiry for every flow behind it.
   - **Status:** still present on master (meter.py unchanged since 2024-05-10).
   - **Related issues:** the likely root cause of the symptom in open issue #120 (2022, never diagnosed; cite #120 and #193). It is different from #196/#215 (timer does not advance without packets), and open PR #227 does not fix it.

## Deep GitHub search (1 Nov 2026: 80 repository-search queries + 9 web searches, ~600 repos, ~45 READMEs read)
No repo matches this project in substance (no similarity score >= 4/5). Closest (3/5), each covering only part of it:
- maremethembalethu-hue/reaf-5g-prototype: replays labelled CICIoT2023 pcaps through a simulated 5G UPF, XGBoost / decision tree "Lite", notes live-vs-training divergence; no blocking, no NFStream, no evidence-based relabelling.
- MiltonTwi/iot-sdn-ai: Mininet + OVS IoT network, Ryu DROP/meter rules, IP-MAC anti-spoofing, "0 false alarms, 0 collateral rules"; self-generated attacks, CIC-IoT-2023 only as an external CSV test.
- shivangtanwar/xai-sdn-ids: confidence- and persistence-gated DROP (close to our k-verdict policy); self-generated data, controller statistics.
Also related: harsh-pandhe/netguard-ml (NFStream, temporal split, CIC-IDS2017), anacletu/ml-intrusion-detection-cicids2017 (tcpreplay on a Raspberry Pi 5).
Commonplace on GitHub: NFStream + ML live detection (~15 repos), Ryu/Mininet/OVS ML IDS with DROP rules (dozens), CICIoT2023 notebooks (100+), ARP-spoof watchers, GA/NSGA feature selection.
Not found anywhere: evidence-based per-flow relabelling of CICIoT2023 pcaps; tcpreplay of held-out windows through a blocking Mininet/OVS gateway; cgroup CPU-limited gateway evaluation; validation-chosen k-verdict policy with false-block analysis on replayed real data; an NFStream idle-expiry patch.
README matching only (GitHub code search unavailable), so treat as indicative.

## Open-source projects closest to ours (first, quick search)
- **netguard-ml:** NFStream, CIC-IDS2017, honest temporal evaluation; no IoT, no blocking.
- **TrangTuanAnh/tls-anomaly-detection-ids:** NFStream + MLP + iptables blocking; no evaluation.
- **Sunay20/IDS_IoT:** RT-IoT2022, NFStream, IP blocking; random split only.
- **chiragbiradar/DDoS-Attack-Detection-and-Mitigation, icesonata/DDoSDN:** Mininet + Ryu + RF on switch statistics.

None combines CIC-IoT2023, live NFStream capture, replay of the dataset's pcaps through Mininet/OVS, OVS blocking, and a live-vs-offline evaluation with CPU limits (search was rate-limited, so this is indicative only).

## To verify before publishing a paper
- Full text of PDGC 2024 and of Tang et al. 2026.
- Fadel's paper, beyond the repository README.
- Whether NFStream issue #120 shares our root cause (needs a reproduction).
