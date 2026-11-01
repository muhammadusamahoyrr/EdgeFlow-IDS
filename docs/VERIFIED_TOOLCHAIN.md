# Toolchain notes (researched 1 Nov 2026)

> **Pre-implementation notes, kept for history; superseded by `README.md`.** In the final setup: venv at `/opt/edgeflow` (`src/setup_venv.sh`), blocking with OVS drop rules (not iptables), a 200 packet/s ping ticker instead of packet-count early expiry, and the NFStream patch in `src/patch_nfstream.py`.

Sources were checked online before implementation. Items marked UNVERIFIED were later tested in the project.

## Mininet (WSL2, Ubuntu 24.04)
- Use the apt package: `mininet 2.3.0-1.1` (noble/universe). The Debian fix replaced distutils with `packaging`, so it works with Python 3.12.
  https://packages.ubuntu.com/noble/mininet
- Avoid `util/install.sh` from source on 24.04. It fails on pep8, PEP 668 and the OpenFlow reference build.
- The WSL2 kernel 6.6 here already loads `openvswitch` (checked locally), so no custom kernel is needed.

```bash
sudo apt update
sudo apt install -y mininet openvswitch-switch openvswitch-testcontroller tcpreplay iptables ethtool tcpdump
# every WSL boot:
sudo modprobe -a openvswitch sch_netem sch_htb sch_tbf
sudo service openvswitch-switch start      # no systemd: sudo /usr/share/openvswitch/scripts/ovs-ctl start
sudo ovs-vsctl show
sudo mn --switch ovsbr --controller none --test pingall
```
UNVERIFIED: whether systemd is enabled in this WSL image (check `/etc/wsl.conf`).

## NFStream
- Version 6.6.0 (Feb 2026). It needs Python ≥3.9, and a manylinux wheel exists for cp312.
  https://pypi.org/project/nfstream/
- Install it in a venv (PEP 668), and call the venv by its absolute path from Mininet hosts:

```bash
python3 -m venv ~/edgeflow && ~/edgeflow/bin/pip install nfstream scikit-learn pymoo pandas
```

- **Defaults:**
  - `idle_timeout=120`
  - `active_timeout=1800`
  - `statistical_analysis=False`
  - Setting `statistical_analysis=True` adds 48 features: packet-size and inter-arrival stats plus TCP flag counts, each for bidirectional, src2dst and dst2src.
  - API reference: https://www.nfstream.org/docs/api
- **Early classification:** in an `NFPlugin.on_update`, set `flow.expiration_id = -1` once `flow.bidirectional_packets >= N`.
- **Known issue:** idle timeouts do not fire in live capture when no packets arrive (issue #196). Use packet-count early expiry instead.
- **Where to apply drop rules:** in the main `for flow in streamer:` loop. Plugins run in meter processes.

## tcpreplay (replay through the gateway)
```bash
tcpprep --auto=bridge --pcap=in.pcap --cachefile=in.cache
tcprewrite -i in.pcap -o out.pcap -c in.cache --pnat=<old_cidr>:<new_cidr> \
  --enet-dmac=<gw-mac>,<gw-mac> --mtu=1500 --mtu-trunc --fixlen=pad --fixcsum
tcpreplay -i h1-eth0 -x 1.0 out.pcap      # real-time; keeps inter-arrival features honest
```
- **Gateway:**
  - `sysctl -w net.ipv4.ip_forward=1 net.ipv4.conf.all.rp_filter=0`
  - `ethtool -K <if> tx off rx off`
- **Replay speed:** don't use `--topspeed` for the offline-vs-live comparison, because it distorts inter-arrival times.

## Enforcement
- In the gateway namespace (recommended):
  `iptables -I FORWARD -p tcp -s A --sport p -d B --dport q -j DROP`
- Alternative on the switch:
  `ovs-ofctl add-flow s1 "priority=100,tcp,nw_src=A,nw_dst=B,tp_src=p,tp_dst=q,actions=drop"`

## NSGA-II (pymoo 0.6.2)
- Classes: `ElementwiseProblem`, `NSGA2(sampling=BinaryRandomSampling(), crossover=TwoPointCrossover(), mutation=BitflipMutation(), eliminate_duplicates=True)`.
- Objectives used in the end: `[1 - validation macro-F1, number of features, node count]` (see `results/nsga/summary.md`).
- Source: https://pymoo.org/customization/binary.html

## Related work to cite
- **Engelen, Rimmer, Joosen**, "Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study", IEEE SPW 2021. Covers flow-construction and labelling errors.
- **arXiv 2401.16843**, "Evaluating ML-Based Anomaly Detection Across Datasets of Varied Integrity". Maps NFStream features to CICFlowMeter and reports value discrepancies.
- **Rosay et al. 2022**, LycoSTand / LYCOS-IDS2017.
- **"Why are My Flows Different? A Tutorial on Flow Exporters"**, IEEE COMST: https://ieeexplore.ieee.org/document/9076310
- **NFStream + Mininet + live ML IDS:** a first quick search found none; the later deep search found about 15 NFStream + ML repos, none combining all parts of this project (see `docs/RELATED_WORK.md`).
