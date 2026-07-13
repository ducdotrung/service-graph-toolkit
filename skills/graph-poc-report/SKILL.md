---
name: graph-poc-report
description: "Use when preparing a leader-facing proof-of-concept report for a GitNexus-backed multi-repository service graph. Produces evidence, limits, cost, and a recommendation rather than a tool transcript."
---

# Graph PoC Report

Use this skill to decide whether a project graph is valuable enough to adopt.
The audience is an engineering leader, platform owner, or hackathon judge. They
need a decision, not an explanation of GitNexus commands.

## Script-first evidence collection

Run deterministic checks before interpreting anything:

```bash
python3 scripts/graph.py validate <project>
python3 scripts/graph.py generate <project>
git status --short
```

Read only the generated files needed for the question:

- `.graph-work/<project>/service-map.md` for architecture coverage
- `.graph-work/<project>/services/<service>.md` for service ownership/dependencies
- `.graph-work/<project>/group.yaml` for indexed-repository coverage
- `projects/<project>/inventory.yaml` for authored edges and evidence pointers

When indexes are available, use GitNexus for one or two concrete questions:

```text
query(<feature or protocol>, repo=<project--service>)
context(<symbol>, repo=<project--service>)
impact(<symbol>, direction=upstream, repo=<project--service>)
```

Do not claim a capability that was not exercised. Do not estimate code facts by
reading generated prose when a graph query or script can establish them.

## Minimum demonstration

Choose one realistic change question that crosses a service boundary, for example:

- Which services are affected if a checkout/payment contract changes?
- Which service owns a public route, and what does it call next?
- Which repositories must be inspected before changing a shared event or API?

Record: question, deterministic evidence used, answer, time/steps avoided, and
what remains uncertain. Label manifest edges as authored evidence and GitNexus
links as code-derived evidence; neither is automatically runtime truth.

## Required report shape

Write a concise report with these sections:

1. **Recommendation** — adopt, extend pilot, or stop; state why in two sentences.
2. **PoC scope** — project, repositories/services indexed, source revision/date, and what was excluded.
3. **What it proved** — up to three concrete questions answered, each with source paths or generated artifact references.
4. **Measured coverage** — indexed services, authored cross-service edges, generated outputs, and any graph-query results actually run.
5. **Limits and risks** — missing source, dynamic/runtime calls, false positives, stale indexes, and security/access constraints.
6. **Operating model** — who owns the inventory, when scripts run, and how local use differs from a future shared workstation.
7. **Next 1–2 actions** — bounded actions with acceptance criteria.

## Decision rules

- Recommend **adopt** only when the demo answered a cross-repository question faster or more reliably than manual search.
- Recommend **extend pilot** when the inventory is useful but indexes, evidence, or a representative workflow are incomplete.
- Recommend **stop** when maintaining the manifest costs more than the decisions it improves.
- Never include secrets, private remotes, unbounded logs, or unsupported ROI claims.

## Handoff

End with the exact commands used, artifact paths, assumptions, and the next
owner. Keep the raw command output out of the report unless it is necessary
evidence for a failure or limitation.
