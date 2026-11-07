import pandas as pd
df = pd.read_parquet("/mnt/d/EdgeFlow-IDS/data/processed/iot23_flows.parquet")
print(df.shape); print([c for c in df.columns if not c.startswith(("bidirectional_","src2dst_","dst2src_"))])
print(df.source_file.value_counts())
print(df.groupby(["source_file","label"]).size())
for f,g in df.groupby("source_file"):
    print(f, "top src", g.src_ip.value_counts().head(3).to_dict(), "top dst", g.dst_ip.value_counts().head(3).to_dict())
