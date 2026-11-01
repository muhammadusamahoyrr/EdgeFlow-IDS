"""ARP-spoofing watcher for the gateway (flow features cannot see ARP).

Reads ARP replies and applies three rules:
  gateway_ip_spoof (high)        a reply binds a protected IP (the router) to a MAC other than
                                 its known MAC: the classic man-in-the-middle ARP spoof.
  ip_rebound_to_new_mac (info)   any IP announced by a different MAC than before.
  mac_claims_multiple_ips (info) one MAC announcing several IPs.
The two "info" rules are noisy in practice (devices with several addresses, DHCP changes), so
only "high" alerts are meant to trigger action. Alerts are JSON lines with the wall-clock time.

Live (as root, inside the gateway namespace):
  python -u arp_watch.py --iface gw-eth0 --out results/live/<tag>/arp_alerts.jsonl
Offline on a pcap (fresh state, same rules):
  python arp_watch.py --pcap file.pcap --out alerts.jsonl
"""
import argparse
import json
import re
import signal
import subprocess
import sys
import time

REPLY = re.compile(r"^(\d+\.\d+) .*Reply (\d+\.\d+\.\d+\.\d+) is-at ([0-9a-f:]{17})")
# Known router of the CIC-IoT2023 testbed (an operator knows their own gateway's MAC).
PROTECTED = {"192.168.137.1": "3c:18:a0:41:c3:a0"}


class ArpState:
    def __init__(self, protected=PROTECTED):
        self.protected = protected
        self.mac_ips, self.ip_mac, self.seen = {}, {}, set()

    def check(self, ip, mac):
        """Return new alerts (kind, severity, mac, detail) for one ARP reply."""
        out = []
        if ip in self.protected and mac != self.protected[ip]:
            out.append(("gateway_ip_spoof", "high", mac, [ip, self.protected[ip]]))
        old = self.ip_mac.get(ip)
        if old is not None and old != mac:
            out.append(("ip_rebound_to_new_mac", "info", mac, [ip, old]))
        self.ip_mac[ip] = mac
        self.mac_ips.setdefault(mac, set()).add(ip)
        if len(self.mac_ips[mac]) > 1:
            out.append(("mac_claims_multiple_ips", "info", mac, sorted(self.mac_ips[mac])))
        fresh = []
        for kind, sev, amac, detail in out:
            key = (kind, amac, tuple(detail) if kind != "mac_claims_multiple_ips" else ())
            if key not in self.seen:
                self.seen.add(key)
                fresh.append((kind, sev, amac, detail))
        return fresh


def run(cmd, out, live):
    state = ArpState()
    # SIGUSR1 = a new capture session (the live harness sends it between windows): forget bindings.
    signal.signal(signal.SIGUSR1, lambda *_: state.__init__())
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        with open(out, "a") as fh:
            for line in proc.stdout:
                m = REPLY.search(line)
                if not m:
                    continue
                ts, ip, mac = float(m.group(1)), m.group(2), m.group(3).lower()
                when = time.time() * 1000 if live else ts * 1000
                for kind, sev, amac, detail in state.check(ip, mac):
                    fh.write(json.dumps({"time_ms": when, "kind": kind, "severity": sev,
                                         "mac": amac, "detail": detail}) + "\n")
                    fh.flush()
        proc.wait()
    finally:
        proc.terminate()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--iface")
    ap.add_argument("--pcap")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    if a.pcap:
        run(["tcpdump", "-tt", "-n", "-e", "-r", a.pcap, "arp"], a.out, live=False)
    else:
        run(["tcpdump", "-tt", "-l", "-n", "-e", "-i", a.iface or "gw-eth0", "arp"], a.out, live=True)
