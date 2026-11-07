"""Management-subnet filter and the NFStream LRU patch script."""
import subprocess
import sys
from pathlib import Path

import pytest

from config import is_mgmt

PATCH = Path(__file__).resolve().parents[1] / "src" / "patch_nfstream.py"

METER_UNPATCHED = """def consume(cache, flow_key):
    try:
        if cache[flow_key].expired:
            state = 1
        else:
            state = 0
    except KeyError:  # create flow
        state = 2
"""


@pytest.mark.parametrize("ip,expected", [
    ("10.0.1.10", True), ("10.0.2.10", True), ("10.0.1.1", True),
    ("10.0.3.5", False), ("10.0.25.1", False),  # matched the old "10.0." prefix
    ("192.168.137.1", False), ("not-an-ip", False), ("", False),
])
def test_is_mgmt(ip, expected):
    assert is_mgmt(ip) is expected


def patch(tmp_path, *args):
    env_path = str(tmp_path)
    return subprocess.run([sys.executable, str(PATCH), *args], capture_output=True, text=True,
                          env={"PYTHONPATH": env_path, "PATH": ""})


@pytest.fixture
def fake_nfstream(tmp_path):
    pkg = tmp_path / "nfstream"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('__version__ = "6.6.0"\n')
    (pkg / "meter.py").write_text(METER_UNPATCHED)
    return pkg / "meter.py"


def test_patch_applies_once_and_reverts(tmp_path, fake_nfstream):
    r = patch(tmp_path)
    assert r.returncode == 0 and "patched" in r.stdout
    text = fake_nfstream.read_text()
    assert text.count("cache.move_to_end(flow_key)") == 1
    assert "already patched" in patch(tmp_path).stdout
    assert fake_nfstream.read_text() == text
    patch(tmp_path, "--revert")
    assert fake_nfstream.read_text() == METER_UNPATCHED


def test_patch_refuses_unknown_code(tmp_path, fake_nfstream):
    fake_nfstream.write_text("def consume():\n    pass\n")
    r = patch(tmp_path)
    assert r.returncode != 0 and "pattern not found" in r.stderr
