# Developer Guide — Microservice Code Intelligence Platform

Audience: developers using Claude Code, Codex, or OpenCode  
Last updated: 2026-07-08

## How the system works

The platform has two layers:

```text
Layer 1 — Per-service indexes
  Each service is analyzed individually.
  Best for symbols, calls, traces, and local impact.

Layer 2 — Cross-service overlay
  Manifest plus optional group bridge.
  Best for routes, service-to-service links, topics, and runtime wiring.
```

## MCP setup

Use a project-level or global MCP config that points to:

`http://<graph-host>:4748/mcp`

Then verify:

```text
@gitnexus list_repos
```

## Web UI

Use the UI when you want to browse, not automate. Many teams also point the UI
at a shared LiteLLM proxy instead of asking every developer to manage a
personal key.

## Core tool usage

### Discover indexed repos

```text
@gitnexus list_repos
```

### Find code by concept

```text
@gitnexus query({search_query: "PaymentProviderProcessor", repo: "billing-integration-service"})
```

### Inspect callers and callees

```text
@gitnexus context({name: "PaymentProviderProcessor", repo: "billing-integration-service"})
```

### Check blast radius

```text
@gitnexus impact({target: "PaymentProviderProcessor", direction: "upstream", repo: "billing-integration-service"})
```

### Trace execution path

```text
@gitnexus trace({from: "ProviderRegistryController", to: "BillingRecordRepository", repo: "billing-integration-service"})
```

### Search across repos

```text
@gitnexus query({search_query: "provider processor factory", group: "platform-graph"})
```

### Impact across repos

```text
@gitnexus impact({target: "BillingRecord", group: "platform-graph", direction: "upstream"})
```

## Skills

Skills are reusable prompts or workflows that combine GitNexus tools in a
repeatable order. A good skill should:

- declare when to use it
- specify the tool sequence
- define the output checklist

Typical install layout:

- `skills/<skill-name>/SKILL.md` in this repo
- `~/.claude/skills/<skill-name>/SKILL.md` for a personal install

## Good workflow

When implementing a feature:

1. identify the owning service
2. query for the relevant pattern
3. inspect the main symbol with `context`
4. run `impact` before editing shared contracts
5. check the manifest for service-boundary effects

## Limits to remember

- route ownership is often a config question
- service-to-service HTTP links may need manifest help
- event producer discovery may require wider indexing scope
- not every architecture fact belongs in the code graph
