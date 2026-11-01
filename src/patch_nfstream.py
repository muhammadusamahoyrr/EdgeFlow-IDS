"""Patch NFStream 6.6.0's flow cache so idle flows are exported on time in live capture.

Bug: NFCache is an LRU (OrderedDict) and meter_scan() expires flows starting from the LRU end,
stopping at the first non-idle flow. But when a packet UPDATES an existing flow, meter.py does
not move that flow to the MRU end. A long-lived, still-active flow therefore stays at the LRU
head forever, the scan stops on it, and every idle flow behind it waits until that flow hits
active_timeout. Observed here: verdicts ~70 s after a flow's last packet with idle_timeout=15 s.

Fix: move the updated flow to the MRU end. Flow boundaries and features are unchanged
(update() itself splits flows on idle gaps), only the export time is corrected.

Usage (as root): /opt/edgeflow/bin/python src/patch_nfstream.py   (idempotent; --revert undoes it)
Before/after measurement: src/run_bug_check.sh -> results/nfstream_bug_check.md
"""
import sys
from pathlib import Path

import nfstream

METER = Path(nfstream.__file__).parent / "meter.py"
OLD = """        else:
            state = 0
    except KeyError:  # create flow"""
NEW = """        else:
            cache.move_to_end(flow_key)  # EdgeFlow-IDS patch: keep LRU order on update
            state = 0
    except KeyError:  # create flow"""

src = METER.read_text()
if "--revert" in sys.argv:  # restore the original code (used once to measure the bug's effect)
    METER.write_text(src.replace(NEW, OLD))
    print(f"reverted: {METER}")
elif "EdgeFlow-IDS patch" in src:
    print(f"already patched: {METER}")
elif src.count(OLD) == 1:
    METER.write_text(src.replace(OLD, NEW))
    print(f"patched: {METER} (nfstream {nfstream.__version__})")
else:
    raise SystemExit(f"pattern not found exactly once in {METER}; NFStream version changed?")
