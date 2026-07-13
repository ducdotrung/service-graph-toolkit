---
name: engineering-workflow
description: "Use for non-trivial repository, graph, or web-evidence work that benefits from deterministic context before model reasoning."
---

# Engineering Workflow

1. Run `scripts/context-pack.sh` before broad repository exploration.
2. Use narrow scripts, tests, graph artifacts, and cited web fetches to gather facts.
3. State goal, evidence, constraints, and acceptance checks before a cross-cutting change.
4. Run deterministic validation before judging success with a model.
5. Report changed files, commands, evidence, and unresolved risks.

Use `scripts/fetch-web.mjs` for a known public URL; do not manually copy web
pages into a prompt when a Markdown artifact with source metadata can be made.
