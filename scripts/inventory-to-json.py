#!/usr/bin/env python3
"""Emit inventory.json: a flat JSON view of inventory.yaml for AI agents
and tools that prefer JSON to YAML.

The JSON preserves every key from the YAML. Comments are lost (JSON limitation
— consult the YAML for prose context), but data is identical.

A small JSON Schema is written alongside (inventory.schema.json) capturing
the top-level shape so consumers can validate. The schema is illustrative,
not exhaustive — every field that varies per service-role would balloon it.

Usage:  python3 scripts/inventory-to-json.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY = REPO_ROOT / "inventory.yaml"
OUT_JSON = REPO_ROOT / "views" / "inventory.json"
OUT_SCHEMA = REPO_ROOT / "views" / "inventory.schema.json"


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.local/inventory.schema.json",
    "title": "Microservice Platform Inventory",
    "type": "object",
    "required": ["schema_version", "repos", "services", "edges"],
    "properties": {
        "schema_version": {"type": "integer"},
        "last_updated": {"type": "string"},
        "scope": {"type": "string"},
        "repos": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "type": {"type": "string", "enum": ["monorepo", "single-service", "shared-lib"]},
                    "primary_lang": {"type": "string"},
                    "build": {"type": "string"},
                },
            },
        },
        "services": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["repo", "role"],
                "properties": {
                    "repo": {"type": "string"},
                    "role": {"type": "string"},
                    "framework": {"type": "string"},
                    "port": {"type": ["integer", "null"]},
                    "paths": {"type": "object"},
                    "chart": {"type": "object"},
                    "db": {"type": "object"},
                    "redis": {"type": "object"},
                    "kafka": {"type": "object"},
                    "consumes": {"type": "array"},
                    "consumes_evidence": {"type": "string"},
                    "feign_clients_exposed": {"type": "array"},
                    "notes": {"type": "string"},
                    "gitnexus_index": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "analyze_path": {"type": "string"},
                            "strategy": {"type": "string"},
                            "skip_git": {"type": "boolean"},
                        },
                    },
                },
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["from", "to", "kind"],
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "kind": {
                        "type": "string",
                        "enum": ["gateway_route", "feign_call", "kafka",
                                 "mcp_tool_use", "shared_db"],
                    },
                    "evidence": {"type": "string"},
                    "notes": {"type": "string"},
                    "path": {"type": "string"},
                    "topic": {"type": "string"},
                    "tools_used": {"type": "array", "items": {"type": "string"}},
                    "via_client": {"type": "string"},
                    "via_clients": {"type": "array", "items": {"type": "string"}},
                    "target_uri": {"type": "string"},
                    "confidence": {"type": "string"},
                },
            },
        },
        "infrastructure": {"type": "object"},
        "resolved_questions": {"type": "array"},
        "open_questions": {"type": "array"},
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default=str(INVENTORY))
    parser.add_argument("--out", default=str(OUT_JSON))
    parser.add_argument("--schema", default=str(OUT_SCHEMA))
    args = parser.parse_args()

    with open(args.inventory) as fh:
        inventory = yaml.safe_load(fh)

    def _default(o):
        # PyYAML decodes YYYY-MM-DD as datetime.date; JSON has no date type.
        return o.isoformat() if hasattr(o, "isoformat") else str(o)

    with open(args.out, "w") as fh:
        json.dump(inventory, fh, indent=2, ensure_ascii=False, sort_keys=False,
                  default=_default)
        fh.write("\n")

    with open(args.schema, "w") as fh:
        json.dump(SCHEMA, fh, indent=2)
        fh.write("\n")

    print(f"Wrote {args.out} ({len(inventory.get('services', {}))} services, "
          f"{len(inventory.get('edges', []))} edges)")
    print(f"Wrote {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
