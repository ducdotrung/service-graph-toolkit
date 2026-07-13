# Workstation Setup

The default mode is local: clone this toolkit, keep source repositories outside
Git, configure `projects/<id>/.local.yaml`, and run `graph.py` commands.

For a future shared workstation, use the same project directories with a
dedicated service account, a protected environment file containing source-root
and MCP credentials, and scheduled **index/generate** jobs. Do not enable
automatic cloning, pulling, arbitrary shell execution, or public HTTP MCP
access by default. Authenticate remote MCP clients, scope them to authorized
projects, audit tool calls, and keep outputs bounded.

Existing `deploy/` templates are legacy reference material and must be
parameterized and reviewed before use. The safe rollout is: local pilot,
read-only shared workstation, then explicitly approved mutation workflows.
The local Graph MCP server requires Node.js 20 or newer.
