---
name: test-driven-development
description: >-
  Applies Red-Green-Refactor and pyramid-shaped testing for analytics apps:
  metric logic, data transforms, API contracts, and critical UI. Use when
  implementing behavior, fixing bugs, or changing queries and definitions.
---

# Test-Driven Development (Data Analytics Web App)

## Overview

Tests are **proof**, not ceremony. For analytics web apps, the highest value tests often guard **metric math**, **timezone and windowing**, **join keys and grain**, and **API contracts** consumed by charts. Follow the test pyramid: many fast unit tests, fewer integration tests, minimal E2E for critical journeys. Prefer **DAMP** (Descriptive And Meaningful Phrases) assertions over clever DRY abstractions that obscure failure reasons.

## When to Use

- New or changed business rules affecting numbers users see.
- Refactors of SQL, dataframe logic, or aggregation pipelines.
- Public HTTP handlers or GraphQL fields that power dashboards.
- Bug fixes where a regression test prevents recurrence.

## Process

1. **Red** — Write a failing test that encodes the spec: inputs → expected aggregates, shapes, or HTTP payloads.
2. **Green** — Implement the minimum to pass; avoid over-building adjacent features.
3. **Refactor** — Clean duplication while keeping tests green; extract pure functions for testability.
4. **Layer appropriately** — Pure functions and SQL builders in unit tests; DB or container-backed tests for real planner behavior when needed.
5. **Beyonce Rule** — If users rely on it, **test it** (export formats, role-based row filters, grand totals).
6. **Name tests for behavior** — `returns_zero_when_no_events_in_window` beats `test_query_1`.
7. **Stop when risk is covered** — Do not chase coverage percentages at the expense of meaningful cases.

## Rationalizations

| Excuse | Rebuttal |
|--------|----------|
| "E2E is enough." | E2E alone misses combinatorics of filters and slow feedback loops. |
| "The chart looks right." | Visual sanity is necessary but not sufficient; encode key cases in tests. |
| "SQL can't be unit tested." | Extract expressions, windows, and filters into testable pieces or use fixtures. |
| "I'll add the test if we have time." | Regressions in metrics are expensive; the test is part of the feature. |

## Red Flags

- Tests depend on **production** data or random ordering without fixtures.
- Assertions only check **200 OK** without payload structure.
- Flaky timing in tests masking **race conditions** in cache invalidation.

## Verification

- Failing test existed before implementation (or clear equivalent for urgent hotfixes documented).
- CI runs the new tests in the **appropriate** job (unit vs integration).
- At least one test ties to a **metric ID** or user story from the spec.
