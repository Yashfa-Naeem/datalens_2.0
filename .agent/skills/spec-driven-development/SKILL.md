---
name: spec-driven-development
description: >-
  Guides specification-first delivery for data analytics web apps: PRDs,
  data contracts, UX for dashboards, and non-goals before implementation.
  Use when starting features, new datasets, metrics definitions, or
  significant changes to queries, APIs, or visualization behavior.
---

# Spec-Driven Development (Data Analytics Web App)

## Overview

This skill enforces **spec before code** for DatatLens-style products: interactive dashboards, dataset ingestion, metric definitions, filters, exports, and role-aware data access. A specification is not a wish list; it is an agreement on objectives, boundaries, and verifiable outcomes that downstream planning and tests can trace to.

## When to Use

- New feature or user journey (e.g., cohort analysis, drill-down, scheduled report).
- New or changed **data source**, schema, grain, or refresh semantics.
- Changes affecting **correctness** (definitions of KPIs, attribution rules, time zones).
- Any work that could silently mislead users if semantics drift.

## Process

1. **Problem and users** — Who acts on this? What decision does the insight support?
2. **Objectives and success metrics** — Product KPIs and data-quality signals (e.g., freshness SLAs, max acceptable null rate).
3. **Functional scope** — Inputs, transformations, outputs (tables, charts, exports). Explicit **out of scope**.
4. **Data contract** — Entities, grain, keys, time dimensions, filters, and **definition of each metric** (formula, filters, edge cases).
5. **Commands and UX** — Primary flows, empty states, loading/error behavior, accessibility expectations for charts and tables.
6. **APIs and boundaries** — Server endpoints or jobs: request/response shapes, pagination, authz rules, rate limits.
7. **Testing and observability** — What must be provable (unit, contract, E2E), logging, and alerts for pipeline or query failures.
8. **Review gate** — Spec is complete when another engineer could implement without guessing semantics.

## Rationalizations

| Excuse | Rebuttal |
|--------|----------|
| "We can lock semantics in the code." | Misaligned metrics ship silently; specs anchor tests and docs. |
| "The dashboard is self-explanatory." | Labels and filters still need defined meaning and edge-case behavior. |
| "We'll add the SLA later." | Freshness and failure modes affect UX and trust; decide up front. |
| "It's just a small query change." | Small query changes are the highest-risk place for metric drift. |

## Red Flags

- Metric definitions live only in a ticket comment or Slack thread.
- No stated grain (per user, per day, per session) for aggregated views.
- "Match the spreadsheet" without a named reference artifact.

## Verification

- Spec artifact exists (PRD or equivalent) with **traceable IDs** for metrics and datasets.
- Acceptance criteria are **testable** (given input data, expected numbers or shapes).
- Stakeholders acknowledge **non-goals** and **out of scope** in writing or in the doc itself.
