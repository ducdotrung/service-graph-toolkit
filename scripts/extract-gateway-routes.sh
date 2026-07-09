#!/usr/bin/env bash
# extract-gateway-routes.sh
#
# Reads api-gateway's application-k8s.yml and prints YAML edges suitable for
# pasting under `edges:` in inventory.yaml.
#
# Usage:
#   ./extract-gateway-routes.sh [path-to-application-k8s.yml]
#
# Default path is the canonical one; override only if testing.

set -euo pipefail

PLATFORM_ROOT="${PLATFORM_ROOT:-$(cd "$(dirname "$0")/../../platform-workspace" && pwd)}"
SRC="${1:-$PLATFORM_ROOT/backend-core/gateway-service/src/main/resources/application-k8s.yml}"

if [[ ! -f "$SRC" ]]; then
  echo "not found: $SRC" >&2
  exit 1
fi

REL_EVIDENCE="${SRC#"$PLATFORM_ROOT"/}"

# Parse the routes block. We only need: id, uri, predicates Path=...
# yq would be cleaner but we avoid extra deps; awk works for this shape.
awk -v evidence="$REL_EVIDENCE" '
  /^      routes:$/ { in_routes=1; next }
  in_routes && /^      [a-zA-Z]/ { in_routes=0 }   # block ended
  in_routes && /^        - id:/ {
    if (id) emit()
    id=$3; uri=""; path=""
  }
  in_routes && /^          uri:/ { uri=$2 }
  in_routes && /^            - Path=/ {
    sub(/^.*Path=/, ""); path=$0
  }
  END { if (id) emit() }

  function emit() {
    # extract host from uri  http://X[:port]
    host=uri
    sub(/^http:\/\//, "", host)
    sub(/:.*/, "", host)
    # primary path = first comma-separated entry
    primary=path; rest=""
    if (index(path, ",") > 0) {
      primary=substr(path, 1, index(path, ",")-1)
      rest=substr(path, index(path, ",")+1)
    }
    print "  - from: api-gateway"
    print "    to: " id
    print "    kind: gateway_route"
    print "    path: " primary
    if (rest != "") print "    extra_paths: [" rest "]"
    print "    target: " uri
    print "    evidence: " evidence
  }
' "$SRC"
