#!/usr/bin/env python3
"""Render inventory.yaml as a Mermaid service map.

Output: views/service-map.md — one combined diagram plus per-kind subviews.
GitHub renders Mermaid natively, so the file is reviewable in any PR.

Node colors track service.role; edge styles track edge.kind.

Usage:  python3 scripts/inventory-to-service-map.py [--out views/service-map.md]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY = REPO_ROOT / "inventory.yaml"
OUT = REPO_ROOT / "views" / "service-map.md"

ROLE_CLASS = {
    "gateway":     ("roleGw",   "fill:#fef3c7,stroke:#d97706,stroke-width:2px"),
    "backend":     ("roleBe",   "fill:#dbeafe,stroke:#2563eb,stroke-width:1px"),
    "mcp-server":  ("roleMcp",  "fill:#ede9fe,stroke:#7c3aed,stroke-width:1px"),
    "ai-app":      ("roleAi",   "fill:#fce7f3,stroke:#db2777,stroke-width:1px"),
    "ai-service":  ("roleAis",  "fill:#ffe4e6,stroke:#e11d48,stroke-width:1px"),
    "tool":        ("roleTool", "fill:#d1fae5,stroke:#059669,stroke-width:1px"),
    "jar-worker":  ("roleWork", "fill:#e5e7eb,stroke:#4b5563,stroke-width:1px"),
}

EDGE_STYLE = {
    "gateway_route":  "-->",
    "feign_call":     "-->",
    "kafka":          "-.->",
    "mcp_tool_use":   "==>",
    "shared_db":      "---",
}

EDGE_LABEL = {
    "gateway_route":  "route",
    "feign_call":     "feign",
    "kafka":          "kafka",
    "mcp_tool_use":   "mcp",
    "shared_db":      "db",
}


def node_id(sid: str) -> str:
    """Mermaid node identifier — alphanumeric + underscore."""
    return sid.replace("-", "_")


def build_diagram(services: dict, edges: list[dict], kinds: set[str] | None = None) -> str:
    """Build one Mermaid diagram. If kinds is None, include all edges."""
    lines = ["```mermaid", "graph LR"]
    # Group nodes by role for visual clustering.
    by_role: dict[str, list[str]] = {}
    for sid, svc in services.items():
        role = svc.get("role", "backend")
        by_role.setdefault(role, []).append(sid)
    for role, sids in by_role.items():
        css_class, _ = ROLE_CLASS.get(role, ("other", ""))
        lines.append(f"  subgraph {css_class}[{role}]")
        for sid in sorted(sids):
            lines.append(f"    {node_id(sid)}[{sid}]")
        lines.append("  end")
    # Edges
    seen: set[tuple[str, str, str]] = set()
    for e in edges:
        kind = e.get("kind")
        if kinds is not None and kind not in kinds:
            continue
        src, dst = e.get("from"), e.get("to")
        if not (src and dst):
            continue
        if src not in services or dst not in services:
            continue
        key = (src, dst, kind)
        if key in seen:
            continue
        seen.add(key)
        arrow = EDGE_STYLE.get(kind, "-->")
        label = EDGE_LABEL.get(kind, kind)
        lines.append(f"  {node_id(src)} {arrow}|{label}| {node_id(dst)}")
    # Class definitions
    for role, (css, style) in ROLE_CLASS.items():
        lines.append(f"  classDef {css} {style}")
    for sid, svc in services.items():
        role = svc.get("role", "backend")
        css, _ = ROLE_CLASS.get(role, ("other", ""))
        lines.append(f"  class {node_id(sid)} {css}")
    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default=str(INVENTORY))
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args()

    with open(args.inventory) as fh:
        inventory = yaml.safe_load(fh)
    services = inventory.get("services", {})
    edges = inventory.get("edges", [])

    # Filter services to those with a gitnexus_index so the map matches
    # what's actually queryable. Edges to/from unindexed services are dropped
    # by build_diagram's services check above.
    indexed = {sid: svc for sid, svc in services.items() if svc.get("gitnexus_index")}

    sections = [
        "# Microservice Platform — Service Map",
        "",
        f"Generated from `inventory.yaml` ({len(indexed)} indexed services, {len(edges)} edges). Do not hand-edit — re-run `scripts/inventory-to-service-map.py`.",
        "",
        "## Legend",
        "",
        "- Node color: service role (gateway / backend / mcp-server / ai-app / ai-service / tool / jar-worker)",
        "- Edge style: `-->` http (feign / gateway), `-.->` kafka, `==>` mcp tool use, `---` shared db",
        "",
        "## Full graph",
        "",
        build_diagram(indexed, edges),
        "",
        "## Gateway routes only",
        "",
        build_diagram(indexed, edges, kinds={"gateway_route"}),
        "",
        "## Feign calls only",
        "",
        build_diagram(indexed, edges, kinds={"feign_call"}),
        "",
        "## Kafka edges only",
        "",
        build_diagram(indexed, edges, kinds={"kafka"}),
        "",
        "## MCP tool use",
        "",
        build_diagram(indexed, edges, kinds={"mcp_tool_use"}),
        "",
    ]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(sections))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
