---
name: planning-and-task-breakdown
description: >-
  Decomposes analytics product specs into small, ordered tasks with acceptance
  criteria and data dependencies. Use after a spec exists and before building
  pipelines, APIs, or UI slices.
---

# Planning and Task Breakdown (Data Analytics Web App)

## Overview

Turn an approved spec into **implementable units** that respect dependencies typical of analytics apps: raw data → modeled layers → APIs → UI → authz → observability. Tasks should be small enough to review quickly (~100 logical lines where practical), each with a clear **done** definition that often includes a query result, schema snapshot, or UI state.

## When to Use

- Spec (or PRD) is approved or stable enough to implement.
- The change spans storage, compute, API, and/or frontend.
- Parallel work is possible and must avoid blocking on undefined contracts.

## Process

1. **Inventory dependencies** — Upstream tables, feature flags, migrations, secrets, third-party quotas.
2. **Order by data flow** — Land schema or contract tests before heavy UI; stub APIs before binding charts if it de-risks parallel work.
3. **Slice vertically when valuable** — Prefer thin end-to-end slices (e.g., one metric end-to-end) over long horizontal layers that delay integration feedback.
4. **Write tasks as outcomes** — Imperative titles with acceptance criteria: data shape, performance budget, error codes.
5. **Tag risk** — Tasks touching **metric definitions**, PII, or authz get explicit review and test tasks paired with them.
6. **Estimate review and test cost** — Data-heavy PRs need time for query plans, sample data, and screenshot or Playwright evidence.
7. **Exit checklist** — Every metric ID in the spec maps to at least one task that proves correctness; no orphan UI tasks without API contract tasks.

## Rationalizations

| Excuse | Rebuttal |
|--------|----------|
| "One big PR is faster." | Large analytics diffs hide wrong joins and wrong filters until late. |
| "We'll wire the API when the UI is ready." | Undefined contracts cause rework; stub or OpenAPI-first. |
| "Backend can go last." | Without shaped data, charts encode wrong assumptions. |
| "Acceptance criteria are obvious." | Obvious criteria diverge across reviewers; write them down. |

## Red Flags

- Tasks that say "implement dashboard" without listed widgets and data fields.
- No task owns **sample fixtures** or seed data for local dev.
- Authz treated as a follow-up task instead of paired with data access.

## Verification

- Task list is **ordered** with noted blockers and parallel tracks.
- Each task has **acceptance criteria** traceable to the spec.
- Critical path for **first demonstrable slice** is identified (demo or screenshot target).
