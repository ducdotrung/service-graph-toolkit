---
date: YYYY-MM-DD
ticket: TASK-XXX                       # primary ticket; omit if exploration
session_type: work | exploration | review
status: in-progress | complete | blocked
related_decisions: []                  # e.g. [001, 003]
related_gotchas: []                    # e.g. [platform-tools-not-a-monorepo]
---

# {short title — what this session was about}

## Goal
One or two sentences. What did I set out to do?

## What I did
Bullet points. Concrete: paths, commands, decisions made on the fly. Not a
narrative — a record.

- Ran `gitnexus analyze backend-core/identity-service --name identity-service`. 4m12s wall-clock. 0 parse-timeout warnings.
- Found that `<svc>-client` modules contain `@FeignClient` interfaces and the convention is consistent across all backend services.

## What surprised me
Anything I didn't expect. This is the most valuable section for future sessions.

## What's blocked / unresolved
What I couldn't finish, and what would unblock it. Link to an issue or sub-task
if one exists.

## What I'd do next
For the next session (which may be me, may be someone else). One step is
enough; don't over-plan.

## Output
- Files changed: `inventory.yaml`, `06-poc-validation-results.md`
- Commits: `TASK-134 …` (link via SHA)
- Tool output worth keeping: pasted below or linked to.
