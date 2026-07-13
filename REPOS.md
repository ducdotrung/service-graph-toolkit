# Source Repo Layout Guide

This file describes how the graph workspace expects sibling source repositories
to be organized. It intentionally avoids listing private repo names or remotes.

## Purpose

The graph workspace usually sits next to a separate folder that contains the
actual service repositories. The manifest then points at those sibling repos by
relative path.

A common layout looks like this:

```text
~/workspace/
  service-graph-toolkit/
  platform-source/
    gateway-service/
    identity-service/
    user-service/
    bio-service/
    platform-mcp/
    shared-libs/
```

If your layout differs, set a `PLATFORM_ROOT` environment variable or adjust
your local scripts accordingly.

## Recommended categories

Most platforms end up with some version of these groups:

### Backend monorepos

Use this when one repo contains multiple deployable services or shared modules.

Examples:
- `backend-core/`
- `platform-services/`
- `shared-modules/`

### Standalone services

Use this for repos that map cleanly to one deployable service.

Examples:
- `assistant-service/`
- `platform-mcp/`
- `event-router/`

### Folder of sibling repos

Sometimes a directory groups several repos without being a monorepo itself.

Examples:
- `mcp-servers/`
- `visualization-apps/`
- `frontend-apps/`

In that case, the folder is only an organizer. Each child still has its own
git history.

## Generic bootstrap example

```bash
mkdir -p ~/workspace/platform-source
cd ~/workspace/platform-source

# Clone your service repos here
git clone <backend-core-remote> backend-core
git clone <platform-services-remote> platform-services
git clone <assistant-service-remote> assistant-service

mkdir -p mcp-servers
cd mcp-servers
git clone <platform-mcp-remote> platform-mcp
git clone <asset-mcp-remote> asset-mcp
```

## What the graph repo needs from sibling repos

For each service or repo you want to index, the graph workspace usually needs:

- a stable local path
- a stable service ID
- enough source and config files to derive routes, topics, and ownership

The exact remote URLs are not important to this repo. They should stay in your
private bootstrap docs or internal automation.

## What should not be committed here

Do not commit:

- private git remotes
- internal hostnames
- access tokens
- local absolute paths tied to one machine
- environment-specific clone inventories unless they are fully sanitized

## Recommended next step

Once your sibling repos are cloned locally:

1. define service IDs in `projects/<project-id>/inventory.yaml`
2. index a small pilot set with GitNexus
3. validate route and event edges
4. only then expand the manifest
