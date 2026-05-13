# DataLens — Task Breakdown

## Task 1 - Project Setup
Files: README.md, .gitignore, .env.example, pyproject.toml
Acceptance: Repo exists, dependencies install, env vars documented

## Task 2 - Agent Skills
Files: .agent/skills/*/SKILL.md (6 files)
Acceptance: All 6 SKILL.md files present with methodology content

## Task 3 - Database Layer
Files: backend/app/database.py, backend/app/models.py
Acceptance: SQLite database creates successfully, tables exist

## Task 4 - CSV Upload Endpoint
Files: backend/app/routers/upload.py
Acceptance: Valid CSV uploads successfully, invalid files rejected with clear errors, 50MB limit enforced

## Task 5 - Data Profiling Endpoint
Files: backend/app/routers/profile.py
Acceptance: Returns column types, null counts, min, max, mean, median for all columns

## Task 6 - Data Retrieval Endpoint
Files: backend/app/routers/data.py
Acceptance: Returns paginated data from SQLite, page size configurable

## Task 7 - Groq Chat Endpoint
Files: backend/app/routers/chat.py
Acceptance: Accepts natural language questions, returns data-grounded answers using tool-calling

## Task 8 - Executive Summary Endpoint
Files: backend/app/routers/summary.py
Acceptance: Returns coherent business summary referencing actual data patterns

## Task 9 - React Frontend
Files: frontend/src/App.jsx, frontend/src/components/*
Acceptance: App loads at localhost:5173, CSV upload works, dashboard shows charts

## Task 10 - Global Filters
Files: frontend/src/components/Filters.jsx
Acceptance: Filters apply across all visualizations simultaneously, clearing restores original view

## Task 11 - Tests
Files: backend/tests/, frontend/tests/
Acceptance: 10 pytest tests pass, 5 Vitest tests pass

## Task 12 - Documentation
Files: docs/adrs/*.md, docs/report.md, README.md
Acceptance: 3 ADRs written, report reflects on agent experience, README works on clean install
