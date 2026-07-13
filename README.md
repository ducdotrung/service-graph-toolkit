# Microservice Call Graph

This is a reusable, multi-project GitNexus graph toolkit. Start with the
fictional example under `projects/example-platform`; private source repositories
stay outside this checkout and are referenced only by ignored `.local.yaml`
files.

```bash
python3 scripts/graph.py validate example-platform
python3 scripts/graph.py generate example-platform
python3 scripts/graph.py mcp-config example-platform
```

Generated files are written to `.graph-work/<project>/`. To index private code,
copy `projects/example-platform/.local.yaml.example` to `.local.yaml`, set
`source_root`, then run `python3 scripts/graph.py index example-platform`.

## Skills

- `skills/gitnexus-implement/`: evidence-backed implementation planning across services.
- `skills/graph-poc-report/`: leader-facing, script-first proof-of-concept reports.
- `skills/graph-feature-discovery/`: identify feature ownership and dependencies.
- `skills/graph-change-impact/`: evidence-backed cross-service change analysis.
- `skills/graph-test-scope/`: risk-based QA and regression scope.
- `skills/graph-release-readiness/`: release evidence, conditions, and rollback checks.
- `skills/graph-incident-triage/`: bounded, read-only service-path investigation.

This repository is a public-friendly reference workspace for building a
GitNexus-backed microservice architecture map. It is not an application repo.
It is the documentation, manifest, and tooling layer that sits beside a set of
service repositories and turns them into something humans and AI tools can
query.

## What this repo is for

Large microservice platforms usually spread architecture facts across several
places:

- service source code
- gateway configuration
- deployment charts
- CI/CD pipelines
- event contracts
- internal operating knowledge

That makes basic questions expensive to answer:

- Which service owns this route?
- What calls this service?
- What breaks if this contract changes?
- Which Kafka topic connects these services?
- Where is the deploy configuration that makes this runtime path real?

This repo exists to capture those answers in a machine-readable and
maintainable form.

## Core idea

The project combines two layers:

```text
inventory.yaml
  - services
  - source paths
  - route ownership
  - cross-service edges
  - evidence

        | join by service_id
        v

GitNexus per-service indexes
  - symbols
  - calls
  - traces
  - local impact
```

GitNexus is responsible for code structure inside one service index. The
inventory is responsible for cross-service facts that code parsing alone cannot
reliably infer.

## Repo contents

| Path | Purpose |
|------|---------|
| `README.md` | Entry point and project framing |
| `QUICKSTART.md` | Bootstrapping notes for a local setup |
| `inventory.yaml` | Main authored architecture manifest |
| `group.yaml` | Local generated GitNexus bridge definition |
| `REPOS.md` | Generic guidance for organizing sibling source repos |
| `docs/` | Public-safe docs: strategy, usage, runbook, validation |
| `scripts/` | Export and transformation helpers |
| `views/` | Presentation assets plus local generated summaries |
| `results/` | Example index outputs and validation artifacts |
| `memory/` | Working notes, templates, and session scaffolding |
| `skills/` | Reusable AI workflow prompts |

## Suggested reading order

If you are new here:

1. Read this file.
2. Read [`docs/README.md`](docs/README.md).
3. Read [`docs/CURRENT/code-graph-strategy.md`](docs/CURRENT/code-graph-strategy.md).
4. Read [`docs/USAGE.md`](docs/USAGE.md).
5. Read [`docs/gitnexus-runbook.md`](docs/gitnexus-runbook.md).

If you are presenting the project:

1. Read [`docs/CURRENT/platform-intelligence-brief.md`](docs/CURRENT/platform-intelligence-brief.md).
2. Use [`docs/CURRENT/poc-validation-results.md`](docs/CURRENT/poc-validation-results.md) as evidence.

If you are extending the system:

1. Read [`inventory.yaml`](inventory.yaml).
2. Read [`docs/CURRENT/gitnexus-group-feature.md`](docs/CURRENT/gitnexus-group-feature.md).
3. Read [`docs/NEXT-PHASE.md`](docs/NEXT-PHASE.md).

## Working rules

1. Every cross-service edge should have evidence.
2. Code questions belong in GitNexus.
3. Route and deployment questions usually belong in the manifest.
4. `inventory.yaml` is the only authored source of truth for the service map.
5. Generated artifacts should be reproducible from source inputs.
6. Local-only shortcuts such as `.gitnexus/` indexes, regenerated `views/`, and `group.yaml` do not belong in version control.

## What this repo is not

- It is not the source tree for your application services.
- It is not a replacement for deployment automation.
- It is not a promise that all architecture facts can be inferred from code alone.

## Current state

The repository is structured as a reusable template for:

- per-service indexing
- manifest-driven cross-service mapping
- optional `gitnexus group` bridging
- derived documentation and summary views

Before publishing the repo outside a private environment, make sure all
generated data, service names, and environment-specific files are sanitized.

## Regenerate local outputs

When `inventory.yaml` changes, rebuild the derived local files with:

```bash
python3 scripts/inventory-to-group.py
python3 scripts/inventory-to-json.py
python3 scripts/inventory-to-service-map.py
python3 scripts/inventory-to-pages.py
```
