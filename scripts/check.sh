#!/usr/bin/env bash
set -euo pipefail
python3 -m unittest discover -s tests -v
scripts/agent-doctor.sh
python3 scripts/graph.py validate example-platform
python3 scripts/graph.py validate sock-shop
