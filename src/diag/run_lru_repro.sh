#!/usr/bin/env bash
# Run the minimal NFStream repro with the original and the patched meter.py (run as root in WSL).
cd "$(dirname "$0")"
PY=/opt/edgeflow/bin/python
echo "=== original NFStream 6.6.0"; $PY ../patch_nfstream.py --revert > /dev/null; $PY nfstream_lru_repro.py
echo "=== patched";                  $PY ../patch_nfstream.py > /dev/null;          $PY nfstream_lru_repro.py
