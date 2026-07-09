# Documentation Index

Last updated: 2026-07-08

This directory holds the public-facing documentation for a GitNexus-based
microservice call graph project. The aim is to keep the repo useful as a
reference implementation without exposing private environment details,
company-specific service inventories, or feature planning artifacts.

## Core docs

| File | Purpose | Read when |
|------|---------|-----------|
| [`CURRENT/platform-overview.md`](CURRENT/platform-overview.md) | Deployment and chart architecture patterns | You need the big-picture platform layout |
| [`CURRENT/code-graph-strategy.md`](CURRENT/code-graph-strategy.md) | Why the graph is split into code indexes and a service overlay | You are evaluating or extending the approach |
| [`CURRENT/capability-analysis.md`](CURRENT/capability-analysis.md) | What GitNexus answers well and where it still needs help | You want clear expectations |
| [`CURRENT/poc-validation-results.md`](CURRENT/poc-validation-results.md) | Example validation outcomes from a pilot | You want evidence for the approach |
| [`CURRENT/gitnexus-group-feature.md`](CURRENT/gitnexus-group-feature.md) | How `gitnexus group` fits into a multi-repo graph | You are considering cross-repo search and impact |
| [`CURRENT/platform-intelligence-brief.md`](CURRENT/platform-intelligence-brief.md) | Presentation-friendly overview of the system | You need a non-developer summary |
| [`CURRENT/developer-guide.md`](CURRENT/developer-guide.md) | Day-to-day usage for developers | You want MCP, UI, and workflow guidance |
| [`CURRENT/developer-mcp-setup.md`](CURRENT/developer-mcp-setup.md) | Minimal connection instructions for remote MCP access | You only need setup steps |
| [`CURRENT/implement-skill-guide.md`](CURRENT/implement-skill-guide.md) | How to use a reusable implementation skill with the graph | You want structured feature-scaffolding help |
| [`USAGE.md`](USAGE.md) | Query patterns and examples | You want concrete commands |
| [`gitnexus-runbook.md`](gitnexus-runbook.md) | Operational indexing and troubleshooting guide | You are maintaining the graph |

## Suggested reading order

If you are new to the repo:
1. Read this file.
2. Read [`CURRENT/platform-overview.md`](CURRENT/platform-overview.md).
3. Read [`CURRENT/code-graph-strategy.md`](CURRENT/code-graph-strategy.md).
4. Read [`CURRENT/capability-analysis.md`](CURRENT/capability-analysis.md).
5. Use [`USAGE.md`](USAGE.md) and [`gitnexus-runbook.md`](gitnexus-runbook.md) when you start running commands.

If you are preparing a presentation:
1. Start with [`CURRENT/platform-intelligence-brief.md`](CURRENT/platform-intelligence-brief.md).
2. Pull supporting detail from [`CURRENT/poc-validation-results.md`](CURRENT/poc-validation-results.md).
3. Use [`CURRENT/gitnexus-group-feature.md`](CURRENT/gitnexus-group-feature.md) only if the audience cares about the implementation path.

If you are extending the system:
1. Read [`CURRENT/code-graph-strategy.md`](CURRENT/code-graph-strategy.md).
2. Read [`CURRENT/gitnexus-group-feature.md`](CURRENT/gitnexus-group-feature.md).
3. Read [`CURRENT/implement-skill-guide.md`](CURRENT/implement-skill-guide.md).
4. Follow [`gitnexus-runbook.md`](gitnexus-runbook.md) for indexing and validation.

## Scope notes

- Historical internal planning docs were removed on purpose.
- Private repo lists, internal hosts, and company feature examples were removed.
- The remaining docs keep the architecture, process, and technical lessons.

## Updating docs

- Put stable technical guidance in `CURRENT/`.
- Keep examples generic unless they are safe to publish.
- Prefer placeholders over real hostnames, tokens, or private repo paths.
