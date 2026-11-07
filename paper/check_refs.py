"""Check that every \\cite key is defined in refs.bib, and list unused or TODO entries."""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BS = chr(92)  # backslash
bib = (HERE / "refs.bib").read_text(encoding="utf-8")
keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib))
cite = re.compile(re.escape(BS + "cite") + r"\{([^}]*)\}")
cited = set()
for tex in sorted((HERE / "sections").glob("*.tex")):
    for m in cite.finditer(tex.read_text(encoding="utf-8")):
        cited |= {k.strip() for k in m.group(1).split(",")}
print("cited:", len(cited), "| in bib:", len(keys))
print("cited but missing:", sorted(cited - keys))
print("in bib but never cited:", sorted(keys - cited))
print("bib entries with TODO:", re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,[^@]*TODO", bib))
