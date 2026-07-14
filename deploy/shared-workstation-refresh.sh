#!/usr/bin/env bash
# Index and generate one declared project; never clone, pull, or serve MCP.
set -euo pipefail

project=${1:?usage: shared-workstation-refresh.sh <project-id>}
[[ $project =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo 'invalid project ID' >&2; exit 2; }
for required in PROJECT_ID GRAPH_ROOT SOURCE_ROOT GITNEXUS_HOME AUDIT_LOG; do
  [[ -n ${!required:-} ]] || { echo "missing $required" >&2; exit 2; }
done
command -v python3 >/dev/null || { echo 'missing python3' >&2; exit 2; }
command -v gitnexus >/dev/null || { echo 'missing gitnexus' >&2; exit 2; }

audit() {
  mkdir -p "$(dirname "$AUDIT_LOG")"
  printf '%s project=%s action=index-generate result=%s\n' "$(date -Iseconds)" "$project" "$1" >> "$AUDIT_LOG"
  if [[ $(wc -l < "$AUDIT_LOG") -gt 10000 ]]; then
    tail -n 10000 "$AUDIT_LOG" > "$AUDIT_LOG.tmp" && mv "$AUDIT_LOG.tmp" "$AUDIT_LOG"
  fi
}
trap 'audit failed' ERR

cd "$GRAPH_ROOT"
project_dir=projects/$project
[[ $project == "$PROJECT_ID" && -d $SOURCE_ROOT ]] || { echo 'project configuration mismatch' >&2; exit 2; }
[[ -f $project_dir/project.yaml && -f $project_dir/inventory.yaml ]] || { echo "unknown project: $project" >&2; exit 2; }
umask 027
printf 'source_root: %s\n' "$SOURCE_ROOT" > "$project_dir/.local.yaml"
export GITNEXUS_HOME
python3 scripts/graph.py validate "$project"
python3 scripts/graph.py index "$project"
python3 scripts/graph.py generate "$project"
audit success
