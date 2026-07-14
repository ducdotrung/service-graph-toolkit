#!/usr/bin/env bash
set -euo pipefail
for path in shared/AGENTS.md shared/MODEL_GUIDE.md shared/mcp/tool-contracts.md scripts/context-pack.sh scripts/fetch-web.mjs; do
  [[ -e "$path" ]] || { echo "missing: $path" >&2; exit 1; }
done
command -v python3 >/dev/null || { echo 'missing: python3' >&2; exit 1; }
command -v node >/dev/null || { echo 'missing: node' >&2; exit 1; }
bash -n scripts/context-pack.sh scripts/agent-doctor.sh
node --check scripts/fetch-web.mjs
node -e "import('./scripts/fetch-web.mjs')"
echo 'Service Graph Toolkit agent checks passed'
