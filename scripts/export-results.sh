#!/usr/bin/env bash
# Export GitNexus per-service summaries into results/<svc>.json
# Run from the microservice-graph repo root.
# Requires: gitnexus installed, all 6 PoC services indexed.

set -euo pipefail

GRAPH_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RESULTS_DIR="$GRAPH_ROOT/results"
PLATFORM_ROOT="${PLATFORM_ROOT:-$HOME/sre/code-platform}"

mkdir -p "$RESULTS_DIR"

SERVICES=(
  app-gateway
  auth-service
  bio-service
  user-platform-service
  mcp-platform
  ai-assistant
)

echo "Exporting GitNexus results to $RESULTS_DIR ..."

# Capture gitnexus list as raw text
LIST_OUTPUT=$(cd "$PLATFORM_ROOT" && gitnexus list 2>&1)
echo "$LIST_OUTPUT" > "$RESULTS_DIR/gitnexus-list.txt"

for svc in "${SERVICES[@]}"; do
  echo "  $svc ..."

  # Run structural check
  CHECK_JSON=$(cd "$PLATFORM_ROOT" && gitnexus check --cycles --json -r "$svc" 2>&1)

  # Extract stats block from gitnexus list output
  STATS_BLOCK=$(echo "$LIST_OUTPUT" | sed -n "/^  $svc$/,/^$/p" | head -n -1)

  # Parse individual fields
  SVC_PATH=$(echo "$STATS_BLOCK" | grep "Path:" | sed 's/.*Path:\s*//' | xargs)
  SVC_INDEXED=$(echo "$STATS_BLOCK" | grep "Indexed:" | sed 's/.*Indexed:\s*//' | xargs)
  SVC_COMMIT=$(echo "$STATS_BLOCK" | grep "Commit:" | sed 's/.*Commit:\s*//' | xargs)
  SVC_BRANCH=$(echo "$STATS_BLOCK" | grep "Branch:" | sed 's/.*Branch:\s*//' | xargs || echo "")
  SVC_STATS=$(echo "$STATS_BLOCK" | grep "Stats:" | sed 's/.*Stats:\s*//' | xargs)
  SVC_CLUSTERS=$(echo "$STATS_BLOCK" | grep "Clusters:" | sed 's/.*Clusters:\s*//' | xargs)
  SVC_PROCESSES=$(echo "$STATS_BLOCK" | grep "Processes:" | sed 's/.*Processes:\s*//' | xargs)

  # Parse stats line: "35 files, 192 symbols, 367 edges"
  SVC_FILES=$(echo "$SVC_STATS" | grep -o '[0-9]* files' | grep -o '[0-9]*')
  SVC_SYMBOLS=$(echo "$SVC_STATS" | grep -o '[0-9,]* symbols' | grep -o '[0-9,]*')
  SVC_EDGES=$(echo "$SVC_STATS" | grep -o '[0-9,]* edges' | grep -o '[0-9,]*')

  # Determine skip_git status
  SKIP_GIT="true"
  if [ "$SVC_COMMIT" != "unknown" ]; then
    SKIP_GIT="false"
  fi

  # Build JSON using python for reliability
  python3 -c "
import json, sys

check = json.loads('''$CHECK_JSON''')

result = {
    'service': '$svc',
    'exported_at': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'index': {
        'path': '$SVC_PATH',
        'indexed_at': '$SVC_INDEXED',
        'commit': '$SVC_COMMIT',
        'skip_git': $SKIP_GIT
    },
    'stats': {
        'files': $SVC_FILES,
        'symbols': int('$SVC_SYMBOLS'.replace(',', '')),
        'edges': int('$SVC_EDGES'.replace(',', '')),
        'clusters': $SVC_CLUSTERS,
        'processes': $SVC_PROCESSES
    },
    'check': check
}

# Add branch if present
if '$SVC_BRANCH':
    result['index']['branch'] = '$SVC_BRANCH'

with open('$RESULTS_DIR/$svc.json', 'w') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
"

done

echo "Done. Results in $RESULTS_DIR/"
ls -la "$RESULTS_DIR/"
