---
name: graph-release-readiness
description: "Use before releasing a cross-service change to assess graph-backed dependency, validation, and rollback readiness."
---

# Graph Release Readiness

Collect facts with `graph-change-impact`, `graph-test-scope`, project validation,
and the current generated map. Inspect only declared deploy/config evidence;
never claim production status without an authorized operational source.

Return **ready**, **ready with conditions**, or **not ready**. Include affected
services, contract/config/database compatibility checks, completed and missing
tests, rollout order, rollback trigger/action, and unresolved owners. A missing
index or dynamic edge is a condition, not proof that it is safe.
