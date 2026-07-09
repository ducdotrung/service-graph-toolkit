---
date: YYYY-MM-DD
discovered_in: TASK-XXX                # ticket where this hit
status: active | resolved | obsolete
severity: trap | annoyance             # trap = costs >15 min if unknown; annoyance = mild
related_decisions: []                  # decisions that exist because of this
---

# {short, scannable title — what to expect}

## What happens
The surprising behavior, in concrete terms. Include the failing command, the
misleading output, or the wrong assumption.

## Why
Root cause. If unknown, say so.

## How to detect
The signal that you're hitting it. A specific error, a wrong-looking number,
a directory that doesn't match expectation.

## How to handle
The workaround or correct approach. Be prescriptive.

## Notes
Anything else: scope (does it affect all services or just one?), upstream
issue link, when it might be fixed.
