#!/usr/bin/env bash
# workstation-refresh.sh — nightly cron pipeline for the platform-graph
#
# Runs on the workstation as the gitnexus service user.
# Steps:
#   1. Pull latest code for every repo listed in inventory.yaml
#   2. Re-index repos whose HEAD changed since last run
#   3. Regenerate all derived views (group.yaml, service-map, pages, json)
#   4. Run gitnexus group sync + post-filter
#   5. Leave regenerated artifacts on disk for local use
#
# Cron entry (edit with: sudo crontab -e -u gitnexus):
#   0 3 * * *  /opt/platform-graph/scripts/workstation-refresh.sh >> /var/log/platform-graph-refresh.log 2>&1
#
# Environment (set via systemd EnvironmentFile or before calling this script):
#   GRAPH_ROOT      — path to this repo     (default: /opt/platform-graph)
#   PLATFORM_ROOT   — path to cloned repos  (default: /opt/platform-workspace)
#   GITNEXUS_HOME   — gitnexus data dir     (default: /opt/gitnexus-home)
#   SLACK_WEBHOOK   — optional Slack URL for failure alerts

set -euo pipefail

# Cron runs with a minimal PATH — probe common install locations for gitnexus
export PATH="/usr/local/bin:/usr/bin:/bin:$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"

# Auto-detect gitnexus if not already on PATH (npm global install varies by user)
if ! command -v gitnexus &>/dev/null; then
    for _candidate in \
        "$(npm root -g 2>/dev/null)/../bin/gitnexus" \
        "/opt/gitnexus/bin/gitnexus" \
        "$HOME/.npm/bin/gitnexus" \
        "$HOME/node_modules/.bin/gitnexus"
    do
        if [[ -x "$_candidate" ]]; then
            export PATH="$(dirname "$_candidate"):$PATH"
            break
        fi
    done
fi

command -v gitnexus &>/dev/null || { echo "FATAL: gitnexus not found on PATH. Install with: npm install -g gitnexus"; exit 1; }

GRAPH_ROOT="${GRAPH_ROOT:-/opt/platform-graph}"
PLATFORM_ROOT="${PLATFORM_ROOT:-/opt/platform-workspace}"
GITNEXUS_HOME="${GITNEXUS_HOME:-/opt/gitnexus-home}"
# Marker file lives in GITNEXUS_HOME so the gitnexus user always has write access
MARKER_FILE="${GITNEXUS_HOME}/.last-refresh-commits"
LOG_PREFIX="[platform-refresh $(date -Iseconds)]"

export GITNEXUS_HOME

cd "$GRAPH_ROOT"

log() { echo "${LOG_PREFIX} $*"; }
fail() { log "ERROR: $*"; if [[ -n "${SLACK_WEBHOOK:-}" ]]; then curl -s -X POST "$SLACK_WEBHOOK" -H "Content-Type: application/json" -d "{\"text\":\"platform-graph refresh FAILED: $*\"}" > /dev/null; fi; exit 1; }

log "=== Platform graph refresh started ==="

# ──────────────────────────────────────────────────────────────────────────────
# 0. Clone any repos in REPOS.md that aren't on disk yet
#    Source of truth: the table rows in REPOS.md (path | type | remote).
#    Stops at "Other repos referenced by automation" — those are not in scope.
# ──────────────────────────────────────────────────────────────────────────────
log "Step 0: cloning missing repos"

CLONED=0
CLONE_ERRORS=0

python3 - <<'PYEOF' > /tmp/clone-targets.txt
import re, pathlib

repos_md = pathlib.Path("REPOS.md").read_text()

# Stop before the "not yet cloned / not in scope" section
stop_marker = "## Other repos referenced by automation"
if stop_marker in repos_md:
    repos_md = repos_md[:repos_md.index(stop_marker)]

# Match table rows: | `path` | anything | `git@...` |
for m in re.finditer(r'^\|\s*`([^`]+)`\s*\|[^|]*\|\s*`(git@[^`]+)`\s*\|', repos_md, re.MULTILINE):
    path, remote = m.group(1), m.group(2)
    print(f"{path}|{remote}")
PYEOF

while IFS='|' read -r rel_path remote; do
    [[ -z "$rel_path" || -z "$remote" ]] && continue
    abs_path="$PLATFORM_ROOT/$rel_path"
    if [[ -d "$abs_path/.git" ]]; then
        continue  # already cloned
    fi
    # Dir exists without .git (empty scaffold folder) — remove so git clone can proceed
    if [[ -d "$abs_path" ]]; then
        log "  removing non-git dir: $rel_path"
        rm -rf "$abs_path"
    fi
    parent="$(dirname "$abs_path")"
    mkdir -p "$parent"
    log "  cloning: $rel_path from $remote"
    clone_out=$(git clone --quiet "$remote" "$abs_path" 2>&1)
    if [[ $? -eq 0 ]]; then
        CLONED=$((CLONED + 1))
    else
        log "  ERROR clone failed: $rel_path — $clone_out"
        CLONE_ERRORS=$((CLONE_ERRORS + 1))
    fi
done < /tmp/clone-targets.txt

log "  cloned: $CLONED repos, $CLONE_ERRORS errors"

# ──────────────────────────────────────────────────────────────────────────────
# 1. Pull every git repo found under PLATFORM_ROOT (up to 2 levels deep)
# ──────────────────────────────────────────────────────────────────────────────
log "Step 1: pulling repos"

PULLED=0
PULL_ERRORS=0

# Find all .git dirs at depth 1 (flat repos) and depth 2 (repos inside grouped
# folders like mcp-servers/ and visualization-apps/) — but not deeper to avoid submodules.
while IFS= read -r git_dir; do
    abs="${git_dir%/.git}"
    rel="${abs#$PLATFORM_ROOT/}"
    if git -C "$abs" pull --ff-only --quiet 2>/dev/null; then
        PULLED=$((PULLED + 1))
    else
        log "  WARN pull failed: $rel"
        PULL_ERRORS=$((PULL_ERRORS + 1))
    fi
done < <(find "$PLATFORM_ROOT" -mindepth 2 -maxdepth 3 -name ".git" -type d | sort)

log "  pulled: $PULLED repos, $PULL_ERRORS errors"

# ──────────────────────────────────────────────────────────────────────────────
# 2. Re-index repos whose HEAD changed since last run
# ──────────────────────────────────────────────────────────────────────────────
log "Step 2: re-indexing changed repos"

# Load previous HEAD markers (file format: "<registry-name> <commit-hash>")
declare -A PREV_COMMITS
if [[ -f "$MARKER_FILE" ]]; then
    while IFS=' ' read -r name hash; do
        PREV_COMMITS["$name"]="$hash"
    done < "$MARKER_FILE"
fi

REINDEXED=0
declare -A NEW_COMMITS

python3 - <<'PYEOF' > /tmp/index-targets.txt
import yaml
with open("inventory.yaml") as f:
    inv = yaml.safe_load(f)
for sid, svc in inv.get("services", {}).items():
    gi = svc.get("gitnexus_index") or {}
    if not gi.get("name"):
        continue
    path = gi.get("analyze_path") or ""
    repo_id = inv.get("repos", {}).get(svc.get("repo", ""), {}).get("path", "")
    skip_git = "1" if gi.get("skip_git") else "0"
    print(f"{gi['name']}|{path}|{repo_id}|{skip_git}")
PYEOF

while IFS='|' read -r gname analyze_path repo_rel skip_git; do
    [[ -z "$gname" ]] && continue
    abs_repo="$PLATFORM_ROOT/$repo_rel"
    abs_analyze="${PLATFORM_ROOT}/${analyze_path:-$repo_rel}"

    if [[ ! -d "$abs_analyze" ]]; then
        log "  SKIP (not found): $gname at $abs_analyze"
        continue
    fi

    # Determine current HEAD
    if [[ -d "$abs_repo/.git" ]]; then
        current=$(git -C "$abs_repo" rev-parse HEAD 2>/dev/null || echo "unknown")
    else
        current="unknown"
    fi
    NEW_COMMITS["$gname"]="$current"

    prev="${PREV_COMMITS[$gname]:-}"
    index_dir="$abs_analyze/.gitnexus"
    if [[ "$current" == "$prev" && "$current" != "unknown" && -d "$index_dir" ]]; then
        continue  # no change and index already exists
    fi

    reason="changed"
    if [[ ! -d "$index_dir" ]]; then
        reason="missing-index"
    elif [[ "$prev" != "$current" || "$current" == "unknown" ]]; then
        reason="changed"
    fi

    log "  indexing: $gname (${prev:-new} → ${current:0:8}, $reason)"
    skip_flag=""
    [[ "$skip_git" == "1" ]] && skip_flag="--skip-git"
    if gitnexus analyze "$abs_analyze" --name "$gname" $skip_flag --force 2>&1 | tail -2; then
        REINDEXED=$((REINDEXED + 1))
    else
        log "  WARN: analyze failed for $gname"
    fi
done < /tmp/index-targets.txt

# Save new HEAD markers
for name in "${!NEW_COMMITS[@]}"; do
    echo "$name ${NEW_COMMITS[$name]}"
done > "$MARKER_FILE"

log "  re-indexed: $REINDEXED repos"

# Skip remaining steps if nothing changed
if [[ "$REINDEXED" -eq 0 ]]; then
    log "Nothing changed — skipping downstream steps."
    log "=== Refresh complete (no changes) ==="
    exit 0
fi

# ──────────────────────────────────────────────────────────────────────────────
# 3. Regenerate derived views
# ──────────────────────────────────────────────────────────────────────────────
log "Step 3: regenerating derived views"
python3 scripts/inventory-to-group.py   || fail "inventory-to-group failed"
python3 scripts/inventory-to-mermaid.py  2>/dev/null || python3 scripts/inventory-to-service-map.py || fail "inventory-to-mermaid failed"
python3 scripts/inventory-to-pages.py   || fail "inventory-to-pages failed"
python3 scripts/inventory-to-json.py    || fail "inventory-to-json failed"
log "  done"

# ──────────────────────────────────────────────────────────────────────────────
# 4. Group sync + post-filter
# ──────────────────────────────────────────────────────────────────────────────
log "Step 4: group sync + filter"
# Install/update group.yaml into GITNEXUS_HOME so gitnexus can find it
GROUP_DIR="${GITNEXUS_HOME}/groups/platform-projected"
mkdir -p "$GROUP_DIR"
cp "${GRAPH_ROOT}/group.yaml" "${GROUP_DIR}/group.yaml"
gitnexus group sync platform-projected 2>&1 | tail -3 || fail "group sync failed"
python3 scripts/filter-bridge.py \
    --report "views/drift-report.md" \
    --out "views/filtered-bridge.json" || fail "filter-bridge failed"
log "  done"

# ──────────────────────────────────────────────────────────────────────────────
# 5. Leave regenerated artifacts on disk (do not commit generated outputs)
# ──────────────────────────────────────────────────────────────────────────────
log "Step 5: leaving generated artifacts uncommitted"
log "  refreshed local outputs under group.yaml and views/"

# Optional Slack digest
if [[ -n "${SLACK_WEBHOOK:-}" ]]; then
    DROPPED=$(grep "^\\*\\*dropped" views/drift-report.md | grep -o '[0-9]*' | head -1 || echo "?")
    INV_ONLY=$(grep "^\\*\\*inventory-only" views/drift-report.md | grep -o '[0-9]*' | head -1 || echo "?")
    curl -s -X POST "$SLACK_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"platform-graph refresh ${REFRESH_DATE}: ${REINDEXED} repos re-indexed, ${DROPPED} bridge false-positives dropped, ${INV_ONLY} inventory-only gaps\"}" > /dev/null
fi

log "=== Refresh complete ==="
