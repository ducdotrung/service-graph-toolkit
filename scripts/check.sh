#!/usr/bin/env bash
set -euo pipefail
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
scripts/agent-doctor.sh
python3 scripts/graph.py validate example-platform
python3 scripts/graph.py validate sock-shop
