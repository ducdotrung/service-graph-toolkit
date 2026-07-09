# GitNexus Runbook

Last updated: 2026-07-08

This is the operational guide for maintaining a GitNexus-backed microservice
call graph. It focuses on repeatable commands, validation, and troubleshooting.

## Quick start

```bash
npm install -g gitnexus@latest
gitnexus --version

# Monorepo-style services
gitnexus analyze --skip-git --name gateway-service   services/gateway-service
gitnexus analyze --skip-git --name identity-service  services/identity-service
gitnexus analyze --skip-git --name bio-service           services/bio-service
gitnexus analyze --skip-git --name user-service      services/user-service

# Standalone repos
gitnexus analyze --name platform-mcp      tools/platform-mcp
gitnexus analyze --name assistant-service apps/assistant-service

gitnexus list
```

If any step fails, stop and fix that failure before expanding scope.

## Why per-service indexes

Indexing an entire monorepo as one graph is usually too noisy:
- semantic search returns unrelated services
- impact results cross service boundaries that are only path-based
- freshness checks become less meaningful

Indexing one service directory at a time keeps the graph usable. If shared
libraries matter, index them separately or use `gitnexus group` plus a manifest.

## Optional local index shortcuts

GitNexus stores indexes inside each analyzed path as `.gitnexus/`. If you want
a single directory of shortcuts, create local symlinks:

```bash
mkdir -p indexes
ln -sf /path/to/services/gateway-service/.gitnexus   indexes/gateway-service
ln -sf /path/to/services/identity-service/.gitnexus  indexes/identity-service
ln -sf /path/to/services/bio-service/.gitnexus           indexes/bio-service
ln -sf /path/to/services/user-service/.gitnexus      indexes/user-service
ln -sf /path/to/tools/platform-mcp/.gitnexus         indexes/platform-mcp
```

Keep this local-only. Absolute paths do not belong in the committed repo.

## Validation checklist

Run these after a fresh pilot index.

### 1. Index visibility

```bash
gitnexus list
```

Expected result:
- every intended service appears
- symbol counts are non-zero
- services that should include both app and client modules are indexed from the parent service directory

### 2. In-service impact

```text
@gitnexus impact({target: "IdentityClient", direction: "downstream", repo: "identity-service"})
```

Expected result:
- useful callers and callees inside the service
- enough signal to support refactoring decisions

### 3. Cross-index boundary check

```text
@gitnexus context({name: "IdentityClient", repo: "bio-service"})
```

Interpretation:
- if cross-service links are missing, that is normal without a bridge layer
- record those edges in `inventory.yaml` or a similar manifest
- if `gitnexus group` is enabled, repeat after `group sync`

### 4. Gateway route lookup

```bash
grep -A 3 "path_prefix: /users/" inventory.yaml
```

This is usually a manifest question, not a pure code graph question.

### 5. Event flow lookup

```text
@gitnexus query({search_query: "USER_CREATED_EVENT", repo: "bio-service"})
@gitnexus query({search_query: "USER_CREATED_EVENT", repo: "user-service"})
```

Expected result:
- the consumer is often easy to find
- the producer may require a shared-lib index or an explicit manifest edge

## Re-indexing rules

### Standalone repo

If the service itself is a git repo, GitNexus can track history directly:

```bash
gitnexus analyze --name assistant-service apps/assistant-service
```

### Monorepo service

If the service lives inside a parent repo and has no `.git` of its own, use
`--skip-git`:

```bash
gitnexus analyze --skip-git --force --name gateway-service services/gateway-service
```

Use `--force` when source changed and you need a clean rebuild.

## Troubleshooting

### `gitnexus list` shows zero symbols

Likely causes:
- wrong analyze path
- indexed only the `-app` module instead of the parent service directory
- parse failure during analyze

### `context` or `impact` misses cross-service HTTP links

That is expected in many setups. Use one of these:
- a manifest such as `inventory.yaml`
- `gitnexus group sync`
- a custom bridge script for known contracts

### Route questions are unanswered

The route definition probably lives in:
- gateway YAML
- Helm values
- service config
- deployment overlay

Do not expect the code graph alone to answer that.

### Stale or corrupt index

Rebuild it:

```bash
gitnexus analyze --skip-git --force --index-only --name identity-service services/identity-service
```

### Too many false-positive cross-links after `group sync`

Reduce noise by:
- excluding health-check routes
- keeping manual route edges in a manifest
- post-filtering `group sync` output with known service mappings

## When to modify GitNexus itself

Default answer: avoid it.

Try these before forking:
1. `.gitnexusrc`
2. `.gitnexusignore`
3. environment flags
4. a manifest-driven overlay
5. `gitnexus group`

Fork only when a missing capability is central to the project and repeated
workarounds are more expensive than maintaining a patch.
