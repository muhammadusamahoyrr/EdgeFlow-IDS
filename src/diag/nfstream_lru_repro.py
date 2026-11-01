"""Minimal, self-contained reproduction of the NFStream idle-expiry ordering bug (no extra packages).

Writes a tiny synthetic pcap:
  flow A: UDP 10.0.0.1:1000 -> 10.0.0.2:2000, one packet per second for 200 s (long-lived, active)
  flow B: UDP 10.0.0.3:3000 -> 10.0.0.4:4000, two packets at t=10 s and t=11 s (then idle)
With idle_timeout=15 and active_timeout=120, B is idle from t=26 s and should be exported then,
long before A's first active-timeout cut at t=120 s. NFStream reports the export order; the
script prints it and whether B was exported before the first segment of A.

Usage: python nfstream_lru_repro.py
"""
import struct
import tempfile

from nfstream import NFStreamer


def udp_packet(src, dst, sport, dport):
    payload = b"x" * 20
    udp = struct.pack("!HHHH", sport, dport, 8 + len(payload), 0) + payload
    total = 20 + len(udp)
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, total, 0, 0, 64, 17, 0,
                     bytes(map(int, src.split("."))), bytes(map(int, dst.split("."))))
    csum = sum(struct.unpack("!10H", ip))
    csum = (csum >> 16) + (csum & 0xFFFF)
    csum = ~(csum + (csum >> 16)) & 0xFFFF
    ip = ip[:10] + struct.pack("!H", csum) + ip[12:]
    eth = b"\x02\x00\x00\x00\x00\x01" + b"\x02\x00\x00\x00\x00\x02" + b"\x08\x00"
    return eth + ip + udp


def write_pcap(path):
    t0 = 1_700_000_000
    packets = [(t0 + s, udp_packet("10.0.0.1", "10.0.0.2", 1000, 2000)) for s in range(200)]
    packets += [(t0 + s, udp_packet("10.0.0.3", "10.0.0.4", 3000, 4000)) for s in (10, 11)]
    packets.sort(key=lambda p: p[0])
    with open(path, "wb") as f:
        f.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        for ts, pkt in packets:
            f.write(struct.pack("<IIII", ts, 0, len(pkt), len(pkt)) + pkt)


def main():
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as t:
        path = t.name
    write_pcap(path)
    order = []
    for flow in NFStreamer(source=path, idle_timeout=15, active_timeout=120, n_meters=1):
        name = "A" if flow.src_port == 1000 else "B"
        order.append(name)
        print(f"exported {name}: first_seen +{(flow.bidirectional_first_seen_ms - 1_700_000_000_000) / 1000:.0f} s, "
              f"last_seen +{(flow.bidirectional_last_seen_ms - 1_700_000_000_000) / 1000:.0f} s, "
              f"expiration_id {flow.expiration_id}")
    ok = order.index("B") < order.index("A")
    print("export order:", " ".join(order))
    print("EXPECTED (B exported before A's first segment):" if ok else
          "BUG: idle flow B was held back until A's active-timeout cut")


if __name__ == "__main__":
    main()
