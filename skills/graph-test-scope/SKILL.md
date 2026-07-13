---
name: graph-test-scope
description: "Use to derive a risk-based QA and developer test scope from a multi-repository feature or change."
---

# Graph Test Scope

Run `graph-change-impact` evidence collection first: validate/generate the
project, inspect service pages and edges, and query indexed symbols only when
needed. Do not substitute a generic testing checklist for actual dependencies.

Return test scope grouped by: local unit tests, provider/consumer contract
tests, service integration tests, end-to-end route or workflow tests, and
regression/observability checks. For every test target state the triggering
edge, expected behaviour, failure signal, owner, and priority. Explicitly list
out-of-scope dependencies and unknown runtime paths.
