#!/usr/bin/env python3
"""filter-bridge.py — post-sync precision filter for gitnexus group cross-links.

PROBLEM
-------
`gitnexus group sync` matches HTTP contracts by path only.  On this platform
the BIO service deliberately re-exposes upstream paths, so the extractor
produces ~34% false-positive cross-repo links (e.g. user-platform-client →
bio-controller when the client actually calls user-platform-service).

SOLUTION
--------
Use inventory.yaml as the scope authority.  For each auto-extracted cross-repo
HTTP cross-link, check whether inventory records a feign_call / kafka /
mcp_tool_use edge between those two services.  Three outcomes:

  inventory says A→B  |  group says A→B  |  verdict
  --------------------+------------------+------------------
  YES                 |  YES             |  KEEP
  YES                 |  NO              |  inventory-only (extractor gap)
  NO                  |  YES             |  DROP (false positive)

Manifest links (gateway routes, MCP tools, shared DB injected by the
projector from inventory.yaml) are already authoritative — they are always
kept.

USAGE
-----
    python3 scripts/filter-bridge.py [options]

    --inventory  PATH   default: inventory.yaml
    --group      NAME   default: platform-projected
    --out        PATH   write filtered cross-links JSON (default: stdout)
    --report     PATH   write drift Markdown report   (default: drift-report.md)
    --drop-only         only print dropped links, skip kept/inventory-only
    --dry-run           parse + classify, do not write files

OUTPUT
------
    <out>           filtered-bridge.json — kept + manifest cross-links only
    <report>        drift-report.md      — three sections: kept / dropped / inventory-only
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY = REPO_ROOT / "inventory.yaml"
OUT_JSON = REPO_ROOT / "views" / "filtered-bridge.json"
OUT_REPORT = REPO_ROOT / "views" / "drift-report.md"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_inventory(path: Path) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)


def load_group_contracts(group_name: str) -> dict:
    """Call `gitnexus group contracts <name> --json` and return parsed JSON."""
    result = subprocess.run(
        ["gitnexus", "group", "contracts", group_name, "--json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.exit(f"ERROR: gitnexus group contracts failed:\n{result.stderr}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: could not parse gitnexus output as JSON: {e}")


# ---------------------------------------------------------------------------
# Build inventory truth map
# ---------------------------------------------------------------------------

def build_inventory_pairs(inventory: dict, group_yaml_path: Path) -> dict[str, set[tuple[str, str]]]:
    """Return a map of contract-type → set of (from_group_path, to_group_path).

    Contract type mapping (group type → inventory kind):
      http   → feign_call
      topic  → kafka
      custom → mcp_tool_use

    gateway_route / shared_db are already projected as manifest links,
    so they never appear as auto-extracted cross-links.
    """
    KIND_TO_TYPE = {
        "feign_call":   "http",
        "kafka":        "topic",
        "mcp_tool_use": "custom",
    }

    if group_yaml_path.exists():
        with open(group_yaml_path) as fh:
            grp = yaml.safe_load(fh)
        name_to_path: dict[str, str] = {v: k for k, v in (grp.get("repos") or {}).items()}
    else:
        name_to_path = {}

    services = inventory.get("services") or {}

    def svc_to_path(service_id: str) -> str | None:
        svc = services.get(service_id) or {}
        gi = svc.get("gitnexus_index") or {}
        gname = gi.get("name") or service_id
        return name_to_path.get(gname)

    pairs: dict[str, set[tuple[str, str]]] = {"http": set(), "topic": set(), "custom": set()}
    for edge in (inventory.get("edges") or []):
        contract_type = KIND_TO_TYPE.get(edge.get("kind", ""))
        if not contract_type:
            continue
        fp = svc_to_path(edge.get("from", ""))
        tp = svc_to_path(edge.get("to", ""))
        if fp and tp:
            pairs[contract_type].add((fp, tp))
    return pairs


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_cross_links(
    cross_links: list[dict],
    inventory_pairs: dict[str, set[tuple[str, str]]],
) -> tuple[list[dict], list[dict], list[dict]]:
    """Split cross-links into (kept, dropped, manifest).

    kept      — auto-extracted AND backed by a matching-kind inventory edge,
                OR intra-repo (same-repo *-client → *-app)
    dropped   — auto-extracted AND no same-kind inventory edge (false positive)
    manifest  — injected by projector; always kept
    """
    kept: list[dict] = []
    dropped: list[dict] = []
    manifest: list[dict] = []

    for link in cross_links:
        match_type = link.get("matchType", "")

        if match_type == "manifest":
            manifest.append(link)
            continue

        from_repo     = link.get("from", {}).get("repo", "")
        to_repo       = link.get("to",   {}).get("repo", "")
        contract_type = link.get("type", "http")

        # Same-repo intra-service links (e.g. *-client → *-app): always keep
        if from_repo == to_repo:
            kept.append(link)
            continue

        # Cross-repo: check inventory for same contract type
        allowed = inventory_pairs.get(contract_type, set())
        if (from_repo, to_repo) in allowed:
            kept.append(link)
        else:
            dropped.append(link)

    return kept, dropped, manifest


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _link_summary(link: dict) -> str:
    fr = link.get("from", {})
    to = link.get("to", {})
    contract = link.get("contractId", "?")
    confidence = link.get("confidence", "?")
    from_sym = fr.get("symbolRef", {}).get("name", "?")
    to_sym   = to.get("symbolRef", {}).get("name", "?")
    return (
        f"  - `{fr.get('repo')}::{from_sym}` → "
        f"`{to.get('repo')}::{to_sym}` "
        f"| `{contract}` | confidence={confidence}"
    )


def render_report(
    kept: list[dict],
    dropped: list[dict],
    manifest: list[dict],
    inventory_only: list[tuple[str, str, str]],  # (from_svc, to_svc, kind)
) -> str:
    lines = [
        "# Bridge Filter Drift Report",
        "",
        f"**kept** (auto-extracted, inventory-confirmed): {len(kept)}  ",
        f"**manifest** (projector-injected, always trusted): {len(manifest)}  ",
        f"**dropped** (auto-extracted, NOT in inventory): {len(dropped)}  ",
        f"**inventory-only** (inventory says yes, group missing): {len(inventory_only)}  ",
        "",
    ]

    if dropped:
        lines += [
            "## Dropped (false positives)",
            "",
            "Group's path-only matching produced these; inventory has no matching edge.",
            "Likely cause: BIO path re-exposure (bio-service mirrors upstream paths).",
            "",
        ]
        # Group by pair
        by_pair: dict[str, list[dict]] = defaultdict(list)
        for lnk in dropped:
            key = f"{lnk.get('from', {}).get('repo')} → {lnk.get('to', {}).get('repo')}"
            by_pair[key].append(lnk)
        for pair, links in sorted(by_pair.items(), key=lambda x: -len(x[1])):
            lines.append(f"### {pair} ({len(links)} links)")
            lines.append("")
            for lnk in links:
                lines.append(_link_summary(lnk))
            lines.append("")

    if inventory_only:
        lines += [
            "## Inventory-only edges (extractor coverage gaps)",
            "",
            "Inventory records these edges but `group sync` found no matching contract.",
            "Possible causes: service not indexed, topic constant not resolved, dynamic dispatch.",
            "",
        ]
        by_kind: dict[str, list] = defaultdict(list)
        for f, t, k in inventory_only:
            by_kind[k].append((f, t))
        for kind, pairs in sorted(by_kind.items()):
            lines.append(f"### {kind} ({len(pairs)})")
            lines.append("")
            for f, t in sorted(pairs):
                lines.append(f"  - `{f}` → `{t}`")
            lines.append("")

    if kept:
        lines += [
            "## Kept (auto-extracted, inventory-confirmed)",
            "",
        ]
        by_pair2: dict[str, list[dict]] = defaultdict(list)
        for lnk in kept:
            if lnk.get("from", {}).get("repo") != lnk.get("to", {}).get("repo"):
                key = f"{lnk.get('from', {}).get('repo')} → {lnk.get('to', {}).get('repo')}"
                by_pair2[key].append(lnk)
        for pair, links in sorted(by_pair2.items()):
            lines.append(f"### {pair} ({len(links)} links)")
            lines.append("")
            for lnk in links:
                lines.append(_link_summary(lnk))
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Inventory-only edges: in inventory but missing from bridge
# ---------------------------------------------------------------------------

def find_inventory_only(
    inventory: dict,
    group_yaml_path: Path,
    all_cross_links: list[dict],
) -> list[tuple[str, str, str]]:
    """Find inventory edges that have no matching cross-link in the bridge.

    Uses same-type matching: a feign_call edge is only 'covered' by an http
    cross-link; a kafka edge is only covered by a topic cross-link.
    """
    KIND_TO_TYPE = {
        "feign_call":   "http",
        "kafka":        "topic",
        "mcp_tool_use": "custom",
    }

    # Build (type, from_repo, to_repo) set from bridge
    present: set[tuple[str, str, str]] = set()
    for lnk in all_cross_links:
        fp = lnk.get("from", {}).get("repo", "")
        tp = lnk.get("to",   {}).get("repo", "")
        ct = lnk.get("type", "http")
        if fp and tp and fp != tp:
            present.add((ct, fp, tp))
            present.add((ct, tp, fp))  # group may emit either direction

    if group_yaml_path.exists():
        with open(group_yaml_path) as fh:
            grp = yaml.safe_load(fh)
        name_to_path: dict[str, str] = {v: k for k, v in (grp.get("repos") or {}).items()}
    else:
        name_to_path = {}

    services = inventory.get("services") or {}

    def svc_to_path(service_id: str) -> str | None:
        svc = services.get(service_id) or {}
        gi = svc.get("gitnexus_index") or {}
        gname = gi.get("name") or service_id
        return name_to_path.get(gname)

    missing = []
    for edge in (inventory.get("edges") or []):
        kind = edge.get("kind", "")
        ct = KIND_TO_TYPE.get(kind)
        if not ct:
            continue
        fp = svc_to_path(edge.get("from", ""))
        tp = svc_to_path(edge.get("to", ""))
        if fp and tp and (ct, fp, tp) not in present:
            missing.append((edge.get("from", ""), edge.get("to", ""), kind))
    return missing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inventory", default=str(INVENTORY))
    parser.add_argument("--group",     default="platform-projected")
    parser.add_argument("--out",       default=str(OUT_JSON))
    parser.add_argument("--report",    default=str(OUT_REPORT))
    parser.add_argument("--drop-only", action="store_true")
    parser.add_argument("--dry-run",   action="store_true")
    args = parser.parse_args()

    inventory      = load_inventory(Path(args.inventory))
    contracts_data = load_group_contracts(args.group)
    cross_links    = contracts_data.get("crossLinks", [])
    contracts      = contracts_data.get("contracts", [])

    group_yaml_path = REPO_ROOT / "group.yaml"
    inventory_pairs = build_inventory_pairs(inventory, group_yaml_path)

    kept, dropped, manifest = classify_cross_links(cross_links, inventory_pairs)
    inventory_only = find_inventory_only(inventory, group_yaml_path, cross_links)

    # Summary to stdout
    total_auto = len([l for l in cross_links if l.get("matchType") != "manifest"])
    total_cross_repo = len([l for l in cross_links if l.get("from", {}).get("repo") != l.get("to", {}).get("repo")])
    intra = len([l for l in cross_links if l.get("matchType") != "manifest" and l.get("from", {}).get("repo") == l.get("to", {}).get("repo")])

    print(f"Contracts in bridge : {len(contracts)}")
    print(f"Cross-links total   : {len(cross_links)}")
    print(f"  manifest          : {len(manifest)}")
    print(f"  auto-extracted    : {total_auto}")
    print(f"    intra-repo      : {intra}")
    print(f"    cross-repo      : {total_cross_repo - len(manifest)}")
    print(f"      kept          : {len(kept) - intra}")
    print(f"      dropped       : {len(dropped)}")
    fp_rate = len(dropped) / max(total_cross_repo - len(manifest), 1) * 100
    print(f"  false-positive %%  : {fp_rate:.0f}%%")
    print(f"Inventory-only edges: {len(inventory_only)}")

    if args.drop_only:
        for lnk in dropped:
            print(_link_summary(lnk))
        return 0

    if args.dry_run:
        print("\n(dry-run — no files written)")
        return 0

    # Write filtered cross-links JSON
    filtered = {
        "contracts": contracts,
        "crossLinks": kept + manifest,
        "_filter_meta": {
            "dropped_count": len(dropped),
            "inventory_only_count": len(inventory_only),
            "group": args.group,
            "inventory": args.inventory,
        }
    }
    out_path = Path(args.out)
    out_path.write_text(json.dumps(filtered, indent=2, ensure_ascii=False) + "\n")
    print(f"\nWrote {out_path} ({len(filtered['crossLinks'])} cross-links)")

    # Write drift report
    report = render_report(kept, dropped, manifest, inventory_only)
    report_path = Path(args.report)
    report_path.write_text(report)
    print(f"Wrote {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
