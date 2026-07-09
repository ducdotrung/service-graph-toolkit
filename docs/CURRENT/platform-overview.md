# Platform Overview

Last updated: 2026-07-08

This project assumes a typical microservice platform with three important
surfaces:

1. service source repositories
2. deployment templates and overlays
3. CI/CD automation that connects the two

## Short answer

In many real platforms, both of these are true:

1. there is a shared chart repository with reusable deploy templates
2. some service repos still carry a local `chart/` directory that CI deploys directly

That split matters because the code graph is not enough to explain runtime
topology. Route ownership, environment wiring, and actual deploy inputs often
live outside application code.

## Typical deployment pattern

### Shared chart packaging

A chart pipeline usually:

- checks out a shared chart repo
- packages charts
- publishes them to a registry or artifact store
- versions them per build or release

### Service deployment

A service deployment job often:

1. checks out the application repo
2. reads service config from the source tree
3. copies or mounts that config into a repo-local chart
4. applies environment-specific overrides
5. runs `helm upgrade --install`

The important consequence is that the effective runtime config is spread across:

- chart defaults
- environment overlays
- copied application config
- CI `--set` overrides

### Mixed deployment models

Some teams deploy:

- packaged charts for mature services
- local charts for services still evolving
- a different flow for tools, background jobs, or AI services

That mixed model is normal and worth documenting explicitly.

## Why this matters for a service graph

To answer "what talks to what" reliably, you usually need evidence from:

- source code
- gateway config
- Helm or Kubernetes templates
- CI job parameters
- environment-specific config

If you only index source code, route and deployment questions stay unresolved.

## Common chart shapes

### Backend service chart

Typical rendered objects:

- `ServiceAccount`
- `ConfigMap`
- `Service`
- `Deployment`
- `VirtualService`

### Shared service chart

Typical rendered objects:

- `ServiceAccount`
- `Service`
- `Deployment`
- optional scaling and persistence resources

### Tool or AI service chart

Typical rendered objects:

- `ServiceAccount`
- `Service`
- `Deployment`
- optional `Job`, `PVC`, `Role`, `RoleBinding`, or monitoring resources

## Repo-local chart differences

Repo-local charts often differ from shared charts in small but important ways:

- they read application files from the checked-out repo
- they assume CI has already copied config into place
- they carry service-specific mounts or secrets
- they drift from the shared chart over time

That is why platform mapping should capture both the generic chart pattern and
the actual deployed chart path.

## What to document in the manifest

For each service, keep at least:

- service ID
- source path
- deploy path or chart path
- route ownership
- config location
- key runtime dependencies

## Practical conclusion

If you want an accurate microservice map, inspect the platform as a system, not
just as code. CI rules and deployment templates are part of the architecture.
