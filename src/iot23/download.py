"""Resumable download of the chosen IoT-23 scenarios (pcap + Zeek conn.log.labeled).

Source: Stratosphere Lab, IoT-23 (Garcia, Parmisano, Erquiaga; doi 10.5281/zenodo.4743746),
individual scenarios at BASE/<scenario>/. Scenarios were chosen by size (pcap < 400 MB; the
Okiru/"Attack" captures are all >= 1 GB and are left out) and label coverage. Honeypot
7-1 is split into Somfy-01..06; only Somfy-01 has a labelled conn log on the server.
A partial file is resumed with an HTTP Range request; a finished file (size equals the server's
Content-Length) is skipped. A compressed pcap (.xz) is unpacked next to it.

Usage: python src/iot23/download.py [--logs-only]
Output: data/raw/iot23/<scenario>/{<pcap>, conn.log.labeled}, data/raw/iot23/sizes.csv
"""
import argparse
import lzma
import pathlib
import shutil
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

from config import RAW  # noqa: E402

BASE = "https://mcfp.felk.cvut.cz/publicDatasets/IoT-23-Dataset/IndividualScenarios"
OUT = RAW / "iot23"

# scenario folder (local name) -> (remote folder, pcap file, malware family = file label)
SCENARIOS = {
    "CTU-Honeypot-Capture-4-1": ("CTU-Honeypot-Capture-4-1", "2018-10-25-14-06-32-192.168.1.132.pcap.xz", "Benign"),
    "CTU-Honeypot-Capture-5-1": ("CTU-Honeypot-Capture-5-1", "2018-09-21-capture.pcap", "Benign"),
    "CTU-Honeypot-Capture-7-1-Somfy-01": ("CTU-Honeypot-Capture-7-1/Somfy-01", "2019-07-03-15-15-47-first_start_somfy_gateway.pcap", "Benign"),
    "CTU-IoT-Malware-Capture-1-1": ("CTU-IoT-Malware-Capture-1-1", "2018-05-09-192.168.100.103.pcap", "Hide&Seek"),
    "CTU-IoT-Malware-Capture-3-1": ("CTU-IoT-Malware-Capture-3-1", "2018-05-21_capture.pcap", "Muhstik"),
    "CTU-IoT-Malware-Capture-8-1": ("CTU-IoT-Malware-Capture-8-1", "2018-07-31-15-15-09-192.168.100.113.pcap", "Hakai"),
    "CTU-IoT-Malware-Capture-20-1": ("CTU-IoT-Malware-Capture-20-1", "2018-10-02-13-12-30-192.168.100.103.pcap", "Torii"),
    "CTU-IoT-Malware-Capture-21-1": ("CTU-IoT-Malware-Capture-21-1", "2018-10-03-15-22-32-192.168.100.113.pcap", "Torii"),
    "CTU-IoT-Malware-Capture-34-1": ("CTU-IoT-Malware-Capture-34-1", "2018-12-21-15-50-14-192.168.1.195.pcap", "Mirai"),
    "CTU-IoT-Malware-Capture-42-1": ("CTU-IoT-Malware-Capture-42-1", "2019-01-10-14-34-38-192.168.1.197.pcap", "Trojan"),
}


def fetch(url, dest):
    """Download url to dest, resuming a partial file. Returns the final size in bytes."""
    with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60) as r:
        total = int(r.headers["Content-Length"])
    have = dest.stat().st_size if dest.exists() else 0
    if have == total:
        return total
    if have > total:
        dest.unlink()
        have = 0
    req = urllib.request.Request(url, headers={"Range": f"bytes={have}-"} if have else {})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "ab" if have else "wb") as f:
        if have and r.status != 206:  # server ignored the Range header: start over
            f.seek(0)
            f.truncate()
        shutil.copyfileobj(r, f, length=1 << 20)
    size = dest.stat().st_size
    if size != total:
        raise IOError(f"{dest}: got {size} of {total} bytes (run again to resume)")
    return size


def main(logs_only):
    rows = []
    for name, (remote, pcap, family) in SCENARIOS.items():
        d = OUT / name
        d.mkdir(parents=True, exist_ok=True)
        files = [("bro/conn.log.labeled", "conn.log.labeled")]
        if not logs_only:
            files.append((pcap, pcap))
        for rel, local in files:
            size = fetch(f"{BASE}/{remote}/{rel}", d / local)
            print(f"{name}/{local}: {size / 1e6:.1f} MB")
            rows.append(f"{name},{local},{family},{size}")
        xz = d / pcap
        if pcap.endswith(".xz") and xz.exists() and not xz.with_suffix("").exists():
            with lzma.open(xz) as src, open(xz.with_suffix(""), "wb") as dst:
                shutil.copyfileobj(src, dst)
            print(f"unpacked {xz.with_suffix('').name}")
    (OUT / "sizes.csv").write_text("scenario,file,family,bytes\n" + "\n".join(rows) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs-only", action="store_true", help="download only the Zeek logs")
    main(ap.parse_args().logs_only)
