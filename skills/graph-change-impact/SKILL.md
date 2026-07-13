---
name: graph-change-impact
description: "Use before changing a service API, route, event, schema, configuration, or symbol that may affect other repositories."
---

# Graph Change Impact

Validate and generate the selected project first. Locate the service and all
incoming/outgoing manifest edges, then run GitNexus `impact` or `context` for
the exact changed symbol when indexed. Use scripts and graph outputs for facts;
use reasoning only to classify risk.

Return a table: affected service/repository, dependency direction, contract or
symbol, evidence path, required action, and confidence. Separate confirmed
impact from checks caused by dynamic configuration or missing indexes. End with
the smallest safe validation plan and an explicit no-impact statement only when
evidence supports it.
