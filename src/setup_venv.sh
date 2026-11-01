#!/usr/bin/env bash
# Create the project venv in WSL (run as root, so Mininet hosts can use it).
set -e
python3 -m venv /opt/edgeflow
/opt/edgeflow/bin/pip install -q -r "$(dirname "$0")/../requirements.txt"
/opt/edgeflow/bin/python -c 'import nfstream,sklearn,pymoo;print("nfstream",nfstream.__version__,"sklearn",sklearn.__version__,"pymoo",pymoo.__version__)'
/opt/edgeflow/bin/python "$(dirname "$0")/patch_nfstream.py"
