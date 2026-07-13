# Local Graph MCP Demo

This is a public, local-only demonstration of the Graph MCP server. It uses the
bundled Sock Shop manifest and does not require private source code or a remote
MCP host.

## Setup

Node.js 20+ is required by the official MCP SDK.

```bash
npm install --prefix mcp-server
python3 scripts/graph.py mcp-config sock-shop
npm run --prefix mcp-server smoke
```

The smoke test starts the stdio server, confirms its read-only tool catalog,
lists bundled projects, and asks for the declared `sock-shop/orders` service
dependencies. It exercises MCP transport and project-manifest evidence without
requiring GitNexus indexes.

## Expected evidence

`get_service_details(project="sock-shop", service="orders")` returns the
orders service definition plus its declared outgoing edges to `payment` and
`shipping`. Each result identifies `projects/sock-shop/inventory.yaml` as its
source. `list_projects` includes `example-platform` and `sock-shop`.

## Indexed-code demonstration

After running `python3 scripts/graph.py index sock-shop`, a client can call:

```text
search_code(project="sock-shop", service="orders", query="payment")
get_change_impact(project="sock-shop", service="orders", symbol="OrdersController")
```

Those tools return GitNexus output together with the manifest's adjacent
cross-service edges. They do not claim runtime behavior beyond the indexed code
and authored evidence.
