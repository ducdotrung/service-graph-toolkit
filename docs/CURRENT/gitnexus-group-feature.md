# GitNexus `group` Feature — How It Fits a Multi-Repo Graph

Status: research notes plus experiment results  
Date: 2026-07-08

## TL;DR

`gitnexus group` can reduce a lot of manual cross-repo glue work, but it should
not replace a richer manifest without a pilot. The best model is usually:

1. keep `inventory.yaml` or similar as the source of truth
2. derive or maintain `group.yaml`
3. run `gitnexus group sync`
4. post-filter obvious false positives

## What the feature does

A group is a set of indexed repos plus a `group.yaml` file that:

- lists member repos
- enables protocol extractors
- accepts manual links
- produces a shared bridge database

After sync, group-aware tools can answer cross-repo search and impact questions.

## Where it helps

It is most useful for:
- cross-repo semantic search
- cross-repo impact analysis
- partial auto-extraction of HTTP and topic contracts

## Where it still needs help

It often still needs manual support for:
- gateway routes defined only in YAML
- runtime tool wiring
- shared database dependencies
- edge cases that collide on common paths such as `/health`

## Suggested coexistence model

Use the manifest for:
- evidence
- deploy metadata
- environment-specific facts
- route ownership
- non-code dependencies

Use `group.yaml` for:
- repo membership
- bridge configuration
- extractors and matching thresholds

## Pilot advice

Run a small pilot before depending on it:

1. one gateway
2. one caller service
3. one callee service
4. one async service

Check:
- how many useful links are created automatically
- how many false positives need filtering
- whether cross-repo impact is meaningfully better than the manifest alone

## Practical rule

If `group sync` removes large amounts of manual work without hiding important
uncertainty, keep it. If it adds opaque noise, keep the manifest primary and use
group support sparingly.
