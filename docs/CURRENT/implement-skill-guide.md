# `gitnexus-implement` Skill — Developer Guide

This guide describes a reusable implementation skill that combines code-graph
queries with a structured output format.

## Purpose

The skill should answer:

"Given an existing pattern, what files and symbols should I touch to add a new
variant safely?"

## Good use cases

- adding a new enum value
- adding a new processor that follows an established base class
- extending a feature behind an existing factory or registry
- finding downstream docs or tools that mention a shared contract

## Tool sequence

1. `query` to find the existing pattern
2. `context` to inspect the main symbols
3. `impact` to find the blast radius
4. direct source reads to confirm the edit points

## Expected output shape

The output should group changes by confidence:

- `[must]` files that definitely need edits
- `[likely]` files that usually need edits
- `[verify]` files that should be checked but may not change

## Example result shape

### `[must]` shared-common

| File | Reason |
|------|--------|
| `shared-common/.../PaymentType.java` | add the new enum constant |
| `shared-common/.../PaymentConstants.java` | add the enum-to-resource mapping |

### `[must]` implementation service

| File | Reason |
|------|--------|
| `billing-integration-service/.../PaymentProviderProcessor.java` | add new processor |
| `billing-integration-service/.../ProviderFactory.java` | register the new processor |

### `[verify]` downstream docs or tools

| File | Reason |
|------|--------|
| `tools/platform-mcp/.../PaymentTypeUsageTool.java` | may mention allowed values in docs or tool output |

## Installation

```bash
mkdir -p ~/.claude/skills/gitnexus-implement
cp /path/to/microservice-call-graph/skills/gitnexus-implement/SKILL.md \
  ~/.claude/skills/gitnexus-implement/SKILL.md
```

## Why it is useful

The skill turns "find the pattern and guess the edit list" into a repeatable
workflow. It does not replace code review, but it reduces the first hour of
manual spelunking.
