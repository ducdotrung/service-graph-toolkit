---
name: platform-graph
description: "Use when asking about microservice platform architecture, service relationships, cross-service calls, or how services connect. Examples: 'Who calls auth-service?', 'What does the gateway route to?', 'Show me the Feign clients', 'What Kafka topics does bio-service use?'"
---

# Microservice Platform Code Graph

Combines GitNexus code-graph queries with the `inventory.yaml` cross-service
overlay to answer architecture questions about the microservice platform.

## When to Use

- "Who calls auth-service?"
- "What does /user-platform/* route to?"
- "What Feign clients does bio-service expose?"
- "What Kafka listeners does user-platform-service have?"
- "What MCP tools does platform-mcp-service provide?"
- Any question about how Nimbus services connect to each other

## Key Principle

GitNexus sees **in-process code** within one service. The inventory overlay
sees **cross-service edges** that code parsing cannot detect (gateway routes,
Feign HTTP calls, Kafka topics, MCP tool wiring). **Always check both.**

## Workflow

```
1. Read inventory.yaml for cross-service edges involving the target service
2. Use GitNexus MCP tools for in-process code exploration
3. Combine both to give a complete answer
```

## Inventory quick reference

Location: `~/devops/platform-graph/inventory.yaml`

### Service lookup
```bash
grep -A 20 "^  <service-id>:" inventory.yaml
```

### Cross-service edges
```bash
# All edges involving a service
grep -B 2 -A 5 "to: <service-id>" inventory.yaml
grep -B 2 -A 5 "from: <service-id>" inventory.yaml

# By edge kind
grep -B 2 -A 5 "kind: gateway_route" inventory.yaml
grep -B 2 -A 5 "kind: feign_call" inventory.yaml
grep -B 2 -A 5 "kind: kafka" inventory.yaml
grep -B 2 -A 5 "kind: mcp_tool_use" inventory.yaml
```

### Edge kinds
| Kind | Meaning | GitNexus sees it? |
|------|---------|-------------------|
| `gateway_route` | HTTP path prefix → service | No (YAML config) |
| `feign_call` | Service A calls B via Feign HTTP | No (cross-index) |
| `kafka` | Producer → topic → consumer | Partially |
| `mcp_tool_use` | AI app calls MCP tool | No (runtime) |
| `shared_db` | Two services share a DB | No (config) |

## GitNexus MCP tools

All queries require `repo:` parameter (one of: api-gateway, auth-service,
bio-service, user-platform-service, platform-mcp-service, ai-assistant).

### query — find code by concept
```
@gitnexus query({search_query: "KafkaListener", repo: "bio-service"})
```

### context — callers/callees of a symbol
```
@gitnexus context({name: "AuthenticationClient", repo: "auth-service"})
```

### impact — blast radius
```
@gitnexus impact({target: "AuthenticationClient", direction: "upstream", repo: "auth-service"})
```

### trace — path between two symbols
```
@gitnexus trace({from: "SomeController", to: "SomeRepository", repo: "auth-service"})
```

## Indexed services

| service_id | repo | symbols | role |
|------------|------|---------|------|
| api-gateway | backend-monorepo | 192 | gateway |
| auth-service | backend-monorepo | 681 | backend |
| bio-service | backend-common | 14,492 | backend |
| user-platform-service | backend-common | 11,913 | backend |
| platform-mcp-service | mcp-servers | 317 | mcp-server |
| ai-assistant | ai-assistant-svc | 24,200 | ai-app |

## Example: "Who calls auth-service?"

```
Step 1 — Inventory (cross-service edges):
  grep -B 2 -A 5 "to: auth-service" inventory.yaml
  → bio-service calls auth-service via Feign (AuthenticationClient)
  → api-gateway routes /auth/** to auth-service
  → api-gateway uses auth-service as JWT issuer

Step 2 — GitNexus (in-process callers within auth-service):
  @gitnexus impact({target: "AuthenticationController", direction: "upstream", repo: "auth-service"})
  → Shows internal callers of the controller

Step 3 — Combine:
  "auth-service is called by:
   - bio-service via Feign (AuthenticationClient) — inventory edge
   - api-gateway via /auth/** route — inventory edge
   - [internal callers from GitNexus]"
```

## Expanding the graph

See `gitnexus-runbook.md` §"Indexing checklist" for adding new services.
After indexing, run `scripts/export-results.sh` to update `results/`.
