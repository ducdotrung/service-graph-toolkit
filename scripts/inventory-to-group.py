#!/usr/bin/env python3
"""Project inventory.yaml into a gitnexus group.yaml.

Emits:
  - repos:    every service with a gitnexus_index, keyed by <role>/<service-id>
  - links:    only edges the auto-extractor misses (gateway_route, mcp_tool_use,
              shared_db). feign_call and kafka are SKIPPED because the
              HttpRouteExtractor and topic scanner pick them up natively. See
              docs/CURRENT/gitnexus-group-feature.md for the rationale and the
              post-filter that policies the auto-extractor's false positives.
  - packages: shared-common topic constant remaps (currently none enumerated)
  - detect/matching: static config block

Usage:  python3 scripts/inventory-to-group.py [--out group.yaml]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY = REPO_ROOT / "inventory.yaml"

# Edge kinds we DO emit as manual links: the auto-extractor cannot see them.
PROJECT_KINDS = {"gateway_route", "mcp_tool_use", "shared_db"}
# Edge kinds we deliberately skip: covered by gitnexus auto-extractors.
SKIP_KINDS = {"feign_call", "kafka"}


def group_path(service_id: str, service: dict) -> str:
    """Map a service-id to its group-path. Role-prefixed for human scannability."""
    role = service.get("role", "backend")
    bucket = {
        "gateway": "gateway",
        "backend": "backend",
        "mcp-server": "mcp",
        "ai-app": "ai-app",
        "ai-service": "ai-service",
        "tool": "tool",
        "jar-worker": "worker",
    }.get(role, role)
    if bucket == "gateway":
        return service_id
    return f"{bucket}/{service_id}"


def build_repos(services: dict) -> dict[str, str]:
    """{group_path: gitnexus_registry_name} for every indexed service."""
    out: dict[str, str] = {}
    for sid, svc in services.items():
        idx = svc.get("gitnexus_index")
        if not idx or not idx.get("name"):
            continue
        out[group_path(sid, svc)] = idx["name"]
    return out


def project_gateway_route(edge: dict, paths: dict[str, str]) -> list[dict]:
    """Spring Cloud Gateway YAML route → http link pair (provider + consumer)."""
    src = edge.get("from")
    dst = edge.get("to")
    path = edge.get("path")
    if not (src and dst and path):
        return []
    if src not in paths or dst not in paths:
        return []
    return [
        {"from": paths[src], "to": paths[dst], "type": "http",
         "contract": path, "role": "consumer"},
        {"from": paths[src], "to": paths[dst], "type": "http",
         "contract": path, "role": "provider"},
    ]


def project_mcp_tool_use(edge: dict, paths: dict[str, str]) -> list[dict]:
    """MCP tool call → custom link, one per tool."""
    src = edge.get("from")
    dst = edge.get("to")
    if not (src and dst):
        return []
    if src not in paths or dst not in paths:
        return []
    tools = edge.get("tools_used") or [edge.get("tool")]
    tools = [t for t in tools if t]
    if not tools:
        return [{"from": paths[src], "to": paths[dst], "type": "custom",
                 "contract": f"mcp::{dst}", "role": "consumer"}]
    return [
        {"from": paths[src], "to": paths[dst], "type": "custom",
         "contract": f"mcp::{dst}::{tool}", "role": "consumer"}
        for tool in tools
    ]


def project_shared_db(edge: dict, paths: dict[str, str]) -> list[dict]:
    """Shared-DB edge → custom link tagged with schema name."""
    src = edge.get("from")
    dst = edge.get("to")
    schema = edge.get("schema") or edge.get("db") or "shared"
    if not (src and dst):
        return []
    if src not in paths or dst not in paths:
        return []
    return [
        {"from": paths[src], "to": paths[dst], "type": "custom",
         "contract": f"db::{schema}", "role": "consumer"},
    ]


def build_links(edges: list[dict], paths: dict[str, str]) -> list[dict]:
    links: list[dict] = []
    for edge in edges:
        kind = edge.get("kind")
        if kind in SKIP_KINDS:
            continue
        if kind == "gateway_route":
            links.extend(project_gateway_route(edge, paths))
        elif kind == "mcp_tool_use":
            links.extend(project_mcp_tool_use(edge, paths))
        elif kind == "shared_db":
            links.extend(project_shared_db(edge, paths))
    return links


def build_group(inventory: dict, name: str = "example-platform") -> dict:
    services = inventory.get("services", {})
    edges = inventory.get("edges", [])
    repos = build_repos(services)
    # Restrict paths to indexed services so links never reference an
    # unregistered repo (gitnexus group sync would silently drop those links).
    paths = {sid: group_path(sid, svc) for sid, svc in services.items()
             if svc.get("gitnexus_index")}
    links = build_links(edges, paths)
    return {
        "version": 1,
        "name": name,
        "description": (
            "Example platform projected from inventory.yaml. "
            "Auto-extracted edges (feign_call, kafka) are not in links: — "
            "the extractor sees them natively. Manual links cover what the "
            "extractor misses: gateway YAML routes, MCP tool wiring, shared DB."
        ),
        "repos": repos,
        "links": links,
        "packages": {},
        "detect": {
            "http": True,
            "grpc": True,
            "thrift": True,
            "topics": True,
            "shared_libs": True,
            "embedding_fallback": False,
            "includes": False,
            "workspace_deps": False,
        },
        "matching": {
            "bm25_threshold": 0.7,
            "embedding_threshold": 0.65,
            "max_candidates_per_step": 3,
            "exclude_links_paths": ["/health", "/ping", "/actuator/**"],
            "exclude_links_param_only_paths": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default=str(INVENTORY))
    parser.add_argument("--out", default=str(REPO_ROOT / "group.yaml"))
    parser.add_argument("--name", default="example-platform")
    args = parser.parse_args()

    with open(args.inventory) as fh:
        inventory = yaml.safe_load(fh)

    group = build_group(inventory, name=args.name)
    with open(args.out, "w") as fh:
        yaml.safe_dump(group, fh, sort_keys=False, width=120, allow_unicode=True)

    print(f"Wrote {args.out}: {len(group['repos'])} repos, {len(group['links'])} links", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
