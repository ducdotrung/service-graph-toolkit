# Workstation Setup

The default mode is local: clone this toolkit, keep source repositories outside
Git, configure `projects/<id>/.local.yaml`, and run `graph.py` commands.

For a future shared workstation, use the same project directories with a
dedicated service account, a protected environment file containing source-root
and MCP credentials, and scheduled **index/generate** jobs. Do not enable
automatic cloning, pulling, arbitrary shell execution, or public HTTP MCP
access by default. Authenticate remote MCP clients, scope them to authorized
projects, audit tool calls, and keep outputs bounded.

Parameterized, project-instance templates live in `deploy/templates/`.
`deploy/shared-workstation-refresh.sh` runs only `validate`, `index`, and
`generate`; it never clones, pulls, starts containers, exposes HTTP MCP, or
uses credentials. Copy `deploy/project.env.example` to a protected per-project
environment file, render the service placeholders for the dedicated account and
workspace root, then enable `service-graph-refresh@<project>.timer`.
For a remote transport, an authenticated gateway must set
`SERVICE_GRAPH_ALLOWED_PROJECTS`, `SERVICE_GRAPH_CALLER`, and a protected
`SERVICE_GRAPH_AUDIT_LOG` for each session. The toolkit filters project access
The local Graph MCP server requires Node.js 20 or newer.
