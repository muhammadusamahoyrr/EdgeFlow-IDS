"""Download the official CIC-IoT2023 per-pcap CSV files for the ten captures this project uses.

The dataset ships one CSV per pcap (`CSV/CSV/<Folder>/<file>.pcap.csv`) with its own
packet-window features and a file-level label. We fetch exactly the files that match
data/raw/cic-iot2023/<Folder>/<file>.pcap, to compare our evidence-based pipeline with the
benchmark as distributed.

Usage: python src/analysis/download_official_csv.py
Output: data/raw/official_csv/<Folder>/<file>.pcap.csv
"""
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

from config import FOLDER_TO_CLASS, RAW  # noqa: E402

BASE = "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV"


def main():
    for pcap in sorted((RAW / "cic-iot2023").rglob("*.pcap")):
        folder = pcap.parent.name
        if folder not in FOLDER_TO_CLASS:
            continue
        out = RAW / "official_csv" / folder / (pcap.name + ".csv")
        if out.exists():
            print("skip", out.name)
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        url = f"{BASE}/{folder}/{pcap.name}.csv"
        tmp = out.with_suffix(".part")
        print("get", url)
        urllib.request.urlretrieve(url, tmp)
        tmp.rename(out)
        print("  ->", out, round(out.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
