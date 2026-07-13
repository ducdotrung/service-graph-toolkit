# Service Graph Toolkit Quick Start

## Prerequisites

Install Python 3, Git, and GitNexus:

```bash
npm install -g gitnexus@latest
gitnexus --version
```

## Use the public Sock Shop demo

```bash
scripts/fetch-sock-shop.sh
cp projects/sock-shop/.local.yaml.example projects/sock-shop/.local.yaml
python3 scripts/graph.py validate sock-shop
python3 scripts/graph.py index sock-shop
python3 scripts/graph.py generate sock-shop
```

`index` writes GitNexus indexes next to the ignored local source clones.
`generate` writes reproducible graph artifacts under `.graph-work/sock-shop/`.

## Query code and graph evidence

Use project-namespaced index names, for example:

```bash
gitnexus query "payment" -r sock-shop--orders
gitnexus context OrdersController -r sock-shop--orders
gitnexus impact OrdersController --direction upstream -r sock-shop--orders
```

Read service ownership and authored dependencies in:

```text
.graph-work/sock-shop/services/
.graph-work/sock-shop/service-map.md
projects/sock-shop/inventory.yaml
```

## Configure a local MCP client

```bash
python3 scripts/graph.py mcp-config sock-shop
cat .graph-work/sock-shop/mcp.json
```

Copy the generated stdio server definition into your client’s local MCP
configuration. It contains no endpoint or token.

## Create your own project

```bash
python3 scripts/graph.py init my-platform
cp projects/my-platform/.local.yaml.example projects/my-platform/.local.yaml
python3 scripts/graph.py validate my-platform
```

Edit `inventory.yaml` with service IDs, relative repository paths, cross-service
edges, and evidence pointers. Then index and generate as above.
