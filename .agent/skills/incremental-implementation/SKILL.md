---
name: incremental-implementation
description: >-
  Delivers analytics features in thin vertical slices with safe defaults,
  feature flags, and rollback-friendly steps. Use when implementation touches
  multiple layers or production data paths.
---

# Incremental Implementation (Data Analytics Web App)

## Overview

Build **one slice at a time**: land a narrow data path, expose it safely, prove it in tests, then expand UI and filters. Favor **defaults that do not lie** (empty states, explicit "data delayed" banners) over silent partial data. Align with trunk-based habits: integrate frequently behind flags or dark launches when behavior is user-visible.

## When to Use

- More than one file or subsystem changes (SQL, API, React, caching).
- Risk to **production query cost** or **user-visible metrics**.
- Migrations or backfills that could be partially applied.

## Process

1. **Choose the slice** — Smallest user-visible or contract-visible increment (e.g., one KPI on one page with one filter).
2. **Guard the path** — Timeouts, row limits, feature flags, kill switches for expensive queries.
3. **Implement with seams** — Clear module boundaries: data fetchers, mappers, presentation components.
4. **Verify locally** — Representative volume; explain plan for large tables if relevant.
5. **Commit as save points** — Atomic commits with messages that state intent; no "WIP" on shared mainline.
6. **Integrate** — Push through CI before starting the next slice; fix failures before layering new behavior.
7. **Observe** — Add minimal logging or metrics for new code paths (latency, errors, empty results).

## Rationalizations

| Excuse | Rebuttal |
|--------|----------|
| "I'll add the flag after it works." | Flags belong in the same slice as risky behavior to enable safe rollback. |
| "We can ship the UI with mock data." | Mock data is fine only if clearly labeled and not merged as production truth. |
| "One commit at the end keeps history clean." | Small commits are the audit trail for data regressions. |
| "Query optimization can wait." | Guardrails (limits, indexes) are part of the slice if cost is unknown. |

## Red Flags

- Dashboards render **hard-coded** numbers without a tracked path to real data.
- Long-lived branches with divergent schema from `main`.
- Silent retries that **double-count** or duplicate events in metrics.

## Verification

- Slice is **demonstrable** (local URL, API response, or test output).
- Rollback path exists (flag off, revert migration, or cached fallback documented).
- CI green for the integrated commit set before the next slice begins.
