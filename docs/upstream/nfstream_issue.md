> Posted as https://github.com/nfstream/nfstream/issues/262 on 1 Nov 2026 (shortened version of this draft).

# Idle flows are exported late: `consume()` does not refresh the LRU position of updated flows

**NFStream version:** 6.6.0 (also current `master`; `nfstream/meter.py` last changed in 5481132, 2024-05-10)
**OS / Python:** Ubuntu 24.04 (WSL2, kernel 6.6), Python 3.12
**Mode:** reproduces offline (pcap) and in live capture

## Summary

`idle_timeout` is not respected while another, long-lived flow is active. An idle flow is only
exported after the long-lived flow is cut by `active_timeout`. With `idle_timeout=15` and
`active_timeout=120`, flows in a live capture were exported a median of **82.5 s** after their
last packet. With a one-line fix it is **15.6 s**. Flow features are not affected, only the time
of export (and, in live capture, whether a flow is exported at all before the capture stops).

This looks like the undiagnosed cause of #120 ("Completed flows expiring at active_timeout value
instead of idle_timeout"). It is different from #196 / #215 / PR #227, which concern the timer not
advancing when no packets arrive. Here packets keep arriving.

## Cause

`NFCache` is an LRU `OrderedDict`. Only `__setitem__` moves a key to the most-recent end
([meter.py L47-L49](https://github.com/nfstream/nfstream/blob/master/nfstream/meter.py#L47-L49)).

`meter_scan()` expires flows starting from the LRU head. It stops at the first flow that is not
idle ([L78-L96](https://github.com/nfstream/nfstream/blob/master/nfstream/meter.py#L78-L96)):

```python
flow_key = cache.get_lru_key()
...
else:
    remaining = False  # LRU flow is not yet idle.
```

In `consume()`, an existing flow is updated through a read, `cache[flow_key].update(...)`
([L195](https://github.com/nfstream/nfstream/blob/master/nfstream/meter.py#L195)). When the update
does not expire the flow, the code takes the branch at
[L256-L257](https://github.com/nfstream/nfstream/blob/master/nfstream/meter.py#L256-L257):

```python
        else:
            state = 0
```

There is no reassignment and no `move_to_end`. The cache order is therefore creation order, not
last-activity order. A long-lived active flow created early stays at the LRU head. Every idle scan
stops on it, and all idle flows behind it wait until that flow reaches `active_timeout`.

## Minimal reproduction (offline, standard library only)

A synthetic pcap with:

- flow **A**: one UDP packet per second for 200 s;
- flow **B**: two packets at t = 10 s and t = 11 s.

With `idle_timeout=15` and `active_timeout=120`, B should be exported at about t = 26 s, before
A's first segment (cut at t = 120 s).

<details><summary>nfstream_lru_repro.py</summary>

```python
import struct, tempfile
from nfstream import NFStreamer

def udp_packet(src, dst, sport, dport):
    payload = b"x" * 20
    udp = struct.pack("!HHHH", sport, dport, 8 + len(payload), 0) + payload
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), 0, 0, 64, 17, 0,
                     bytes(map(int, src.split("."))), bytes(map(int, dst.split("."))))
    c = sum(struct.unpack("!10H", ip)); c = (c >> 16) + (c & 0xFFFF); c = ~(c + (c >> 16)) & 0xFFFF
    ip = ip[:10] + struct.pack("!H", c) + ip[12:]
    return b"\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x02\x08\x00" + ip + udp

t0 = 1_700_000_000
pkts = [(t0 + s, udp_packet("10.0.0.1", "10.0.0.2", 1000, 2000)) for s in range(200)]
pkts += [(t0 + s, udp_packet("10.0.0.3", "10.0.0.4", 3000, 4000)) for s in (10, 11)]
pkts.sort(key=lambda p: p[0])
path = tempfile.mktemp(suffix=".pcap")
with open(path, "wb") as f:
    f.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    for ts, p in pkts:
        f.write(struct.pack("<IIII", ts, 0, len(p), len(p)) + p)

order = ["A" if fl.src_port == 1000 else "B"
         for fl in NFStreamer(source=path, idle_timeout=15, active_timeout=120, n_meters=1)]
print("export order:", " ".join(order))   # expected: B A A
```
</details>

**Output with 6.6.0:**

```
export order: A B A     <- B (idle since t = 11 s) is held back until A is cut at t = 120 s
```

**Output with the fix below:**

```
export order: B A A
```

## Proposed fix (one line)

```diff
         else:
+            cache.move_to_end(flow_key)
             state = 0
     except KeyError:  # create flow
```

`move_to_end` is O(1) on an `OrderedDict`. Flow features and flow boundaries do not change:
`NFlow.update()` already splits flows on idle and active timeouts itself. Only the export timing
changes.

## Measured effect in live capture

The measurement used two 60 s windows of CIC-IoT2023 traffic replayed with `tcpreplay` into a
Mininet host, with NFStream live capture (`n_meters=1`, `idle_timeout=15`, `active_timeout=120`,
`statistical_analysis=True`) and a 200 packet/s background flow.

| | Median export delay after a flow's last packet | Packets in exported flows (live / offline) |
|---|---|---|
| 6.6.0, window 1 | 82.5 s | 1.00 |
| 6.6.0, window 2 | 49.2 s | 0.65 (flows still unexported when the capture stopped) |
| patched, window 1 | 15.6 s | 1.00 |
| patched, window 2 | 15.5 s | 0.99 |

Measurement scripts and raw results:
https://github.com/muhammadusamahoyrr/EdgeFlow-IDS (see `results/nfstream_bug_check.md`,
`src/patch_nfstream.py`, `src/diag/nfstream_lru_repro.py`).

I am happy to open a PR with the fix and a regression test based on the reproduction above.
