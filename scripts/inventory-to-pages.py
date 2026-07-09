#!/usr/bin/env python3
"""Generate one Markdown page per service from inventory.yaml.

Output:
  - views/services/<service-id>.md  (one per service)
  - views/services/README.md        (index of all pages, grouped by role)

Each page shows: identity (role, repo, chart, framework, port, db, kafka),
incoming edges (who calls this), outgoing edges (who this calls), evidence
pointers, and any notes from the inventory.

Usage:  python3 scripts/inventory-to-pages.py
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY = REPO_ROOT / "inventory.yaml"
OUT_DIR = REPO_ROOT / "views" / "services"

ROLE_ORDER = ["gateway", "backend", "mcp-server", "ai-app", "ai-service", "tool", "jar-worker"]
KIND_LABEL = {
    "gateway_route": "Gateway route",
    "feign_call":    "Feign call",
    "kafka":         "Kafka",
    "mcp_tool_use":  "MCP tool",
    "shared_db":     "Shared DB",
}


def yaml_block(d: dict | list, indent: int = 0) -> str:
    """Render a small YAML fragment for evidence/details blocks."""
    return yaml.safe_dump(d, sort_keys=False, allow_unicode=True, indent=2).rstrip()


def edge_line(e: dict, direction: str) -> str:
    """One line describing an edge: 'kind  via  details  evidence'."""
    kind = e.get("kind", "?")
    other = e["to"] if direction == "outgoing" else e["from"]
    parts = [f"**{KIND_LABEL.get(kind, kind)}** → `{other}`" if direction == "outgoing"
             else f"**{KIND_LABEL.get(kind, kind)}** ← `{other}`"]
    if e.get("path"):
        parts.append(f"`{e['path']}`")
    if e.get("topic"):
        parts.append(f"topic `{e['topic']}`")
    if e.get("via_client"):
        parts.append(f"via `{e['via_client']}`")
    if e.get("via_clients"):
        parts.append(f"via [{', '.join(f'`{c}`' for c in e['via_clients'])}]")
    if e.get("tools_used"):
        parts.append(f"tools [{', '.join(f'`{t}`' for t in e['tools_used'])}]")
    if e.get("notes"):
        parts.append(f"_{e['notes'].strip()}_")
    return "- " + " — ".join(parts)


def render_service(sid: str, svc: dict, edges_in: list[dict], edges_out: list[dict]) -> str:
    lines = [f"# {sid}", ""]

    # Identity table
    rows = [
        ("Role", svc.get("role")),
        ("Repo", svc.get("repo")),
        ("Framework", svc.get("framework")),
        ("Port", svc.get("port")),
    ]
    chart = svc.get("chart") or {}
    if chart:
        rows.append(("Chart", f"{chart.get('kind','?')} — {chart.get('name', '(local)')} (ns: {chart.get('namespace','?')})"))
        if chart.get("vs_path_prefix"):
            rows.append(("VS path prefix", f"`{chart['vs_path_prefix']}`"))
    db = svc.get("db") or {}
    if db:
        rows.append(("Database", f"{db.get('kind')} — schema `{db.get('schema','?')}`"))
    redis = svc.get("redis") or {}
    if redis:
        rows.append(("Redis key prefix", f"`{redis.get('key_prefix','?')}`"))
    idx = svc.get("gitnexus_index") or {}
    if idx:
        rows.append(("GitNexus index", f"`{idx.get('name')}` ({idx.get('strategy','?')})"))
    rows = [(k, v) for k, v in rows if v]
    if rows:
        lines.append("| Field | Value |")
        lines.append("|---|---|")
        for k, v in rows:
            lines.append(f"| {k} | {v} |")
        lines.append("")

    if svc.get("notes"):
        lines.append("## Notes")
        lines.append("")
        lines.append(svc["notes"].strip())
        lines.append("")

    # Incoming
    lines.append(f"## Incoming edges ({len(edges_in)})")
    lines.append("")
    if not edges_in:
        lines.append("_None recorded._")
    else:
        for e in sorted(edges_in, key=lambda x: (x.get("kind", ""), x.get("from", ""))):
            lines.append(edge_line(e, "incoming"))
    lines.append("")

    # Outgoing
    lines.append(f"## Outgoing edges ({len(edges_out)})")
    lines.append("")
    if not edges_out:
        lines.append("_None recorded._")
    else:
        for e in sorted(edges_out, key=lambda x: (x.get("kind", ""), x.get("to", ""))):
            lines.append(edge_line(e, "outgoing"))
    lines.append("")

    # Feign clients exposed (this service publishes a *-client jar)
    fce = svc.get("feign_clients_exposed")
    if fce:
        lines.append("## Feign clients exposed")
        lines.append("")
        lines.append("```yaml")
        lines.append(yaml_block(fce))
        lines.append("```")
        lines.append("")

    # Consumes block (raw, for completeness — already implied by outgoing edges
    # but keeping the package detail close at hand)
    if svc.get("consumes"):
        lines.append("## Declared `consumes:` (raw)")
        lines.append("")
        lines.append("```yaml")
        lines.append(yaml_block(svc["consumes"]))
        lines.append("```")
        if svc.get("consumes_evidence"):
            lines.append("")
            lines.append(f"Evidence: `{svc['consumes_evidence']}`")
        lines.append("")

    # Evidence pointers from identity fields
    evidence: list[tuple[str, str]] = []
    for field in ("chart", "db", "redis", "kafka"):
        v = svc.get(field) or {}
        if isinstance(v, dict) and v.get("evidence"):
            evidence.append((field, v["evidence"]))
    if evidence:
        lines.append("## Identity evidence")
        lines.append("")
        for f, ev in evidence:
            lines.append(f"- `{f}` → `{ev}`")
        lines.append("")

    return "\n".join(lines)


def render_index(services_by_role: dict[str, list[str]]) -> str:
    lines = ["# Service Pages", "",
             "Auto-generated from `inventory.yaml` by `scripts/inventory-to-pages.py`. Do not hand-edit.",
             ""]
    for role in ROLE_ORDER:
        sids = services_by_role.get(role, [])
        if not sids:
            continue
        lines.append(f"## {role} ({len(sids)})")
        lines.append("")
        for sid in sorted(sids):
            lines.append(f"- [{sid}]({sid}.md)")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default=str(INVENTORY))
    parser.add_argument("--out", default=str(OUT_DIR))
    args = parser.parse_args()

    with open(args.inventory) as fh:
        inventory = yaml.safe_load(fh)
    services = inventory.get("services", {})
    edges = inventory.get("edges", [])

    indexed = {sid: svc for sid, svc in services.items() if svc.get("gitnexus_index")}

    edges_by_src: dict[str, list[dict]] = defaultdict(list)
    edges_by_dst: dict[str, list[dict]] = defaultdict(list)
    for e in edges:
        if e.get("from"):
            edges_by_src[e["from"]].append(e)
        if e.get("to"):
            edges_by_dst[e["to"]].append(e)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # This directory is fully generated from inventory.yaml. Remove stale pages
    # first so deleted or renamed services do not linger between runs.
    for existing in out_dir.glob("*.md"):
        existing.unlink()

    by_role: dict[str, list[str]] = defaultdict(list)
    for sid, svc in indexed.items():
        by_role[svc.get("role", "backend")].append(sid)
        page = render_service(sid, svc,
                              edges_in=edges_by_dst.get(sid, []),
                              edges_out=edges_by_src.get(sid, []))
        (out_dir / f"{sid}.md").write_text(page)

    (out_dir / "README.md").write_text(render_index(by_role))
    print(f"Wrote {len(indexed)} service pages + README.md to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
