"""Live experiment: replay the unseen windows through the emulated gateway.

h1 replays each window pcap (tcpreplay, original timing by default) into s1; an OVS rule sends
everything from h1 to the gateway, where gateway.py (flows) and arp_watch.py (ARP) capture on
gw-eth0. Between windows we wait --gap seconds while h1 pings h2 through the gateway at
200 packets/s, so idle flows keep expiring.

Resource use of the gateway processes (CPU %, RSS) is sampled every second from /proc.
--cpu-quota limits the gateway with a cgroup CPU quota (systemd-run), e.g. 100 = one core,
50 = half a core; without it the gateway shares the laptop's CPUs with tcpreplay and OVS.
--pin puts tcpreplay, the keep-alive ping and the gateway on disjoint cores (taskset), so the
achieved replay rate no longer depends on the gateway's load (needs >= 4 cores).

Run in WSL as root (system python3, which has mininet):
  python3 topology/live_experiment.py --tag run1 [--enforce] [--speed 1.0] [--cpu-quota 100]
      [--only Folder ...] [--model results/models/dt_nsga.pkl]
Output: results/live/<tag>/{flows.csv, windows.json, resources.csv, arp_alerts.jsonl,
        gateway.log, ovs_flows.txt}
"""
import argparse
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from mininet.log import setLogLevel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from edge_topo import build_net  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
VENV_PY = "/opt/edgeflow/bin/python"
IDLE_FLUSH_S = 20  # > NFStream idle_timeout (15 s)
CLK_TCK = os.sysconf("SC_CLK_TCK")
PAGE = os.sysconf("SC_PAGE_SIZE")


def ofport(intf_name):
    out = subprocess.run(["ovs-vsctl", "get", "Interface", intf_name, "ofport"],
                         capture_output=True, text=True, check=True)
    return int(out.stdout.strip())


def gateway_pids():
    out = subprocess.run(["pgrep", "-f", "src/gateway.py"], capture_output=True, text=True)
    return [int(p) for p in out.stdout.split()]


def sample_resources(path, stop_event):
    """CPU % (sum over gateway processes, 100 = one core) and RSS (MB), once per second."""
    prev = {}
    with open(path, "w") as fh:
        fh.write("time_ms,cpu_percent,rss_mb,n_procs\n")
        while not stop_event.is_set():
            t = time.time()
            ticks, rss, pids = 0, 0, gateway_pids()
            for pid in pids:
                try:
                    stat = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
                    ticks_now = int(stat[11]) + int(stat[12])  # utime + stime
                    rss += int(Path(f"/proc/{pid}/statm").read_text().split()[1]) * PAGE
                except (FileNotFoundError, ProcessLookupError, IndexError):
                    continue
                ticks += ticks_now - prev.get(pid, ticks_now)
                prev[pid] = ticks_now
            fh.write(f"{t * 1000:.0f},{100 * ticks / CLK_TCK:.1f},{rss / 2**20:.1f},{len(pids)}\n")
            fh.flush()
            stop_event.wait(1.0)


def wait_caught_up(log_path, quiet_s=5, timeout=600):
    """Wait until the gateway has caught up: neither NFStream's expired-flow counter nor the
    gateway's classified-flow counter has changed for quiet_s seconds. Returns seconds waited."""
    t0, last, still = time.time(), None, 0
    while time.time() - t0 < timeout:
        with open(log_path, "rb") as fh:
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - 8192))
            tail = fh.read().decode(errors="ignore")
        exp = re.findall(r'"flows_expired": (\d+)', tail)
        cls = re.findall(r"gateway: classified (\d+)", tail)
        now = (exp[-1] if exp else None, cls[-1] if cls else None)
        still = still + 1 if now == last else 0
        last = now
        if still >= quiet_s:
            return time.time() - t0
        time.sleep(1)
    raise RuntimeError(f"gateway did not catch up within {timeout} s, see {log_path}")


def wait_ready(log_path, proc, timeout=180):
    """Wait until the gateway has started capturing (it prints "gateway: ready")."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        if proc.poll() is not None:
            raise RuntimeError(f"gateway exited early, see {log_path}")
        if log_path.exists() and "gateway: ready" in log_path.read_text(errors="ignore"):
            return
        time.sleep(0.5)
    raise RuntimeError(f"gateway not ready after {timeout} s, see {log_path}")


def parse_rate(tcpreplay_out):
    m = re.search(r"Rated:\s*([\d.]+) Bps,\s*([\d.]+) Mbps,\s*([\d.]+) pps", tcpreplay_out)
    return {"offered_mbps": float(m.group(2)), "offered_pps": float(m.group(3))} if m else {}


PIN_REPLAY, PIN_PING, PIN_GW = "0", "1", "2-5"


def main(tag, enforce, speed, gap, cpu_quota, only, model, policy, pin=False):
    live = ROOT / "data" / "raw" / "live"
    windows = json.loads((live / "manifest.json").read_text())
    if only:
        windows = [w for w in windows if w["folder"] in only]
    out_dir = ROOT / "results" / "live" / tag
    out_dir.mkdir(parents=True, exist_ok=True)

    net = build_net()
    h1, gw = net["h1"], net["gw"]
    procs, stop_event = [], threading.Event()
    try:
        # Jumbo MTU on the replay path: some captured frames exceed 1500 bytes (offloaded segments).
        for node, intf in ((h1, "h1-eth0"), (gw, "gw-eth0")):
            node.cmd(f"ip link set {intf} mtu 9000")
        for intf in net["s1"].intfList():
            if intf.name != "lo":
                subprocess.run(["ip", "link", "set", intf.name, "mtu", "9000"], check=True)

        # The replayed frames carry many device MACs as source, so a learning switch would map
        # them all to h1's port and never forward frames addressed to them. Send everything that
        # enters from h1 straight to the gateway (enforcement drop rules use a higher priority).
        s1 = net["s1"]
        h1_port = ofport(s1.connectionsTo(h1)[0][0].name)
        gw_port = ofport(s1.connectionsTo(gw)[0][0].name)
        subprocess.run(["ovs-ofctl", "add-flow", "s1",
                        f"priority=10,in_port={h1_port},actions=output:{gw_port}"], check=True)

        cmd = [VENV_PY, "-u", str(ROOT / "src" / "gateway.py"), "--iface", "gw-eth0",
               "--out", str(out_dir / "flows.csv"), "--model", str(model)]
        if enforce:
            cmd += ["--enforce", "--bridge", "s1", "--policy", policy]
        if pin:  # NFStream meter processes inherit the affinity
            cmd = ["taskset", "-c", PIN_GW] + cmd
        if cpu_quota:
            cmd = ["systemd-run", "--scope", "--quiet", "-p", f"CPUQuota={cpu_quota}%"] + cmd
        log = open(out_dir / "gateway.log", "w")
        procs.append(gw.popen(cmd, cwd=str(ROOT / "src"), stdout=log, stderr=log))
        arp_log = open(out_dir / "arp_watch.log", "w")
        procs.append(gw.popen([VENV_PY, "-u", str(ROOT / "src" / "arp_watch.py"), "--iface",
                               "gw-eth0", "--out", str(out_dir / "arp_alerts.jsonl")],
                              cwd=str(ROOT / "src"), stdout=arp_log, stderr=arp_log))
        threading.Thread(target=sample_resources, args=(out_dir / "resources.csv", stop_event),
                         daemon=True).start()
        wait_ready(out_dir / "gateway.log", procs[0])
        ping_pin = f"taskset -c {PIN_PING} " if pin else ""
        replay_pin = f"taskset -c {PIN_REPLAY} " if pin else ""
        h1.cmd(f"{ping_pin}ping -i 0.005 -q 10.0.2.10 > /dev/null 2>&1 &")

        record = []
        for wdw in windows:
            pcap = live / wdw["pcap"]
            t0 = time.time()
            res = h1.cmd(f"{replay_pin}tcpreplay -i h1-eth0 -x {speed} {shlex.quote(str(pcap))} 2>&1")
            t1 = time.time()
            rate = parse_rate(res)
            if not rate:
                raise RuntimeError(f"tcpreplay failed for {pcap.name}: {res.strip()[-300:]}")
            print(f"{wdw['folder']}: replayed in {t1 - t0:.1f} s {rate}")
            time.sleep(gap)
            # Wait until the gateway has classified everything from this window (under load it
            # can lag behind), so no verdict or block of this window spills into the next one.
            caught_up = wait_caught_up(out_dir / "gateway.log")
            record.append({**wdw, "replay_start_ms": t0 * 1000, "replay_end_ms": t1 * 1000,
                           "caught_up_after_gap_s": round(caught_up, 1),
                           **rate, "tcpreplay": res.strip()[-600:]})
            # Each window is a different capture session reusing the same IPs: save this window's
            # drop-rule counters, then clear blocks, votes and ARP state before the next window.
            dump = subprocess.run(["ovs-ofctl", "dump-flows", "s1"], capture_output=True, text=True)
            (out_dir / f"ovs_flows_{wdw['folder']}.txt").write_text(dump.stdout)
            if enforce:
                # Non-strict match "ip" removes only the IP drop rules; the h1->gw forwarding rule
                # (in_port only) and the NORMAL rule have no IP match and stay.
                subprocess.run(["ovs-ofctl", "del-flows", "s1", "ip"], check=True)
            for p in procs:
                p.send_signal(signal.SIGUSR1)
        time.sleep(IDLE_FLUSH_S)

        meta = {"tag": tag, "enforce": enforce, "policy": policy if enforce else None,
                "speed": speed, "cpu_quota": cpu_quota, "pinned": pin, "model": str(model), "windows": record}
        (out_dir / "windows.json").write_text(json.dumps(meta, indent=2))
        dump = subprocess.run(["ovs-ofctl", "dump-flows", "s1"], capture_output=True, text=True)
        (out_dir / "ovs_flows.txt").write_text(dump.stdout)
    finally:
        h1.cmd("pkill -f 'ping -i 0.005 -q 10.0.2.10'")
        for p in procs:
            p.terminate()
        for p in procs:
            try:
                p.wait(timeout=120)  # the gateway still classifies its last batch and moves the CSV
            except subprocess.TimeoutExpired:
                p.kill()
        stop_event.set()
        # NFStream meters run as child processes that outlive the parent: stop them too.
        subprocess.run(["pkill", "-f", "src/gateway.py"], check=False)
        subprocess.run(["pkill", "-f", "src/arp_watch.py"], check=False)
        net.stop()
    print(f"done: {out_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--enforce", action="store_true")
    ap.add_argument("--speed", type=float, default=1.0, help="tcpreplay -x multiplier")
    ap.add_argument("--gap", type=int, default=30, help="seconds between windows")
    ap.add_argument("--cpu-quota", type=int, default=None, help="cgroup CPU quota in percent")
    ap.add_argument("--only", nargs="*", default=None, help="replay only these folders")
    ap.add_argument("--model", default=str(ROOT / "results" / "models" / "decision_tree.pkl"))
    ap.add_argument("--policy", default=str(ROOT / "results" / "block_policy.json"),
                    help='blocking policy for --enforce, or "none" (block on first verdict)')
    ap.add_argument("--pin", action="store_true",
                    help="pin tcpreplay, ping and gateway to disjoint cores")
    a = ap.parse_args()
    setLogLevel("warning")
    main(a.tag, a.enforce, a.speed, a.gap, a.cpu_quota, a.only, a.model, a.policy, a.pin)
