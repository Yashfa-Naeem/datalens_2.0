---
name: documentation-and-adrs
description: >-
  Captures architecture decisions, metric catalogs, and API documentation
  for analytics products. Use when changing data models, metrics, public
  interfaces, or cross-cutting architecture.
---

# Documentation and ADRs (Data Analytics Web App)

## Overview

Documentation for analytics apps must answer **why** numbers are what they are—not only **how** to run the repo. Architecture Decision Records (ADRs) capture context, decision, and consequences for choices that are hard to reverse (warehouse design, caching strategy, auth model, event taxonomy). User-facing docs and inline comments should stay aligned with **metric definitions** and **data freshness** promises.

## When to Use

- New ADR-worthy decision (storage engine, OLAP vs OLTP split, real-time vs batch).
- New metric, renamed metric, or changed definition affecting reports.
- New or changed REST/GraphQL endpoint consumed by the web app.
- Onboarding gaps discovered during implementation.

## Process

1. **Classify the change** — Operational runbook vs ADR vs inline code comment vs user help article.
2. **Author ADRs for significant forks** — Title, status, context, decision, consequences; one decision per ADR; supersede rather than edit history.
3. **Metric catalog** — For each KPI: definition, grain, filters, data sources, known limitations, owner.
4. **API docs** — Request/response schemas, error semantics, pagination, and **empty result** meaning (no data vs forbidden).
5. **Update the README** — Local dev data setup, env vars, and how to refresh sample datasets.
6. **Link artifacts** — PRs reference ADR IDs; ADRs reference specs or tickets.
7. **Deprecation notes** — If behavior changes, document migration for saved reports and embedded links.

## Rationalizations

| Excuse | Rebuttal |
|--------|----------|
| "The code is self-documenting." | Join logic rarely explains business intent or tradeoffs. |
| "We'll update the wiki later." | "Later" never tracks code; colocate ADRs in the repo. |
| "Only engineers read this." | CS and success teams need metric definitions to answer customers. |
| "One long README is enough." | Long READMEs hide updates; ADRs and catalogs scale better. |

## Red Flags

- Two dashboards show different numbers for the **same named metric** without documented difference.
- Breaking API changes with no changelog or version note.
- ADRs without **consequences** (operational cost, migration path).

## Verification

- ADR merged with the decision (or marked superseded with pointer).
- Metric or API change reflected in the **catalog or OpenAPI** equivalent.
- At least one reviewer confirmed **user-visible** docs if behavior changed.
