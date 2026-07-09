---
id: NNN                                # zero-padded, sequential
date: YYYY-MM-DD
status: active | superseded-by-NNN | reversed
deciders: [person, person]             # who agreed; "session" if AI/owner alone
related_tickets: [TASK-XXX]
supersedes: NNN                        # optional, if this replaces an older decision
---

# {short title — the choice itself, e.g. "Per-service indexing for Java monorepos"}

## Context
What was the situation that forced a decision? Two or three sentences.
What were the constraints?

## Options considered
- **Option A** — short description. Pro / con.
- **Option B** — short description. Pro / con.
- **Option C** — (only if real) short description. Pro / con.

## Decision
The chosen option, in one paragraph. Imperative, not optional.

## Rationale
Why this option beat the others. Specifically what made the trade-off
acceptable.

## Consequences
- What this enables (intended).
- What this constrains or makes harder (the cost).
- What we'll have to revisit if this turns out wrong.

## Revisit when
Concrete trigger. "When indexing time exceeds 10 min/service." "When
group-sync starts auto-bridging Feign contracts."
