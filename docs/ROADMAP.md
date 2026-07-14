# Service Graph Toolkit Roadmap

This is the active implementation roadmap. It supersedes the older
single-platform assumptions in `docs/NEXT-PHASE.md`.

## Completed foundation

- Project-scoped manifests under `projects/<project-id>/`, ignored local source
  roots, namespaced GitNexus indexes, and generated `.graph-work/` outputs.
- Fictional example project and public multi-repository Sock Shop demo with a
  reproducible fetch script.
- Deterministic graph validation/generation commands and local GitNexus MCP
  configuration generation.
- Shared operating rules, model-selection guidance, portable context/web-fetch
  scripts, and thin Codex/Claude/Pi adapters.
- Workflow skills for implementation planning, feature discovery, impact, test
  scope, release readiness, incident triage, and PoC reporting.
- Local-first workstation guidance; legacy deployment templates remain reference
  material only.

## Local Graph MCP server

Build a local stdio server in this repository. It must wrap existing scripts
and GitNexus rather than duplicate graph logic.

Read-only v1 tools:

- `list_projects`
- `get_project_context`
- `get_service_details`
- `get_service_map`
- `validate_project`
- `search_code`
- `get_symbol_context`
- `get_change_impact`

Requirements:

- Project ID is required for every project-scoped request.
- Return the bounded source envelope in `shared/mcp/tool-contracts.md`.
- Use project-namespaced GitNexus index names.
- Enforce output limits and return artifact/source paths as evidence.
- Do not expose arbitrary shell execution, indexing, refresh, deployment, or
  secrets through v1 MCP tools.

Implemented as `mcp-server/index.mjs`; remaining acceptance work is an
end-to-end client smoke test after dependencies are installed.

## Completed: deterministic quality gates

Add automated tests for `scripts/graph.py`, project manifests, and generated
artifacts. At minimum test invalid service/edge references, unsafe inventory
paths, index-name namespacing, `init`, and end-to-end generation for both
bundled projects. Add a link/documentation check and run `agent-doctor.sh` in
the same test command.

Delivered by `scripts/check.sh`, which runs graph and documentation tests plus
`agent-doctor.sh` without requiring private sources or GitNexus indexes.

## Completed: improve web evidence extraction

Replace the dependency-free HTML stripping in `scripts/fetch-web.mjs` with a
proper readability-to-Markdown implementation. Keep the current CLI contract,
source metadata, timeout, response-size limit, PDF sidecar behavior, and no
credential requirement for direct public fetches. Make search a separate,
optional credential-backed tool rather than embedding credentials in this repo.

Acceptance: a representative article retains headings, paragraphs, links, and
code blocks in Markdown; a PDF creates both cited Markdown metadata and a
binary sidecar.

## Completed: hackathon demonstration path

Create one script and guide that performs: fetch Sock Shop sources, configure
local source root, validate, index, generate, run one cross-service impact
query, and produce a short `graph-poc-report` artifact. The script must stop
with actionable prerequisites if GitNexus or required language tooling is
missing; it must not start containers or use remote credentials.

Acceptance: a new participant can demonstrate graph value in one guided flow
and explain the evidence to a judge or engineering leader.

## Later: shared workstation mode

Convert `deploy/` from legacy reference to parameterized, project-aware
templates only after the local MCP server and quality gates are stable. Use a
dedicated service account, protected environment files, authenticated remote
MCP, project authorization, bounded audit records, and scheduled
index/generate-only jobs. Never make cloning, pulling, arbitrary command
execution, or write-capable MCP tools default behavior.

Acceptance: deployment docs and templates can host two independent projects
without hard-coded paths, credentials, or cross-project index collisions.
