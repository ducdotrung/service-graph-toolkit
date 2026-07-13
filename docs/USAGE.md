# Using a Service Graph

Start with project artifacts, then use GitNexus for code-level detail.

```bash
python3 scripts/graph.py validate <project>
python3 scripts/graph.py generate <project>
```

## Questions and evidence

| Question | First evidence | Code follow-up |
|---|---|---|
| Who owns a feature/route? | `inventory.yaml`, service page | `gitnexus query` |
| What changes with a service contract? | incoming/outgoing edges | `gitnexus impact` |
| What needs testing? | service map and dependency edges | symbol context/tests |
| Where should an incident be investigated? | adjacent service edges | `context` / `trace` |

Index names are namespaced. For the Sock Shop demo:

```bash
gitnexus query "payment" -r sock-shop--orders
gitnexus context OrdersController -r sock-shop--orders
gitnexus impact OrdersController --direction upstream -r sock-shop--orders
```

Use the matching `skills/` workflow for feature discovery, impact, test scope,
release readiness, incident triage, implementation planning, or PoC reporting.

Generated views are evidence aids, not source of truth. The authored inventory
is authoritative for declared cross-service relationships; GitNexus is
authoritative only for the indexed code it successfully analyzed.
