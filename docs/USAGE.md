# How to Query the Microservice Call Graph

This guide shows how to use GitNexus to explore a microservice platform. The
examples assume you keep one index per service and maintain a small
`inventory.yaml` or equivalent manifest for cross-service edges.

`inventory.yaml` is the authored source of truth in this repo. Files such as
`group.yaml`, `views/service-map.md`, `views/inventory.json`, and
`views/services/*.md` should be treated as local generated outputs.

## One-time setup

```bash
npm install -g gitnexus@latest

# Example pilot indexes
gitnexus analyze --skip-git --name gateway-service   services/gateway-service
gitnexus analyze --skip-git --name identity-service  services/identity-service
gitnexus analyze --skip-git --name bio-service           services/bio-service
gitnexus analyze --skip-git --name user-service      services/user-service
gitnexus analyze --skip-git --name platform-mcp      tools/platform-mcp
gitnexus analyze --name assistant-service            apps/assistant-service
```

## Core query types

### `query`

Use `query` when you know the concept but not the symbol name.

```text
@gitnexus query({search_query: "KafkaListener", repo: "bio-service"})
```

Good inputs:
- class names
- annotation names
- domain terms
- business actions such as `"refresh token"` or `"invoice export"`

### `context`

Use `context` when you already know the symbol name and want callers, callees,
and related flows.

```text
@gitnexus context({name: "IdentityClient", repo: "identity-service"})
```

### `impact`

Use `impact` before changing a class, method, DTO, or event contract.

```text
@gitnexus impact({target: "IdentityClient", direction: "upstream", repo: "identity-service"})
```

Direction meanings:
- `upstream`: who depends on it
- `downstream`: what it depends on

### `trace`

Use `trace` when you want the path between two symbols.

```text
@gitnexus trace({from: "LoginController", to: "UserRepository", repo: "identity-service"})
```

## What the code graph sees

A single GitNexus index is good at:
- imports and method calls inside one service
- controller, service, repository, and handler relationships
- many event producer and consumer paths inside the indexed code

A single GitNexus index is not enough for:
- gateway route ownership from YAML
- service-to-service HTTP hops across different indexes
- runtime MCP wiring
- shared database contracts

That second category belongs in a manifest such as `inventory.yaml`.

## Combining GitNexus with a service manifest

Example question: "Who calls `identity-service`?"

```bash
# Cross-service edges from your manifest
grep -A 5 "to: identity-service" inventory.yaml
```

```text
# In-process callers inside the service itself
@gitnexus impact({target: "IdentityController", direction: "upstream", repo: "identity-service"})
```

Useful edge kinds in a manifest:

| Kind | Meaning |
|------|---------|
| `gateway_route` | HTTP path prefix routes into a service |
| `feign_call` | Service A calls service B over HTTP |
| `kafka` | Producer and consumer relationship by topic |
| `mcp_tool_use` | An app depends on tools exposed by an MCP server |
| `shared_db` | Two services rely on the same schema or tables |

## Common questions

### Who calls `identity-service`?

```bash
grep -B 5 "to: identity-service" inventory.yaml
```

```text
@gitnexus impact({target: "IdentityController", direction: "upstream", repo: "identity-service"})
```

### Where does `/users/*` route?

```bash
grep -A 3 "path_prefix: /users/" inventory.yaml
```

### What Kafka listeners does `bio-service` have?

```text
@gitnexus query({search_query: "KafkaListener", repo: "bio-service"})
```

### What tools does `platform-mcp` expose?

```text
@gitnexus query({search_query: "McpTool", repo: "platform-mcp"})
```

### What HTTP clients does `user-service` expose or consume?

```text
@gitnexus query({search_query: "FeignClient", repo: "user-service"})
```

## CLI equivalents

```bash
gitnexus query "KafkaListener" -r bio-service
gitnexus context IdentityClient -r identity-service
gitnexus impact IdentityClient --direction upstream -r identity-service
gitnexus trace LoginController UserRepository -r identity-service
gitnexus list
gitnexus check --cycles -r bio-service
gitnexus cypher "MATCH (n) RETURN count(n)" -r identity-service
```

## Extending the graph

1. Add the service to your manifest.
2. Run `gitnexus analyze --name <service-id> <path>`.
3. Add any cross-service edges that code parsing will not discover.
4. Re-generate local artifacts from `inventory.yaml`.
5. Re-run your validation queries.
6. If you use `gitnexus group`, re-sync the generated bridge after indexes change.
