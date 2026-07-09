# Prompt: Add a New Service to inventory.yaml

Hand this file to Claude when you want to add or update a service entry in `inventory.yaml`.

**Usage:** "Read `prompts/add-service-to-inventory.md` and add `<service-name>` to the inventory."

---

## What you need to provide

- The service name
- The repo slug on github if known

---

## Research steps (do all of these before writing anything)

### 1. Gateway routes
Check if the service has an HTTP route through the gateway:
```bash
grep -A 5 "<service-name>" gateway-service/src/main/resources/application-k8s.yml
```
Or run `scripts/extract-gateway-routes.sh` for a full dump.

### 2. Service config
Read the Spring k8s config to find port, DB, Redis, Kafka, Feign URLs:
```
<repo>/<svc>-app/src/main/resources/application-k8s.yml
```
Merge `application.yml` + `application-k8s.yml` + `application-prod.yml` for full prod picture.

### 3. Helm chart
Check in this order — stop at the first match:
1. `<repo>/chart/Chart.yaml` — in-repo chart (most backend/common services use this)
2. `<repo>/chart-manifest/` — secondary manifest chart (some example services have both)
3. `platform-charts/README.md` — published platform chart (AI services, some infra)

Note chart name, version, namespace, and any special values (GPU affinity, ports, etc.).

### 4. CI/CD pipeline
```bash
find ci_jobs/ -name "*<service>*" -o -name "*<service>*" | grep -v ".git"
```
Look for: `DEPLOY_SERVICE`, k8s namespace, deploy module, downstream jobs triggered.

### 5. Feign clients
If it's a Java service, check if it exposes a `-client` module:
```bash
ls <repo>/<svc>-client/src/main/java/ 2>/dev/null
```
Then find who consumes it:
```bash
grep -rl "com.example.<svc>.client" backend-core/ platform-tools/ assistant-service/
```

### 6. GitNexus (check if already indexed)
Check `mcp__gitnexus__list_repos` — if the service is already indexed, read its context for additional facts.

### 7. Platform charts cross-check
```bash
grep -r "<service-name>" platform-charts/ --include="*.yaml" --include="*.md" -l
```

---

## Writing the inventory entry

### In `repos:` section (if the repo isn't already there)
```yaml
  <repo-id>:
    path: <folder>/<repo-name>          # relative to PLATFORM_ROOT
    type: single-service                # or monorepo, shared-lib
    remote: git@**.git
    notes: <one line description>
```

### In `services:` section
```yaml
  <service-id>:
    repo: <repo-id>
    paths:
      app_module: <path to app dir>
    role: backend                       # backend | ai-service | app | frontend | infra
    framework: spring-boot              # if applicable
    port: 8080
    chart:
      kind: in-repo                     # in-repo | published | unknown
      chart_path: <path>                # for in-repo
      chart_name: <name>                # for published
      namespace: <k8s-namespace>
    notes: |
      <multi-line if needed>
    evidence: <file-path>#<key>         # always cite evidence
    gitnexus_index:
      name: <index-name>                # must match gitnexus list_repos name
      analyze_path: <path>
      strategy: per-service
      skip_git: false                   # true only for monorepo sub-paths without own .git
```

---

## Rules

- **Every field needs evidence.** If you can't find it, use `kind: unknown` or omit the field — don't guess.
- **`evidence:` always points to a real file path** in one of the cloned repos.
- If the service has no gateway route, say so explicitly in `notes:` rather than leaving `chart.vs_path_prefix` blank.
- If the service is not yet cloned/indexed, add it to `REPOS.md` quick-clone section too.
- After writing the entry, check `REPOS.md` — if the repo isn't listed there, add a table row.

---

## Checklist before committing

- [ ] `repos:` entry present (with `remote:` if it needs cloning)
- [ ] `services:` entry present with all known fields
- [ ] `evidence:` cited for every non-obvious field
- [ ] REPOS.md table updated if repo is new
- [ ] If repo needs cloning on workstation: `remote:` field is set in `repos:` (Step 0 of refresh script will pick it up)
- [ ] `gitnexus_index:` block added so nightly cron will index it after clone
