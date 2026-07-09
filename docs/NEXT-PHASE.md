# Next Phase: From Pilot Graph to Maintainable Platform Map

Status: living roadmap

## Phase 1 — Stable per-service indexes

Keep the service indexes predictable:

- index at the service root
- use stable service IDs
- keep shared libraries explicit
- re-run validation after each expansion batch

## Phase 2 — Cross-service manifest

The graph becomes genuinely useful only when code edges and service edges meet
in one model. Keep a machine-readable manifest with:

- service IDs
- source paths
- route ownership
- HTTP client edges
- event topics
- tool exposure and consumption
- evidence pointers to the config or source that supports each edge

## Phase 3 — Group bridge and filtering

Use `gitnexus group` when it reduces manual effort:

1. keep the manifest as the richer source of truth
2. generate or maintain a `group.yaml`
3. run `gitnexus group sync`
4. filter obvious false-positive links with service-aware rules

## Phase 4 — Derived views

Once the manifest is stable, derive human-friendly views instead of hand-writing
them:

- service map diagrams
- one page per service
- JSON exports for automation
- validation reports

## Phase 5 — Scheduled refresh

The target operating model is unattended refresh:

1. pull or sync source repos
2. re-index changed services
3. update the group bridge
4. run post-filters
5. regenerate derived views
6. store refresh metadata

## Phase 6 — Observed edges

Static analysis will miss some runtime behavior. If needed, add a second layer
of observed evidence from logs, tracing, or metrics. Treat that as supporting
evidence, not the only source of truth.

## Phase 7 — Roadmap-quality documentation

The documentation should stay presentation-ready:

- architecture overview for non-developers
- technical runbook for maintainers
- validation evidence for stakeholders
- clear limits of the current graph

## Exit criteria

The project is healthy when:

- service-to-service questions do not require manual source spelunking
- code-only questions are answered by GitNexus
- config-only questions are answered by the manifest
- bridge output is reproducible
- docs are safe to share and still technically useful

Last reviewed: 2026-07-08
