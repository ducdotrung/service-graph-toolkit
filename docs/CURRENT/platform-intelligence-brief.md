# Code Intelligence Platform Overview

Audience: management, QA, BA, product  
Last updated: 2026-07-08

## The problem it solves

In a microservice platform, the expensive part of a change is often figuring out
which services are involved, where the implementation pattern lives, and what
else might break.

## What the platform is

The platform is a living map of the codebase. It indexes services, tracks how
they connect, and exposes that knowledge to both humans and AI assistants.

## High-level architecture

```text
Source repos
  -> scheduled indexing
  -> per-service code graph
  -> cross-service overlay
  -> web UI + MCP API
```

## What each audience gets

### QA

- impact analysis before regression testing
- service summaries with dependencies and event usage
- browser-based access

### Business analysts

- service map diagrams
- ownership clues for APIs and responsibilities
- better answers to "which service handles this flow?"

### Developers

- faster discovery of existing patterns
- local and cross-service blast radius checks
- AI-assisted implementation guidance backed by code evidence

### Managers and platform owners

- faster onboarding
- clearer change-risk visibility
- a shared architecture reference that stays closer to reality than slideware

## Access model

- web UI for browsing
- MCP API for AI tooling
- scheduled refresh for keeping indexes current

## Maintenance model

Typical responsibilities:

- keep the service manifest current
- refresh indexes after important changes
- verify bridge quality if group sync is enabled
- regenerate derived documentation and views
