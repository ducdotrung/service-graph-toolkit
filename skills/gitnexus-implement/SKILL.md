---
name: gitnexus-implement
description: "Use when adding a new value, partner integration, config entry, enum case, scheduled job, service adapter, or feature that must follow existing team patterns across repos. Examples: add a new external data provider, add a new energy source type, add a new role, add a new scheduled processor, or add a source-specific config block."
---

# Feature Implementation Guide with GitNexus + Team Rules

## Purpose

This skill turns a feature request into a concrete implementation guide. It must not only find code symbols. It must also discover how the team actually ships similar work: branches, release fixes, config conventions, i18n, DB migrations, scheduler/job wiring, tests, and cross-service side effects.

Use this skill when the user asks:

- "Implement a new X following existing pattern Y"
- "Add a new enum/value/vendor/type/config entry"
- "What files need to change for feature X?"
- "Generate an implementation guide for ticket X"
- "Compare a planned implementation with real team code"

## Non-Negotiable Rule

Do not produce a final checklist until both layers are complete:

1. **Code graph discovery**: use GitNexus group and repo tools to find definitions, references, flows, and cross-repo edges.
2. **Team rule discovery**: inspect recent real branches/PRs/commits and nearby implementations to learn the team's non-obvious delivery rules.

If these two disagree, report both and mark the conflict. Do not silently choose the cleaner architecture.

## Required Output Shape

Every implementation guide must include these sections:

1. Executive summary
2. Evidence used
3. Team rules discovered
4. Real target architecture
5. File-by-file change plan
6. Cross-repo impact and verification
7. Configuration and secret plan
8. Database/migration plan
9. i18n/UI/API visibility plan
10. Tests and quality gates
11. Deployment and rollback
12. Open questions
13. Coverage/risk notes

## Workflow

### Phase 0: Normalize the request

Extract:

- Ticket id, feature name, vendor/type/value names, service names, and likely repositories.
- Existing reference implementation named by the user.
- Runtime category: enum-only, REST vendor, Kafka producer/consumer, scheduled job, API surface, DB-backed config, UI-visible value, or mixed.

If the user gives a typo or alias, search for likely variants before deciding there is no match.

### Phase 1: Cross-repo graph discovery

Use group tools first, then per-repo tools:

```text
group_query({name: "example-platform", search_query: "<feature/value/reference>"})
group_query({name: "example-platform", search_query: "<ticket id>"})
group_impact({name: "example-platform", target: "<reference symbol>", repo: "<repo>", direction: "upstream", maxDepth: 3})
context({name: "<reference symbol>", repo: "<repo>"})
impact({target: "<reference symbol>", repo: "<repo>", direction: "upstream", maxDepth: 3})
```

Use `inventory.yaml` or derived views to validate cross-repo edges. The group bridge can produce false positives, especially path-only HTTP matches and edge re-exposure through shared clients. Inventory-confirmed edges become `[cross-repo must]`; unconfirmed edges become `[cross-repo check]`.

### Phase 2: Team rule discovery

Before writing a guide, inspect how the team actually delivered similar changes.

Mandatory checks:

```bash
# 1. Fetch or inspect branch metadata if allowed.
git fetch --all --prune --tags

# 2. Search branches/commits by ticket and feature name.
git branch --all --no-color | rg -i "<ticket>|<feature>|<value>"
git log --all --oneline --decorate --grep="<ticket>|<feature>|<value>"
git log --all --oneline -S "<feature/value>"

# 3. Search release/main refs, not only current checkout.
git grep -n -i "<feature/value>" origin/main origin/release/* origin/feature/* -- <likely paths>

# 4. Diff the feature branch against its merge base if a branch exists.
git diff --name-status <merge-base>..<feature-or-main-ref> -- <likely service paths>
git diff --numstat <merge-base>..<feature-or-main-ref> -- <likely service paths>
```

If remote fetch is not available, state that branch/release evidence is missing and lower confidence.

Look specifically for these team-rule side effects:

- Release branch or hotfix follow-up commits.
- Environment config in every `application-*.yml` file.
- Secrets represented as env placeholders, not literal values.
- Scheduler or job processor classes and job parameter DTOs.
- YAML config model classes needed for new config blocks.
- Admin or control-plane enum additions.
- DB migrations for both data model and UI/admin visibility.
- i18n message files for any UI/API-visible enum or manufacturer.
- Downstream converter/parser repo if raw Kafka payload is forwarded.
- Tests that were added or missing in real team work.
- POM/version changes that are release noise and should not be counted as feature requirements.

### Phase 3: Pattern extraction

For each target repo, read at least two nearby implementations, not just one. Extract:

- Naming convention
- Package/location convention
- Annotation and dependency injection style
- Error handling and retry style
- Config source and secret style
- Kafka topic or HTTP client utilities
- Test naming and test fixture style
- DB migration numbering and table convention
- i18n key naming convention

Prefer the team's real pattern over a generic framework pattern. For example, if the repo uses a shared HTTP client utility and YAML provider domains, do not recommend Feign just because it is cleaner.

### Phase 4: Build a traceable checklist

Classify every item:

- `[must]` required for the feature to run
- `[team-rule must]` required by team conventions, release process, admin visibility, or operations
- `[cross-repo must]` inventory-confirmed downstream update
- `[cross-repo check]` graph-suggested but not confirmed
- `[quality gate]` test, logging, metric, manual verification
- `[open question]` requires human/product confirmation

Each row must include:

- File path
- Symbol/config/table/key
- Reason
- Evidence source
- Risk if missing

### Phase 5: Validate against real branches when available

If a real branch or merged implementation exists, produce a replay score:

- Intent coverage: did the guide find the right architecture and services?
- Strict change-group coverage: exact change groups predicted.
- Weighted task coverage: runtime-critical tasks weighted higher than small i18n/config edits.
- Missed items and false positives.

Do not call replay scoring a pre-implementation prediction. Label it as `post-merge replay` when real code was used as evidence.

## External Integration Specific Rules

For external adapter or telemetry-provider work, always check these before writing the guide:

1. `external-ingestion-service/src/main/java/com/example/integration/SourceRegistry.java`
2. Existing provider processor and client classes.
3. Whether the team parses into internal DTOs or forwards raw data to a downstream topic.
4. Scheduler or job-processor conventions under `src/main/java/com/example/integration/processors/`.
5. Job parameter DTOs and site-mapping models.
6. `model/yaml/YamlConfig.java` plus provider-specific YAML model classes.
7. All `application-*.yml` files for domain and per-client API-key placeholders.
8. `admin-service` DB migrations for provider/type visibility.
9. `admin-service-client` enums such as `DataSourceType`.
10. `admin-web-app/src/main/resources/messages*.properties` for i18n keys.
11. `data-transform-service` or downstream parser repo if raw payload is sent.
12. Unit/integration tests. If the real branch has no tests, report it as a quality gap rather than following the omission.

## Quality Rules

- Do not invent code that conflicts with observed team utilities.
- Do not mark downstream services as "no change" unless the payload contract is proven unchanged or a converter/parser exists.
- Do not hide missing tests. The guide should improve team quality, not simply mirror poor practice.
- Do not include secrets. Use env placeholders.
- Separate release/version noise from feature requirements.
- Always list confidence and evidence gaps.

## Example Output Tags

```text
[must] external-ingestion-service/.../SourceRegistry.java
  Add ACME_SOLAR enum value.
  Evidence: existing provider enum pattern; real branch if available.
  Risk if missing: processor cannot resolve provider/data-source key.

[team-rule must] admin-service/.../messages_en_US.properties
  Add DATA_PROVIDER_ACME_SOLAR=Acme Solar.
  Evidence: existing provider i18n pattern and similar provider commit.
  Risk if missing: admin/API display falls back to missing key.

[cross-repo check] data-transform-service
  Verify converter/parser exists for raw upstream payload.
  Evidence: processor comment says downstream conversion handles field mapping.
  Risk if missing: raw payload reaches Kafka but cannot be transformed into internal data points.
```
