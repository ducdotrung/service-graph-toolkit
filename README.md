# Service Graph Toolkit

Evidence-backed service graphs, code context, and reusable workflows for
multi-repository systems. It is a hackathon-friendly toolkit, not an
application or a host for private source code.

## What it does

- keeps an authored service inventory with evidence for cross-service edges;
- indexes each service with GitNexus for code-level search and impact analysis;
- generates maps, service pages, JSON, and GitNexus group definitions;
- provides script-first skills for discovery, impact, QA scope, releases,
  incidents, implementation planning, and leader-facing PoC reports.

Private sources stay outside Git. Each graph project has tracked metadata and
an ignored local source-root override.

## Quick start

```bash
npm install -g gitnexus@latest
python3 scripts/graph.py validate sock-shop
python3 scripts/graph.py generate sock-shop
```

To fetch the public multi-repository demo and index it locally:

```bash
scripts/fetch-sock-shop.sh
cp projects/sock-shop/.local.yaml.example projects/sock-shop/.local.yaml
python3 scripts/graph.py index sock-shop
python3 scripts/graph.py generate sock-shop
python3 scripts/graph.py mcp-config sock-shop
```

Generated files are written to `.graph-work/<project>/`. The MCP command
creates a credential-free local stdio configuration snippet.

## Project layout

```text
projects/<project-id>/
  project.yaml       # project identity
  inventory.yaml     # authored services, edges, evidence
  .local.yaml        # ignored source_root override
  README.md          # project-specific bootstrap and limits
```

`inventory.yaml` paths are relative to `source_root`; never commit private
remotes, absolute paths, endpoints, or credentials.

See [docs/PROJECTS.md](docs/PROJECTS.md) for the project contract and
[QUICKSTART.md](QUICKSTART.md) for commands.

## Skills

- `gitnexus-implement` — evidence-backed implementation planning.
- `graph-feature-discovery` — identify ownership and dependencies.
- `graph-change-impact` — cross-service change analysis.
- `graph-test-scope` — risk-based QA/regression scope.
- `graph-release-readiness` — release evidence and rollback conditions.
- `graph-incident-triage` — bounded, read-only path investigation.
- `graph-poc-report` — leader-facing adoption report.

## Documentation

- [Project model](docs/PROJECTS.md)
- [Quick start](QUICKSTART.md)
- [Query and workflow usage](docs/USAGE.md)
- [Client adapters and portable automation](shared/AGENTS.md)
- [Future shared workstation setup](docs/WORKSTATION.md)
- [Active implementation roadmap](docs/ROADMAP.md)
- [Public Sock Shop demo](projects/sock-shop/README.md)

Older material under `docs/CURRENT/`, the original runbook, and deployment
templates are retained as research/operational reference. They are not the
default local workflow until converted to the project-scoped model.
