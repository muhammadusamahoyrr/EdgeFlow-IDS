"""ARP-spoofing watcher for the gateway (flow features cannot see ARP).

Reads ARP replies and requests and applies three rules to each (IP, MAC) binding they announce:
  gateway_ip_spoof (high)        a protected IP (the router) is announced by a MAC other than its
                                 known MAC: the classic man-in-the-middle ARP spoof.
  ip_rebound_to_new_mac (info)   any IP announced by a different MAC than before.
  mac_claims_multiple_ips (info) one MAC announcing several IPs.
The two "info" rules are noisy in practice (devices with several addresses, DHCP changes), so
only "high" alerts are meant to trigger action. Alerts are JSON lines with the wall-clock time.

A reply announces "IP is-at MAC". A request announces its sender: "who-has X tell IP", sent from
the Ethernet source MAC; spoofers also poison caches this way (gratuitous or forged requests).
Probes (sender IP 0.0.0.0) announce nothing. --replies-only restores the rule used for the paper
(tag v1.0-paper), which read replies only.

The protected bindings default to the CIC-IoT2023 testbed router; set your own with
--protect IP=MAC (repeatable).

Live (as root, inside the gateway namespace):
  python -u arp_watch.py --iface gw-eth0 --out results/live/<tag>/arp_alerts.jsonl       [--protect 192.168.1.1=aa:bb:cc:dd:ee:ff]
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

REPLY = re.compile(r"^(\d+\.\d+) .*Reply (\d+\.\d+\.\d+\.\d+) is-at ([0-9a-fA-F:]{17})")
REQUEST = re.compile(
    r"^(\d+\.\d+) ([0-9a-fA-F:]{17}) > .*Request who-has .* tell (\d+\.\d+\.\d+\.\d+)")
# Known router of the CIC-IoT2023 testbed (an operator knows their own gateway's MAC).
PROTECTED = {"192.168.137.1": "3c:18:a0:41:c3:a0"}


def parse_line(line, replies_only=False):
    """Return (timestamp_s, ip, mac) for the binding an ARP line (tcpdump -tt -n -e) announces,
    or None."""
    m = REPLY.search(line)
    if m:
        return float(m.group(1)), m.group(2), m.group(3).lower()
    if replies_only:
        return None
    m = REQUEST.search(line)
    if m and m.group(3) != "0.0.0.0":
        return float(m.group(1)), m.group(3), m.group(2).lower()
    return None


def parse_protect(items):
    """["IP=MAC", ...] -> {ip: mac}; None or empty gives the default."""
    if not items:
        return dict(PROTECTED)
    out = {}
    for item in items:
        ip, sep, mac = item.partition("=")
        ip_ok = re.fullmatch(r"\d+\.\d+\.\d+\.\d+", ip)
        mac_ok = re.fullmatch(r"[0-9a-f]{2}(:[0-9a-f]{2}){5}", mac.lower())
        if not (sep and ip_ok and mac_ok):
            raise ValueError(f"--protect expects IP=MAC, got {item!r}")
        out[ip] = mac.lower()
    return out


class ArpState:
    def __init__(self, protected=PROTECTED):
        self.protected = protected
        self.mac_ips, self.ip_mac, self.seen = {}, {}, set()

    def check(self, ip, mac):
        """Return new alerts (kind, severity, mac, detail) for one announced binding."""
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


def run(cmd, out, live, protected=None, replies_only=False):
    protected = protected or dict(PROTECTED)
    state = ArpState(protected)
    # SIGUSR1 = a new capture session (the live harness sends it between windows): forget bindings.
    signal.signal(signal.SIGUSR1, lambda *_: state.__init__(protected))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        with open(out, "a") as fh:
            for line in proc.stdout:
                parsed = parse_line(line, replies_only)
                if parsed is None:
                    continue
                ts, ip, mac = parsed
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
    ap.add_argument("--protect", action="append", metavar="IP=MAC",
                    help="known binding of a protected IP, e.g. the router (repeatable); "
                         "default: the CIC-IoT2023 testbed router")
    ap.add_argument("--replies-only", action="store_true",
                    help="read ARP replies only (the rule used for the paper, tag v1.0-paper)")
    a = ap.parse_args()
    try:
        prot = parse_protect(a.protect)
    except ValueError as e:
        ap.error(str(e))
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    if a.pcap:
        run(["tcpdump", "-tt", "-n", "-e", "-r", a.pcap, "arp"], a.out, live=False,
            protected=prot, replies_only=a.replies_only)
    else:
        run(["tcpdump", "-tt", "-l", "-n", "-e", "-i", a.iface or "gw-eth0", "arp"], a.out,
            live=True, protected=prot, replies_only=a.replies_only)
