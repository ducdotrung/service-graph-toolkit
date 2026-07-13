---
name: graph-feature-discovery
description: "Use to discover where a requested feature belongs across a multi-repository service system before writing a ticket, design, or implementation plan."
---

# Graph Feature Discovery

Start with deterministic evidence:

```bash
python3 scripts/graph.py validate <project>
python3 scripts/graph.py generate <project>
```

Search `projects/<project>/inventory.yaml`, generated service pages, and then
GitNexus for feature terms, routes, events, and likely symbols. Do not infer
ownership from a service name alone.

Return: feature restatement; owning service(s); entry route/tool/event; direct
dependencies; relevant source/evidence paths; assumptions; questions that must
be answered by product or a service owner. Mark each conclusion as manifest,
code, or unverified runtime evidence. Keep it short enough to become a ticket.
