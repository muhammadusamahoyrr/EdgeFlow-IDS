"""IoT-23: attack vs background (Benign) flows per scenario, by the dataset's own Zeek labels.

Usage: python src/iot23/label_shares.py
Output: results/iot23/label_shares.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import pandas as pd  # noqa: E402

from config import PROCESSED, RESULTS  # noqa: E402


def main():
    df = pd.read_parquet(PROCESSED / "iot23_flows.parquet", columns=["source_file", "family", "label"])
    df["scenario"] = df.source_file.str.split("/").str[0]
    t = (df.assign(is_attack=df.label != "Benign")
           .groupby(["scenario", "family"])
           .agg(flows=("label", "size"), attack_flows=("is_attack", "sum")))
    t["background_flows"] = t.flows - t.attack_flows
    t["background_share"] = (t.background_flows / t.flows).round(3)
    classes = pd.crosstab([df.scenario, df.family], df.label)
    md = ["# IoT-23: attack vs background flows per scenario (Zeek labels)", "",
          "NFStream flows matched to a Zeek connection (src/iot23/extract_label.py); background = "
          "Zeek label Benign.", "",
          t.reset_index().to_markdown(index=False), "",
          "Flows per class:", "", classes.reset_index().to_markdown(index=False)]
    (RESULTS / "iot23" / "label_shares.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
