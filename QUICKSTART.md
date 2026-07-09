# Quickstart

This guide gets you from a blank machine to a usable microservice code-graph
workspace.

## Prerequisites

Install GitNexus:

```bash
npm install -g gitnexus@latest
gitnexus --version
```

Set up a local workspace with your service repos beside this graph repo:

```text
~/workspace/
  microservice-call-graph/
  platform-source/
    gateway-service/
    identity-service/
    bio-service/
    user-service/
    platform-mcp/
```

## Index a small pilot

Start with a few representative services:

```bash
gitnexus analyze --skip-git --name gateway-service   ../platform-source/gateway-service
gitnexus analyze --skip-git --name identity-service  ../platform-source/identity-service
gitnexus analyze --skip-git --name bio-service           ../platform-source/bio-service
gitnexus analyze --skip-git --name user-service      ../platform-source/user-service
gitnexus analyze --name platform-mcp                 ../platform-source/platform-mcp
```

Then verify:

```bash
gitnexus list
```

## Option A: Web UI

For demos or visual browsing:

```bash
gitnexus serve --host 0.0.0.0 --port 4747
```

Open:

`http://localhost:4747`

The UI is useful for:
- symbol search
- execution flows
- cluster exploration
- service-level browsing

## Option B: MCP for AI tools

Point your tool at a local or remote MCP endpoint.

Local example:

```json
{
  "mcpServers": {
    "gitnexus": {
      "command": "gitnexus",
      "args": ["mcp"]
    }
  }
}
```

Verify it works:

```text
@gitnexus list_repos
```

## Common workflows

### What breaks if I change this?

```text
@gitnexus impact({target: "IdentityDTO", direction: "upstream", repo: "identity-service"})
```

If the change crosses service boundaries, also check `inventory.yaml`.

### How does this feature work?

```text
@gitnexus query({search_query: "login authenticate", repo: "identity-service"})
@gitnexus context({name: "AuthenticationController", repo: "identity-service"})
```

Then inspect cross-service edges in the manifest.

### What does this service expose?

```text
@gitnexus query({search_query: "Controller", repo: "bio-service", limit: 10})
@gitnexus query({search_query: "KafkaListener", repo: "bio-service"})
```

### Is there a circular dependency?

```bash
gitnexus check --cycles -r identity-service
```

## CLI reference

```bash
gitnexus list
gitnexus query "KafkaListener" -r bio-service
gitnexus context IdentityClient -r identity-service
gitnexus impact IdentityClient --direction upstream -r identity-service
gitnexus trace LoginController UserRepository -r identity-service
gitnexus check --cycles -r bio-service
gitnexus serve --port 4747
```

## Cross-service questions

Use both the manifest and the code graph:

| Question | Best approach |
|----------|---------------|
| Who calls a service? | manifest first, then GitNexus inside each caller |
| What route reaches a service? | manifest or gateway config |
| What Kafka topics does a service consume? | GitNexus query plus manifest |
| What tools does an MCP service expose? | manifest plus code search |
| What breaks if a service is down? | manifest edges plus selective impact checks |

## Next steps

1. Sanitize `inventory.yaml`.
2. Regenerate `group.yaml` and generated `views/` locally when needed.
3. Remove any private `results/` artifacts before pushing.
4. Keep the repo at a single clean initial commit before pushing.
