"""Cut one unseen time window per pcap for the live experiment.

For each source pcap the window starts 1 s after the last TRAINING flow started (from the saved
model's train_cutoff_ms) and lasts --seconds. Packets are selected by epoch time with tshark, so
there is no timezone ambiguity.

Usage: python src/make_live_windows.py [--seconds 60]
Output: data/raw/live/<Folder>__<file>.pcap and data/raw/live/manifest.json
"""
import argparse
import json
import pickle
import subprocess

from config import RAW, RESULTS
from extract_flows import source_for


def main(seconds):
    # Trusted input: the model file is produced locally by train_edge_model.py.
    with open(RESULTS / "models" / "decision_tree.pkl", "rb") as f:
        bundle = pickle.load(f)
    out_dir = RAW / "live"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for source_file, cutoff_ms in sorted(bundle["train_cutoff_ms"].items()):
        folder, name = source_file.split("/")
        src = source_for(RAW / "cic-iot2023" / folder / name)
        start = cutoff_ms / 1000 + 1
        end = start + seconds
        out = out_dir / f"{folder}__{name}"
        flt = f"frame.time_epoch >= {start:.3f} && frame.time_epoch < {end:.3f}"
        subprocess.run(["tshark", "-r", str(src), "-Y", flt, "-w", str(out)],
                       check=True, stderr=subprocess.DEVNULL)
        n = subprocess.run(["capinfos", "-c", "-M", str(out)], capture_output=True, text=True).stdout
        packets = int(n.strip().splitlines()[-1].split()[-1])
        print(f"{source_file}: window {start:.0f}-{end:.0f} -> {packets:,} packets")
        manifest.append({"folder": folder, "source_file": source_file, "pcap": out.name,
                         "start_epoch": start, "end_epoch": end, "packets": packets})
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"manifest: {out_dir / 'manifest.json'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=60)
    main(ap.parse_args().seconds)
