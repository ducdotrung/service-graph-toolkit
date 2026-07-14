# Sock Shop Hackathon Demonstration

This guided local-only flow demonstrates a code-backed service graph in one
run. It fetches public Sock Shop source, creates only ignored local config,
indexes code, generates graph artifacts, runs a cross-service impact query,
and writes a short evidence report. It does not start containers or use remote
credentials.

## Prerequisites

- Git
- Python 3
- Node.js 20 or newer
- GitNexus: `npm install -g gitnexus@latest`

Run from the repository root:

```bash
scripts/demo-sock-shop.sh
```

To use another local source directory, pass it as the only argument and update
the ignored `projects/sock-shop/.local.yaml` source root when the script asks.

## What it does

1. Fetches the seven public Sock Shop repositories, without containers.
2. Creates the ignored local source-root configuration if it is missing.
3. Validates the manifest, indexes each service under its namespaced index, and
   generates graph views in `.graph-work/sock-shop/`.
4. Runs `gitnexus impact OrdersController --direction upstream` against the
   `sock-shop--orders` index.
5. Writes `.graph-work/sock-shop/graph-poc-report.md` and preserves raw impact
   evidence alongside it.

## Judge-ready explanation

The report distinguishes two evidence types: authored inventory edges establish
the declared checkout path (`orders` to `payment` and `shipping`), while the
GitNexus query supplies static-code context for `OrdersController`. Neither is
claimed as runtime truth. The report also records source revision, coverage,
limitations, and the two bounded next actions needed to extend the pilot.

## Failure handling

The script stops before cloning or indexing when Git, Python, GitNexus, or Node
