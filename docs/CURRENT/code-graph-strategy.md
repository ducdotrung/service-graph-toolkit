# Code Graph Strategy

Last updated: 2026-07-08

## Goal

Build a durable microservice knowledge graph that answers two different kinds of
questions:

- code questions inside a service
- architecture questions across services

GitNexus is strong at the first category. A manifest or overlay is usually
needed for the second.

## Core decisions

1. Index by service, not by giant monorepo.
2. Keep cross-service edges in data, not prose.
3. Start with a narrow pilot before indexing everything.
4. Treat deployment config as architecture evidence, not optional context.

## What a useful graph should answer

- What service owns a given endpoint?
- What calls that endpoint?
- What breaks if a DTO or client changes?
- Which topic connects producer and consumer?
- Which route forwards a request into a given service?

If the system only answers in-service refactoring questions, it is helpful but
not yet a platform map.

## Architecture: code graph plus service overlay

```text
inventory.yaml
  - services
  - paths
  - route ownership
  - cross-service edges
  - evidence

        | join by service_id
        v

GitNexus per-service indexes
  - calls
  - symbols
  - traces
  - local impact
```

## Manifest sketch

```yaml
repos:
  platform-monorepo:
    path: services
    type: monorepo
    services:
      - id: gateway-service
        path: gateway-service
      - id: identity-service
        path: identity-service
      - id: bio-service
        path: bio-service

edges:
  - from: gateway-service
    to: user-service
    kind: gateway_route
    path_prefix: /users/
    evidence: gateway-service/application.yml:42
  - from: bio-service
    to: identity-service
    kind: feign_call
    evidence: bio-service/IdentityClient.java:18
  - from: user-service
    to: kafka
    kind: kafka
    topic: user.created
    evidence: user-service/UserEvents.java:11
```

## Pilot scope

A good pilot includes:

- one gateway
- one service that exposes HTTP endpoints
- one service that calls another service
- one event producer or consumer
- one standalone repo outside the monorepo

## Validation questions

Run the pilot until you can answer:

1. What service owns a path?
2. What service calls another service?
3. What is the local blast radius of a symbol change?
4. What topics connect services?
5. Which answers come from code, and which come from config?

## Expansion order

1. core backend services
2. shared libraries if they affect impact quality
3. tooling and MCP services
4. async and batch services
5. frontend callers if they matter to the graph

## Open questions

1. How much can `gitnexus group sync` infer automatically?
2. Do separate shared-lib indexes help or hurt impact quality?
3. Which edge types must stay manifest-driven forever?

## Non-goals

- forcing every architecture fact into the code graph
- replacing deployment documentation
- promising real-time topology without a refresh pipeline
