"""EdgeFlow-IDS gateway: live flow extraction (NFStream) + classification + optional blocking.

Runs inside the Mininet gateway's network namespace.
- Flows exported by NFStream are queued and classified in micro-batches: a batch is closed when it
  has --batch flows, or by a timer thread --max-wait-ms after its first flow, so a quiet network
  never leaves verdicts waiting.
- Per flow the CSV stores identifiers, packet/byte counts, the prediction, recv_ms (flow handed
  over by NFStream), verdict_ms (prediction done), batch_ms (whole-batch predict time) and the
  batch size. Feature values are not written (keeps the hot path short).
- Flows of the testbed's management subnet (config.MGMT_NETS, the ping ticker) are never scored
  or blocked.
- With --enforce, a host pair is blocked (OVS drop rules for both directions on the access switch,
  so later packets of that pair never reach the gateway) once it has collected k attack verdicts.
  k and whether MITM-ARP flow verdicts count come from --policy (default results/block_policy.json,
  chosen on validation data by tune_block_policy.py); --policy none blocks on the first verdict.
- The CSV is written to local /tmp and moved to --out atomically on exit (SIGTERM or end).

Usage (as root, inside the gateway namespace):
  python -u gateway.py --iface gw-eth0 --out results/live/<tag>/flows.csv [--enforce --bridge s1]
"""
import argparse
import csv
import json
import os
import pickle
import shutil
import signal
import subprocess
import threading
import time

import numpy as np
from nfstream import NFStreamer

from config import RESULTS, STREAMER_KW, is_mgmt

ID_FIELDS = ["src_ip", "dst_ip", "src_port", "dst_port", "protocol", "src_mac", "dst_mac",
             "bidirectional_first_seen_ms", "bidirectional_last_seen_ms",
             "bidirectional_packets", "bidirectional_bytes"]


def block_pair(bridge, a, b):
    for src, dst in ((a, b), (b, a)):
        rule = f"priority=100,ip,nw_src={src},nw_dst={dst},actions=drop"
        subprocess.run(["ovs-ofctl", "add-flow", bridge, rule], check=False)


def stop(*_):
    raise SystemExit(0)


class Classifier:
    def __init__(self, model, feats, writer, enforce, bridge, batch_size, max_wait_ms, policy):
        self.model, self.feats, self.w = model, feats, writer
        self.enforce, self.bridge = enforce, bridge
        self.batch_size, self.max_wait = batch_size, max_wait_ms / 1000
        self.k = policy.get("min_attack_verdicts", 1)
        self.ignore_mitm = policy.get("ignore_mitm_flow_verdicts", False)
        self.lock = threading.RLock()
        self.ids, self.rows, self.recv = [], [], []
        self.t_first = None
        self.blocked, self.votes = set(), {}
        self.n_classified = 0

    def add(self, flow):
        with self.lock:
            self.ids.append([getattr(flow, f) for f in ID_FIELDS])
            self.rows.append([getattr(flow, f) for f in self.feats])
            self.recv.append(time.time() * 1000)
            if self.t_first is None:
                self.t_first = time.perf_counter()
            if len(self.rows) >= self.batch_size:
                self.flush()

    def reset(self):
        """Forget blocks and votes (the experiment harness sends SIGUSR1 between windows, because
        each window comes from a different capture session that reuses the same IP addresses)."""
        with self.lock:
            self.blocked.clear()
            self.votes.clear()

    def flush(self):
        # A SIGTERM arriving mid-batch would lose the rest of the batch: defer it until done.
        main = threading.current_thread() is threading.main_thread()
        if main:
            signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM})
        try:
            self._flush()
        finally:
            if main:
                signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGTERM})

    def _flush(self):
        with self.lock:
            if not self.rows:
                return
            # Take the batch first, so an interrupted flush can never write rows twice.
            ids, rows, recv = self.ids, self.rows, self.recv
            self.ids, self.rows, self.recv, self.t_first = [], [], [], None
            X = np.asarray(rows, dtype=np.float32)
            t0 = time.perf_counter()
            preds = self.model.predict(X)
            batch_ms = (time.perf_counter() - t0) * 1000
            verdict_ms = time.time() * 1000
            for idv, r_ms, pred in zip(ids, recv, preds):
                blocked_now = 0
                pair = tuple(sorted((idv[0], idv[1])))
                counts = pred != "Benign" and not (self.ignore_mitm and pred == "MITM-ARP")
                if self.enforce and counts and pair not in self.blocked:
                    self.votes[pair] = self.votes.get(pair, 0) + 1
                    if self.votes[pair] >= self.k:
                        block_pair(self.bridge, *pair)
                        self.blocked.add(pair)
                        blocked_now = 1
                self.w.writerow(idv + [pred, f"{r_ms:.1f}", f"{verdict_ms:.1f}",
                                       f"{batch_ms:.4f}", len(rows), blocked_now])
            self.n_classified += len(rows)

    def heartbeat(self):
        """Print the number of classified flows every second, so the experiment harness can wait
        until the gateway has caught up before it closes a window."""
        while True:
            time.sleep(1)
            print(f"gateway: classified {self.n_classified}", flush=True)

    def timer(self):
        while True:
            time.sleep(self.max_wait / 2)
            with self.lock:
                if self.t_first is not None and time.perf_counter() - self.t_first >= self.max_wait:
                    self.flush()


def main(iface, out, enforce, bridge, model_path, batch_size, max_wait_ms, socket_buffer,
         policy_path):
    # Trusted input: the model file is produced locally by train_edge_model.py.
    with open(model_path, "rb") as f:
        bundle = pickle.load(f)
    signal.signal(signal.SIGTERM, stop)

    local = f"/tmp/edgeflow_gateway_{os.getpid()}.csv"
    fh = open(local, "w", newline="", buffering=1 << 20)
    w = csv.writer(fh)
    w.writerow(ID_FIELDS + ["pred", "recv_ms", "verdict_ms", "batch_ms", "batch_size",
                            "blocked_now"])
    policy = (json.loads(open(policy_path).read())
              if enforce and policy_path != "none" else {})
    if enforce:
        print(f"gateway: blocking policy {policy or 'block on first attack verdict'}", flush=True)
    clf = Classifier(bundle["model"], bundle["features"], w, enforce, bridge, batch_size,
                     max_wait_ms, policy)
    threading.Thread(target=clf.timer, daemon=True).start()
    threading.Thread(target=clf.heartbeat, daemon=True).start()
    signal.signal(signal.SIGUSR1, lambda *_: clf.reset())

    # One meter: NFStream checks a meter's timeouts only when that meter receives a packet, so
    # with several meters idle flows can stay stuck in quiet meters. One core also suits an edge box.
    # performance_report prints NFStream's packet/drop counters every second (to gateway.log).
    streamer = NFStreamer(source=iface, n_meters=1, socket_buffer_size=socket_buffer,
                          performance_report=1, **STREAMER_KW)
    print("gateway: ready", flush=True)
    try:
        for flow in streamer:
            if is_mgmt(flow.src_ip) or is_mgmt(flow.dst_ip):
                continue
            clf.add(flow)
    finally:
        clf.flush()
        fh.close()
        shutil.copy(local, out + ".tmp")
        os.replace(out + ".tmp", out)
        os.remove(local)
        print(f"gateway: wrote {out}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--iface", default="gw-eth0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--enforce", action="store_true")
    ap.add_argument("--bridge", default="s1")
    ap.add_argument("--model", default=str(RESULTS / "models" / "decision_tree.pkl"))
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--max-wait-ms", type=float, default=50)
    ap.add_argument("--socket-buffer", type=int, default=64 << 20, help="capture buffer, bytes")
    ap.add_argument("--policy", default=str(RESULTS / "block_policy.json"),
                    help='blocking policy JSON, or "none" to block on the first attack verdict')
    a = ap.parse_args()
    main(a.iface, a.out, a.enforce, a.bridge, a.model, a.batch, a.max_wait_ms, a.socket_buffer,
         a.policy)
