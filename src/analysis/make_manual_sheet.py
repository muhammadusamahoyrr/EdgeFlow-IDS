"""Blind sheet for a human check of the audit's undecided flows (reviewer round 13).

Draws 100 of the flows the amended rater left undetermined (U) in the strata where label and model
disagree (C: Benign label, one end is a listed attacker; D: Benign label, model flags an attack;
B-fn: attack label, model says Benign), seed 0. The sheet shows only what the program rater saw:
capture scenario, endpoints, ports, times, packet counts and payload heads. It hides the label,
the stratum, the model verdict and the rater's verdict. The key (row -> label, stratum) is a separate
file, to be opened only after rating.

The person rating fills `rating` with A (traffic of the capture's attack), B (benign) or U (cannot
tell), using the same rules as the program rater (docstring of label_audit.py).

Usage: python src/analysis/make_manual_sheet.py
Output: results/final/manual_check_sheet.csv, results/final/manual_check_key.csv
"""
import csv
import pathlib
import random

FINAL = pathlib.Path(__file__).resolve().parents[2] / "results" / "final"
N, SEED, STRATA = 100, 0, {"C", "D", "B-fn"}
SHOW = ["row", "source_file", "src_ip", "src_port", "dst_ip", "dst_port", "protocol", "first_seen_ms",
        "last_seen_ms", "packets_matched", "client_packets", "server_packets", "http_requests",
        "client_payload_head", "server_payload_head"]


def main():
    with open(FINAL / "label_audit_key.csv", newline="", encoding="utf-8") as f:
        key = {r[""]: r for r in csv.DictReader(f)}
    with open(FINAL / "label_audit_sample.csv", newline="", encoding="utf-8") as f:
        sample = {r["row"]: r for r in csv.DictReader(f)}
    pool = sorted(k for k, r in key.items() if r["stratum"] in STRATA and r["evidence"] == "U")
    pick = sorted(random.Random(SEED).sample(pool, min(N, len(pool))), key=int)
    with open(FINAL / "manual_check_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(SHOW + ["rating", "notes"])
        for k in pick:
            w.writerow([sample[k][c] for c in SHOW] + ["", ""])
    with open(FINAL / "manual_check_key.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["row", "label", "stratum", "scenario"])
        for k in pick:
            w.writerow([k, key[k]["label"], key[k]["stratum"], key[k]["scenario"]])
    print(f"pool {len(pool)} undecided flows in {sorted(STRATA)}; sheet {len(pick)} rows")


if __name__ == "__main__":
    main()
