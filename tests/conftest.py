"""Test setup: put src/ on the import path and stub NFStream.

The unit tests cover pure logic (blocking votes, ARP rules, the subnet filter, the NFStream
patch script), so they do not need NFStream, libpcap, Mininet or root. gateway.py imports
NFStreamer at module level; a stub stands in for it.
"""
import sys
import types
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

if "nfstream" not in sys.modules:
    stub = types.ModuleType("nfstream")
    stub.NFStreamer = object
    sys.modules["nfstream"] = stub
