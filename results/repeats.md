# Repeated live detection runs (run-to-run variation)

Three runs per setting. `run1` used the earlier harness (fixed 30 s gap, no catch-up wait); every
other run used the final harness. Sources: `results/live/<run>/live_vs_offline.json`.

| Run | CPU budget | Live macro-F1 (offline) | Kernel drops | DDoS-SYN replay (pps) | DDoS-SYN live flows (offline 142,724) | DDoS-SYN verdict after flow end (s) | DDoS-SYN packet ratio |
|---|---|---|---|---|---|---|---|
| run1 | none | 0.804 (0.804) | 0 | 12,271 | 142,752 | 17.8 | 1.00 |
| run1_r2 | none | 0.804 (0.804) | 0 | 11,611 | 160,242 | 30.9 | 1.00 |
| run1_r3 | none | 0.804 (0.804) | 0 | 10,936 | 184,483 | 34.0 | 1.00 |
| edge50 | 1/2 core | 0.918 (0.914) | 0 | 12,088 | 142,730 | 75.9 | 1.00 |
| edge50_r2 | 1/2 core | 0.917 (0.914) | 0 | 11,831 | 160,475 | 97.0 | 1.00 |
| edge50_r3 | 1/2 core | 0.917 (0.914) | 0 | 12,401 | 142,729 | 60.3 | 1.00 |

- **Stable across runs:**
  - Live macro-F1 (0.804 every time with no limit; 0.917–0.918 at half a core).
  - Zero kernel drops.
  - Packet ratio 1.00 in the DDoS-SYN window.
  - Mirai-window verdict delay of 15.1–15.2 s.
- **Varies with the achieved replay rate:**
  - The DDoS-SYN window holds 388,686 packets in 22.3 s (about 17,400 pps originally).
  - When tcpreplay reached at least 12,088 pps, the live flow count matched offline within
    0.02%.
  - At 11,611–11,831 pps it was 12% higher, and at 10,936 pps 29% higher.
  - Slower replay stretches inter-packet gaps. Some gaps then exceed the 15 s idle timeout, so
    connections are split into more flows, while every packet is still captured.
- **DDoS-SYN verdict delay:** 17.8–34.0 s with no limit and 60.3–97.0 s at half a core.
