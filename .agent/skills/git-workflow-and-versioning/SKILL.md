---
name: git-workflow-and-versioning
description: >-
  Trunk-friendly Git practices for analytics web apps: small atomic commits,
  branch hygiene, meaningful messages, and versioning for APIs and releases.
  Use for every code change and when preparing releases or hotfixes.
---

# Git Workflow and Versioning (Data Analytics Web App)

## Overview

Treat Git history as an **audit trail** for data-facing software. Prefer short-lived branches, frequent integration to the mainline, and **atomic commits** that each leave the project in a buildable state when possible. Commit messages should help future you trace **why** a metric or query changed—especially when investigations tie to customer incidents or regulatory questions.

## When to Use

- Always, for any tracked change.
- Preparing releases, hotfixes, or schema migrations with coordination needs.
- When tagging API or **semantic** breaking changes (metric redefinitions count).

## Process

1. **Branch from updated main** — Sync before substantive work; avoid stale analytics SQL on old schema.
2. **Commit as save points** — One logical change per commit; mix refactors with behavior changes only when inseparable and then say so in the message.
3. **Message discipline** — Imperative subject (~50 chars), body explains motivation, metrics, risk, and rollback notes if non-obvious.
4. **Keep PRs reviewable** — Target small diffs; split data and UI when independent; attach query plans or screenshots for visual changes.
5. **Rebase or merge per team norm** — Prefer linear history only if the team agrees; never rewrite shared history without coordination.
6. **Versioning** — Tag app releases SemVer-style where applicable; version **public APIs** explicitly when consumers exist outside the repo.
7. **Cherry-pick hotfixes** — Port critical fixes back to release branches with the same commit message context and linked incident ID.

## Rationalizations

| Excuse | Rebuttal |
|--------|----------|
| "Squash will hide messy commits." | Squash is fine if the retained message documents the **why** and risk. |
| "I'll push everything Friday." | Large pushes delay review and bisect when dashboards break. |
| "The migration can't be split." | Often the DDL and the app toggle can still be separate commits. |
| "Semantic versioning doesn't apply to internal apps." | APIs and embedded exports still have consumers; signal breaking changes. |

## Red Flags

- Commits titled `fix` / `wip` / `updates` with no body.
- PRs mixing unrelated refactors with **metric definition** changes.
- Force-push to shared branches without team agreement.

## Verification

- PR description links spec/ticket and calls out **data** or **auth** impact.
- CI passed on the latest pushed commit before merge.
- Release or API change has a **tag, changelog entry, or ADR** per team policy.
