# Datasets (researched 1 Nov 2026)

## Primary: CIC-IoT2023 pcaps, ~5.1 GB subset
- Official page: https://www.unb.ca/cic/datasets/iotdataset-2023.html
- Download mirror (unofficial, checked on 1 Nov 2026): https://huggingface.co/datasets/bencorn/CIC-IoT-2023
  - URL pattern: `https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/PCAP/<Folder>/<file>`
  - There is one folder per class (33 attack folders + `Benign_Final`). Large classes are split into 2,048 MB parts.

### Folder sizes on the mirror (checked 1 Nov 2026)
| Class (our label) | Folder / file | Size |
|---|---|---|
| Benign | Benign_Final/BenignTraffic3.pcap | 854 MB |
| DDoS-SYN | DDoS-SYN_Flood/DDoS-SYN_Flood15.pcap | 1,059 MB |
| DoS-HTTP | DoS-HTTP_Flood/DoS-HTTP_Flood1.pcap | 1,492 MB |
| Recon | Recon-PortScan/Recon-PortScan.pcap | 201 MB |
| MITM-ARP | MITM-ArpSpoofing/MITM-ArpSpoofing1.pcap | 632 MB |
| BruteForce | DictionaryBruteForce/DictionaryBruteForce.pcap | 39 MB |
| Web | SqlInjection/SqlInjection.pcap | 10 MB |
| Web | XSS/XSS.pcap | 13 MB |
| Web | CommandInjection/CommandInjection.pcap | 29 MB |
| Mirai | Mirai-udpplain/Mirai-udpplain24.pcap | 840 MB |

### Labelling recipe
The label comes from the file, but **not every flow in an attack file is an attack**.
1. Run NFStream offline with the same settings that will be used live.
2. For each attack file, find the attacker and victim IPs from the top talkers (`tshark -z conv,ip`, or group by `src_ip`). For ARP spoofing, use the MAC that sends unsolicited ARP replies.
3. Give the file's class only to flows that involve the attacker. Mark all other flows benign, or drop them, and report both versions.
4. Merge the classes into 8: Benign, DDoS-SYN, DoS-HTTP, Mirai, Recon, MITM-ARP, BruteForce, Web.

### Known issues to cite
- arXiv 2412.10738 (Ramkumar et al., 2024): not every attack was run against every device as the paper claims. Seen only in a search snippet; read it before citing.
- The attack pcaps may contain background benign traffic (unverified). This is why step 3 is needed.

## Second (generalisation): IoT-23, ~265 MB
- Source: https://mcfp.felk.cvut.cz/publicDatasets/IoT-23-Dataset/IndividualScenarios/
- Scenarios:
  - CTU-IoT-Malware-Capture-8-1 (Hakai, 2 MB)
  - CTU-IoT-Malware-Capture-21-1 (Torii, 4 MB)
  - CTU-IoT-Malware-Capture-34-1 (Mirai, 120 MB)
  - CTU-IoT-Malware-Capture-1-1 (Hide and Seek, 139 MB)
  - CTU-Honeypot-Capture-4-1 (benign)
- Labels are in `bro/conn.log.labeled` (Zeek). Join on the 5-tuple, with ±2 s on the start time, and try the reverse direction too.

## Not used
- **TON_IoT:** labels need attacker-IP + time-window matching; the mixed IT/IoT testbed makes it messier.
- **CIC-IDS2017:** about 10 GB per day, and enterprise rather than IoT traffic.
- **Bot-IoT:** 69 GB.
- **UNSW-NB15:** about 100 GB.
- **Edge-IIoTset:** a good backup. Its official CSVs leak the label (arXiv 2608.15761), but our own NFStream features avoid that.

## Closest related work (state our difference honestly, "to our knowledge")
- Vitorino et al., "Revisiting Network Traffic Analysis: Compatible network flows for ML models", FPS 2025, arXiv 2511.08345. Re-extracts flows from the CICIoT23, IoT-23 and Bot-IoT pcaps. Offline only.
- HERA flow extractor, arXiv 2501.07475. Documents CICFlowMeter errors.
- arXiv 2401.16843. Maps NFStream features to CICFlowMeter and reports discrepancies.
- Sarhan et al., arXiv 2104.07183. Standard NIDS feature sets.
- Realguard, Sensors 2022 (PMC8778231). Lightweight IDS for IoT gateways; does not use NFStream.
- Engelen et al., IEEE SPW 2021 and CNS 2022. Labelling errors.
- **Our difference:** live extraction on an emulated gateway with replayed pcaps, a measured offline-vs-live gap, edge cost (latency, CPU, RAM), and NSGA-II feature selection.
