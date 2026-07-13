#!/usr/bin/env bash
set -euo pipefail
repo="${1:-.}"
cd "$repo"
printf '# Local Context Pack\n\n- Path: `%s`\n' "$(pwd)"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf -- '- Branch: `%s`\n- Revision: `%s`\n\n## Working tree\n```text\n' "$(git branch --show-current || printf detached)" "$(git rev-parse --short HEAD)"
  git status --short
  printf '```\n\n## Recent commits\n```text\n'
  git log -5 --oneline
  printf '```\n'
fi
printf '\n## Instructions\n'
find . -path './.git' -prune -o \( -name AGENTS.md -o -name AGENT.md -o -name CLAUDE.md \) -type f -print | sort || true
printf '\n## Manifests\n'
find . -path './.git' -prune -o \( -name package.json -o -name pyproject.toml -o -name go.mod -o -name Cargo.toml -o -name Makefile \) -type f -print | sort || true
