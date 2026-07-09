# Developer and QA: Connecting to the GitNexus Host

The GitNexus code graph and web UI run on a central host.

## Available endpoints

| Service | Address | Who uses it |
|---------|---------|-------------|
| Web UI | `http://<graph-host>:4747/?server=http%3A%2F%2F<graph-host>%3A4747` | Anyone browsing the graph |
| MCP server | `http://<graph-host>:4748/mcp` | Developers using AI coding tools |

Replace `<graph-host>` with your actual host.

## Browser access

Open:

`http://<graph-host>:4747/?server=http%3A%2F%2F<graph-host>%3A4747`

## Project MCP config

```json
{
  "mcpServers": {
    "gitnexus": {
      "type": "http",
      "url": "http://<graph-host>:4748/mcp",
      "headers": {
        "Authorization": "Bearer <TOKEN>"
      }
    }
  }
}
```

## Global MCP config

```json
{
  "mcpServers": {
    "gitnexus": {
      "type": "http",
      "url": "http://<graph-host>:4748/mcp",
      "headers": {
        "Authorization": "Bearer <TOKEN>"
      }
    }
  }
}
```

## Verify the connection

```text
@gitnexus list_repos
```

Common issues:

| Error | Fix |
|-------|-----|
| `Connection refused` | Check host and port |
| `401 Unauthorized` | Check token |
| `No repos indexed` | Retry after refresh completes |
| `Index stale` | Trigger or request a refresh |

## Manual refresh pattern

If you need a fresh index before the next scheduled run, the maintainer can run
something like:

```bash
sudo -u gitnexus bash /opt/microservice-call-graph/scripts/refresh.sh
```
