#!/usr/bin/env bash
# extract-spring-services.sh
#
# Walks one or more repo paths and prints YAML stubs for every Spring Boot
# service found (a directory containing src/main/resources/application.yml).
# Hand-curated edges still go in inventory.yaml manually — this only fills
# the boring "where is service X" part.
#
# Usage:
#   ./extract-spring-services.sh <repo-path> [<repo-path> ...]
# Example (paths are relative to PLATFORM_ROOT, which defaults to the
# sibling platform-workspace/ workspace where source repos are cloned):
#   ./extract-spring-services.sh ../platform-workspace/backend-core
#
# Output: YAML on stdout, suitable for pasting under `services:` in inventory.yaml.

set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "usage: $0 <repo-path> [<repo-path> ...]" >&2
  exit 2
fi

# Repo paths in inventory.yaml are RELATIVE to the platform-workspace/ workspace
# (the directory containing all cloned source repos). By default we
# expect this graph repo to live as a sibling of platform-workspace/ on disk,
# i.e. ~/devops/platform-graph/ next to ~/devops/platform-workspace/.
# Override with PLATFORM_ROOT=/abs/path if the layout differs.
PLATFORM_ROOT="${PLATFORM_ROOT:-$(cd "$(dirname "$0")/../../platform-workspace" && pwd)}"

emit_service() {
  local app_module="$1"          # absolute path to module containing src/main/resources/application.yml
  local rel_app_module="${app_module#"$PLATFORM_ROOT"/}"
  local resources="$app_module/src/main/resources"
  local app_yml="$resources/application.yml"
  local k8s_yml="$resources/application-k8s.yml"

  # Best-effort defaults — review and edit before committing.
  local name
  name="$(basename "$app_module")"
  # Strip -app suffix to get the service slug (auth-app -> auth-service is the
  # convention but not always — the parent dir name is more reliable).
  local parent
  parent="$(basename "$(dirname "$app_module")")"
  local service_id
  if [[ "$name" == *-app ]]; then
    service_id="$parent"
  else
    service_id="$name"
  fi

  local spring_name=""
  if [[ -f "$app_yml" ]]; then
    spring_name="$(awk '/^spring:/{f=1;next} /^[a-zA-Z]/{f=0} f && /^  application:/{g=1;next} g && /^    name:/{print $2;exit}' "$app_yml" 2>/dev/null || true)"
  fi

  local port=""
  if [[ -f "$app_yml" ]]; then
    port="$(awk '/^server:/{f=1;next} /^[a-zA-Z]/{f=0} f && /^  port:/{print $2;exit}' "$app_yml" 2>/dev/null || true)"
  fi

  cat <<EOF
  ${service_id}:
    repo: $(basename "$(git -C "$app_module" rev-parse --show-toplevel 2>/dev/null || echo "$app_module")")
    paths:
      app_module: ${rel_app_module}
      spring_resources: ${rel_app_module}/src/main/resources
      java_root: ${rel_app_module}/src/main/java
    role: backend
    framework: spring-boot
    spring_name: ${spring_name:-TODO}
    port: ${port:-8080}
    chart:
      kind: local
      vs_path_prefix: TODO            # extract from api-gateway routes / chart VirtualService
    gitnexus_index:
      strategy: per-service
      analyze_path: ${rel_app_module%/*}    # parent module (incl. -client if present)
      name: ${service_id}
EOF
}

for repo in "$@"; do
  abs_repo="$(cd "$repo" && pwd)"
  echo "# Generated from: $abs_repo"
  # Find every module that has src/main/resources/application.yml
  # (the canonical marker for a Spring Boot app; libraries don't have one)
  while IFS= read -r app_yml; do
    module="${app_yml%/src/main/resources/application.yml}"
    emit_service "$module"
  done < <(find "$abs_repo" -path '*/src/main/resources/application.yml' -not -path '*/target/*' -not -path '*/test/*' 2>/dev/null | sort)
done
