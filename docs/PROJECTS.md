# Project Model

Each directory under `projects/` is an independent service-graph workspace.
The repository shares scripts and skills; projects never share private sources.

## Tracked files

- `project.yaml`: stable project ID and display metadata.
- `inventory.yaml`: services, repositories, cross-service edges, and evidence.
- `.local.yaml.example`: safe template for a local source root.
- `README.md`: public bootstrap instructions and known limits.

## Local-only files

`.local.yaml` supplies `source_root`; source clones and `.graph-work/` output
are ignored. `source_root` may be absolute or project-relative in local config,
but all inventory paths must be safe relative paths beneath it.

## Deterministic workflow

1. `validate` checks project identity, repository/service references, and edge references.
2. `index` creates namespaced GitNexus indexes: `<project>--<service>`.
3. `generate` derives group YAML, JSON, Mermaid, and service pages.
4. Skills consume these artifacts before using model reasoning.

Do not commit generated output, tokens, remotes, internal endpoints, or source
repositories. A future shared workstation may run the same commands with an
environment-managed source root and credentials.
