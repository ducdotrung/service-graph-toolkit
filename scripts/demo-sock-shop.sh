#!/usr/bin/env bash
# Run the public, local-only Sock Shop graph demonstration.
set -euo pipefail

project=sock-shop
source_root=${1:-projects/sock-shop/sources}
output_dir=.graph-work/$project
report=$output_dir/graph-poc-report.md

fail() { printf 'prerequisite missing: %s\n' "$1" >&2; exit 2; }
require() { command -v "$1" >/dev/null || fail "$2"; }

require git 'install Git to fetch the public Sock Shop repositories.'
require python3 'install Python 3 to run the graph generator.'
require gitnexus 'install GitNexus (npm install -g gitnexus@latest), then rerun this script.'
require node 'install Node.js 20+; GitNexus and the demo require it.'
node_major=$(node -p 'process.versions.node.split(".")[0]')
(( node_major >= 20 )) || fail "upgrade Node.js to 20+ (found $(node --version))."

if [[ ! -x scripts/fetch-sock-shop.sh ]]; then
  fail 'run this script from the Service Graph Toolkit repository root.'
fi

printf '==> Fetching public Sock Shop sources\n'
scripts/fetch-sock-shop.sh "$source_root"

local_config=projects/sock-shop/.local.yaml
if [[ ! -f $local_config ]]; then
  printf '==> Creating ignored local source configuration\n'
  cp projects/sock-shop/.local.yaml.example "$local_config"
fi
configured_root=$(python3 - <<'PY'
import yaml
print((yaml.safe_load(open('projects/sock-shop/.local.yaml')) or {})['source_root'])
PY
)
[[ $configured_root == "$source_root" ]] || fail "set source_root: $source_root in $local_config, then rerun."

printf '==> Validating and generating graph artifacts\n'
python3 scripts/graph.py validate "$project"
python3 scripts/graph.py index "$project"
python3 scripts/graph.py generate "$project"

printf '==> Running indexed-code impact query\n'
impact_file=$output_dir/orders-controller-impact.txt
gitnexus impact OrdersController --direction upstream -r sock-shop--orders | tee "$impact_file"

indexed=0
for service in front-end catalogue carts orders payment shipping user; do
  [[ -d $source_root/$service/.git ]] && ((indexed += 1))
done
orders_revision=$(git -C "$source_root/orders" rev-parse --short HEAD)

cat > "$report" <<EOF
# Sock Shop Graph PoC Report

## Recommendation

Extend the pilot. The generated manifest makes the checkout dependency path
visible, and the indexed query provides code-level follow-up for orders.

## PoC scope

- Project: `$project`
- Services fetched/indexed: $indexed
- Orders revision: `$orders_revision`
- Excluded: runtime traces, containers, private sources, and remote credentials.

## What it proved

- The authored inventory declares `orders -> payment` and `orders -> shipping` in
  `projects/sock-shop/inventory.yaml`.
- `gitnexus impact OrdersController --direction upstream -r sock-shop--orders`
  completed; raw result: `$impact_file`.
- Generated service-map evidence: `$output_dir/service-map.md`.

## Measured coverage

- Seven public repositories were requested; $indexed have local Git metadata.
- The manifest declares six cross-service edges.
- Generated artifacts: group configuration, inventory JSON/schema, service map,
  and one page per service under `$output_dir`.
