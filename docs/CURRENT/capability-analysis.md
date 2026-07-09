# Capability Analysis: What the PoC Can and Cannot Do

Date: 2026-07-08
Status: analysis

## TL;DR

The PoC graph answers in-service questions well. It does not fully answer
cross-service questions unless you combine GitNexus with a manifest or bridge
layer.

## What the PoC can answer today

### In-service impact

```bash
gitnexus impact IdentityDTO --direction upstream -r identity-service
```

Useful for:
- refactors
- DTO changes
- repository or service-layer blast radius

### In-service flow tracing

```bash
gitnexus trace LoginController UserRepository.findByEmail -r identity-service
```

Useful for:
- understanding the happy path
- onboarding
- debugging where control moves next

### Symbol search

```bash
gitnexus query "KafkaListener" -r bio-service
```

Useful for:
- locating patterns
- finding annotation usage
- discovering likely extension points

### Manual cross-service lookup

```bash
grep -B 2 -A 5 "to: identity-service" inventory.yaml
```

Returns a list such as the API gateway, a BIO, and any tool-facing adapter.
Requires human or agent follow-up inside the relevant service indexes.

## What the PoC cannot answer cleanly yet

### Cross-service blast radius

Question:

"If I rename a client contract, what breaks in other services?"

Problem:
- GitNexus sees one index at a time
- service boundaries usually need manifest edges or `group sync`

### Full request flow across services

Question:

"Draw the full path for a request from gateway to downstream service to event consumer."

Problem:
- some steps are code
- some steps are config
- some steps are asynchronous boundaries

### Config-driven questions

Question:

"Which environment variables or runtime routes does this service depend on?"

Problem:
- much of that data lives in YAML, Helm, or deployment config

### Database dependency questions

Question:

"Which services share a schema or table set?"

Problem:
- this rarely lives in application code in a graph-friendly way

## Recommended combined model

Use:

1. GitNexus for local code structure
2. a manifest for cross-service edges
3. optional `gitnexus group` for cross-repo querying

## Good evaluation questions

| # | Question | Best source today | Status |
|---|----------|-------------------|--------|
| 1 | What breaks if I rename a DTO? | GitNexus `impact` | Works |
| 2 | Which service owns a route? | Manifest | Works |
| 3 | What HTTP endpoints does a service expose? | GitNexus `query` | Works |
| 4 | What is the full path for a request? | Manifest + GitNexus | Partial |
| 5 | If a service is down, what breaks? | Manifest + GitNexus | Partial |
| 6 | Show all imports of `com.example.identity.client.*` | grep + GitNexus | Manual combination |
| 7 | What Kafka topics does a service consume? | GitNexus `query` | Works within one index |
| 8 | Trace sensor or event ingestion across services | Bridge layer | Needs more work |
