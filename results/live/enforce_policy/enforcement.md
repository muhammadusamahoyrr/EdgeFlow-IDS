# Enforcement results (enforce_policy)

Blocked host pairs: 9 · correct (attack) 9 · false blocks 0
Packets dropped by the gateway's rules: 163,546
A pair is blocked only after its first flow has ended and been classified (idle timeout 15 s), so short attacks finish before the block.

| window               |   blocked_pairs |   correct |   dropped_packets |   window_packets |   median_block_after_flow_start_s |   dropped_share_of_window |
|:---------------------|----------------:|----------:|------------------:|-----------------:|----------------------------------:|--------------------------:|
| DDoS-SYN_Flood       |               6 |         6 |            133048 |           388686 |                           15.2807 |                     0.342 |
| DictionaryBruteForce |               1 |         1 |               217 |             3070 |                           36.9417 |                     0.071 |
| DoS-HTTP_Flood       |               1 |         1 |             30281 |            43353 |                           15.2165 |                     0.698 |
| Recon-PortScan       |               1 |         1 |                 0 |             5738 |                           15.3804 |                     0     |

False blocks (benign pairs):

| window   | src_ip   | dst_ip   | dst_port   | pred   | dropped_packets   |
|----------|----------|----------|------------|--------|-------------------|
