#!/bin/bash
# Write the EdgeFlow-IDS NFStream patch as a unified diff (review round 7), without touching the
# live install: the installed (patched) package is copied to a temp dir, patch_nfstream.py --revert
# is run against the COPY (PYTHONPATH puts the copy first), and original vs patched meter.py are diffed.
# If the 6.6.0 wheel can be downloaded, its meter.py is compared with the reverted copy as well.
# Run: wsl -d Ubuntu-24.04 -u root bash /mnt/d/EdgeFlow-IDS/src/make_nfstream_diff.sh
set -u
PY=/opt/edgeflow/bin/python
OUT=/mnt/d/EdgeFlow-IDS/patches/nfstream-6.6.0-lru.diff
PKG=$($PY -c 'import nfstream, os; print(os.path.dirname(nfstream.__file__))')
echo "installed package: $PKG"
echo "live install marker count before: $(grep -c 'EdgeFlow-IDS patch' "$PKG/meter.py")"
T=$(mktemp -d)
mkdir -p "$T/orig" "$T/patched"
cp -r "$PKG" "$T/orig/nfstream"
cp -r "$PKG" "$T/patched/nfstream"
cd "$T/orig" && PYTHONPATH="$T/orig" $PY /mnt/d/EdgeFlow-IDS/src/patch_nfstream.py --revert
echo "copy marker count after revert: $(grep -c 'EdgeFlow-IDS patch' "$T/orig/nfstream/meter.py")"
cd "$T" && diff -u --label a/nfstream/meter.py --label b/nfstream/meter.py orig/nfstream/meter.py patched/nfstream/meter.py > "$OUT"
echo "diff exit $? ; written $OUT"
cat "$OUT"
# optional cross-check against the published wheel
mkdir -p "$T/wheel" && cd "$T/wheel"
if $PY -m pip download --no-deps --only-binary=:all: nfstream==6.6.0 -d . -q 2>/dev/null; then
  W=$(ls *.whl | head -1); echo "wheel: $W"
  $PY -c "import zipfile,sys; sys.stdout.write(zipfile.ZipFile('$W').read('nfstream/meter.py').decode())" > wheel_meter.py
  if cmp -s wheel_meter.py "$T/orig/nfstream/meter.py"; then echo "WHEEL_MATCH: reverted copy == wheel meter.py"; else echo "WHEEL_DIFFERS"; diff wheel_meter.py "$T/orig/nfstream/meter.py" | head; fi
else
  echo "wheel download not possible (offline?); cross-check skipped"
fi
echo "live install marker count after: $(grep -c 'EdgeFlow-IDS patch' "$PKG/meter.py")"
