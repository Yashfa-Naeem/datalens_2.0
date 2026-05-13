# DataLens — Product & Engineering Specification

This document defines what DataLens is, how to run and change it, and the boundaries for contributors and automation. It targets the **2015 Flight Delays** analytics experience backed by `flights.csv`, `airlines.csv`, and `airports.csv` (on the order of **5.8M flight rows**).

---

## 1. Objective

### 1.1 What we are building

**DataLens** is a data analytics web application that lets analysts and curious users explore the 2015 U.S. flight delays dataset through:

- **Upload & persistence**: Ingest CSVs, materialize them in **SQLite** (via **SQLAlchemy**), and keep enough metadata to query a chosen dataset safely.
- **Interactive UI**: **React + Vite + Tailwind + Recharts** for filters, charts, and executive-style summaries.
- **Natural language**: **Groq API** with **tool-calling** so the assistant can run constrained **SELECT** SQL (and related preview steps) against the active dataset and explain results in plain language.

The backend is **FastAPI + Python + Pandas**; Python dependencies are managed with **uv**.

### 1.2 User stories

| ID | As a… | I want to… | So that… |
|----|---------|------------|-----------|
| U1 | User | Upload `flights.csv` / `airlines.csv` / `airports.csv` | The app can analyze delays without me running SQL by hand |
| U2 | User | See charts and KPIs for carriers, airports, routes, and time | I can spot delay patterns quickly |
| U3 | User | Apply filters (e.g. carrier, airport, date range) | I can narrow 5.8M rows to a meaningful slice |
| U4 | User | Ask questions in chat (e.g. “Top 10 airports by average departure delay in June”) | I get answers backed by actual aggregates on my data |
| U5 | Operator | Hit a health endpoint | I can verify API + DB readiness in deploy scripts |
| U6 | Developer | Run lint and tests on backend and frontend | Changes stay safe at dataset scale |

### 1.3 Success criteria (specific and testable)

**Performance & scale**

- **SC1**: With a fully loaded `flights` table (~5.8M rows), a **p95** API latency for a **scoped** aggregate request (e.g. single month + single carrier, or result limited to ≤1k rows) completes in **≤ 5 s** on a representative dev machine, without loading the entire result into the browser.
- **SC2**: Upload path enforces documented **row / preview caps** so a single request cannot exhaust server memory (behavior covered by tests or documented limits in code).

**Correctness**

- **SC3**: `/api/health` returns HTTP **200** and JSON `{"status":"ok"}` whenever the app process and database engine are initialized.
- **SC4**: Chat SQL path rejects non-**SELECT** statements, comments, multi-statements, and queries that reference tables other than the dataset’s SQLite table (covered by unit tests on the validator).

**UX**

- **SC5**: With `GROQ_API_KEY` unset, `/api/chat` returns **503** with a clear message (no silent failure).
- **SC6**: Frontend dev server (**5173**) can call the API (**8000**) without CORS errors for configured origins.

**Quality gates**

- **SC7**: **pytest** passes on CI (or locally before merge) for the backend test suite.
- **SC8**: **Vitest** passes for the frontend unit/component suite; **ESLint** reports zero errors on `npm run lint`.

---

## 2. Commands

Assume repository layout with top-level folders `backend/` and `frontend/`. On Windows, use **PowerShell**; paths below use forward slashes for readability.

### 2.1 One-time setup

**Backend (uv)**

```bash
cd backend
uv sync
```

**Frontend (npm; lockfile is `package-lock.json`)**

```bash
cd frontend
npm install
```

**Environment**

Create `backend/.env` (never commit; see `.gitignore`) with at least:

```bash
GROQ_API_KEY=your_key_here
# Optional override:
# GROQ_MODEL=llama-3.3-70b-versatile
```

### 2.2 Development servers

Run **two** terminals.

**API (port 8000)**

```bash
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Web UI (port 5173)**

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`. The API should be reachable at `http://localhost:8000` (CORS allows `http://localhost:5173`).

### 2.3 Build (production assets)

```bash
cd frontend
npm run build
```

Preview the built site locally:

```bash
cd frontend
npm run preview
```

Backend is not “compiled”; production typically runs the same ASGI command without `--reload`, often behind a process manager or container.

### 2.4 Lint

**Frontend**

```bash
cd frontend
npm run lint
```

**Backend (recommended; add Ruff to dev dependencies if not already present)**

```bash
cd backend
uv run ruff check .
uv run ruff format --check .
```

Auto-format (when Ruff is configured):

```bash
cd backend
uv run ruff format .
```

### 2.5 Test

**Backend (pytest)**

```bash
cd backend
uv run pytest
```

Verbose / single file examples:

```bash
cd backend
uv run pytest -q
uv run pytest tests/test_chat_sql.py -v
```

**Frontend (Vitest)**

After Vitest is configured in `package.json` (see §5), run:

```bash
cd frontend
npm run test
```

Watch mode (typical local DX):

```bash
cd frontend
npm run test -- --watch
```

**Full pre-merge check (example script)**

```bash
cd backend && uv run ruff check . && uv run pytest
cd ../frontend && npm run lint && npm run test && npm run build
```

---

## 3. Project structure

High-level layout (only notable entries; generated artifacts omitted).

```text
datalens_2.0/
├── SPEC.md                 # This specification
├── .gitignore              # Ignores .env, *.db, node_modules, dist, etc.
├── docs/                   # Human-written design notes / reports
├── backend/
│   ├── pyproject.toml      # Python project metadata + runtime deps (uv)
│   ├── uv.lock             # Locked Python dependency versions
│   ├── .python-version     # Target CPython for local/CI
│   ├── main.py             # Optional CLI / scratch entry (not the ASGI app)
│   └── app/
│       ├── main.py         # FastAPI app, CORS, router includes, lifespan
│       ├── database.py     # Engine, session, SQLite URL / path
│       ├── models.py       # SQLAlchemy models (datasets, tables, etc.)
│       └── routers/
│           ├── upload.py   # CSV ingest, caps, table naming
│           ├── data.py     # Dataset-scoped tabular reads / metadata
│           ├── profile.py  # Column stats / profiling endpoints
│           ├── summary.py  # Aggregated “executive” metrics
│           └── chat.py     # Groq + tool-calling + safe SQL execution
├── frontend/
│   ├── package.json        # Scripts: dev, build, lint, (test)
│   ├── vite.config.js      # Vite + React plugin
│   ├── eslint.config.js    # Flat ESLint config for JS/JSX
│   ├── index.html
│   ├── public/             # Static assets (favicons, icons)
│   └── src/
│       ├── main.jsx        # React root mount
│       ├── App.jsx         # Top-level layout / routing shell
│       ├── index.css       # Global styles + Tailwind entry
│       ├── api.jsx         # Axios client / API base URL
│       └── components/     # Dashboard, filters, charts, chat, upload
└── .agent/skills/          # Optional Cursor agent skills (not runtime)
```

**Data files (`flights.csv`, `airlines.csv`, `airports.csv`)** are intentionally **not** committed. Place them under a local directory (e.g. `data/raw/`) and upload via the UI or document your ingest workflow. SQLite files (`*.db`) are local artifacts and gitignored.

---

## 4. Code style

### 4.1 Python (backend)

- **Version**: CPython **≥ 3.11** (see `backend/pyproject.toml`).
- **Imports**: Prefer `from __future__ import annotations` in modules that use forward references; group stdlib / third-party / local.
- **Types**: Annotate public functions and Pydantic models; use `typing` / `collections.abc` for containers.
- **FastAPI**: Keep routers thin; push heavy Pandas/SQL into helpers or service functions; return Pydantic response models where practical.
- **SQL safety**: Any user- or model-influenced SQL must go through the same validation rules as `chat.py` (single `SELECT`, no comments, no DDL/DML keywords, single allowed table identifier).
- **Errors**: Use `HTTPException` with stable `detail` strings for client-visible failures; log server-side context with `logging` rather than printing.

**Example (docstring + typing pattern)**

```python
def monthly_delay_summary(df: pd.DataFrame, carrier_col: str) -> pd.DataFrame:
    """Return mean arrival delay by month for the given carrier column."""
    ...
```

### 4.2 JavaScript / React (frontend)

- **Modules**: ES modules (`import` / `export`); `"type": "module"` in `package.json`.
- **Components**: Prefer **function components**; colocate small helpers next to the component file when they are UI-specific.
- **Hooks**: Follow React Hooks rules; extract reusable logic into custom hooks when duplication appears.
- **Styling**: **Tailwind** utility-first; avoid inline styles except for truly dynamic values.
- **Charts**: Use **Recharts** with typed props where helpful; keep chart data shaping out of JSX when it grows beyond a few lines.
- **API**: Centralize base URLs in `src/api.jsx` (or a `src/lib/api.js` if refactored); avoid scattering `http://localhost:8000` across many files long-term.

**Example (fetch via shared client)**

```jsx
import { api } from "../api";

export async function fetchDatasetProfile(datasetId) {
  const { data } = await api.get(`/data/${datasetId}/profile`);
  return data;
}
```

### 4.3 General

- Match existing naming (`snake_case` Python, `camelCase` / `PascalCase` for JS components).
- Prefer small, reviewable commits; do not reformat unrelated files.

---

## 5. Testing strategy

### 5.1 Backend — pytest

**Goals**

- Fast, deterministic tests that **do not require** the full 5.8M-row CSV in CI.
- Cover **SQL validation**, router contracts, and Pandas transforms on **synthetic mini DataFrames** or small SQLite fixtures created in `tmp_path`.

**Layout (recommended)**

```text
backend/tests/
├── conftest.py           # Fixtures: TestClient, temp DB, sample frames
├── test_health.py
├── test_upload_smoke.py
├── test_data_queries.py
└── test_chat_sql.py      # Validator + tool loop edge cases
```

**Patterns**

- Use `fastapi.testclient.TestClient` against `app.main:app` for HTTP-level assertions.
- For DB, use a file URL to a **temporary** SQLite path per test session or per test to avoid coupling to developer machines.
- Parametrize forbidden SQL strings (comments, `DROP`, second `;`, wrong table name).
- Any test that calls Groq must be **opt-in** (e.g. `@pytest.mark.integration` + env var) so CI stays offline and free.

**Example commands**

```bash
cd backend
uv run pytest
uv run pytest -m "not integration"
```

### 5.2 Frontend — Vitest

**Goals**

- Unit-test pure helpers (formatting, filter builders, chart data mappers).
- Component tests for critical UI (e.g. filter state, empty/error states) using **Vitest** + **@testing-library/react** + **jsdom**.

**Setup expectations**

- Add dev dependencies: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom` (exact versions pinned in `package-lock.json`).
- Extend `vite.config.js` with `test: { environment: "jsdom", globals: false }` and wire `npm run test` to `vitest run`.

**Conventions**

- Colocate tests as `*.test.jsx` next to components **or** under `src/__tests__/` — pick one convention per area and stay consistent.
- Prefer testing behavior (labels, ARIA roles, user-visible outcomes) over snapshot spam.

**Example command**

```bash
cd frontend
npm run test
```

### 5.3 Coverage and CI (recommended targets)

- **Backend**: ≥ **80%** line coverage on `app/routers/chat.py` and SQL validation helpers once introduced; pragmatic lower bar on glue code.
- **Frontend**: Focus coverage on non-trivial logic; do not chase 100% on presentational wrappers.
- CI should run: **ruff** (if adopted) + **pytest** + **eslint** + **vitest** + **vite build**.

---

## 6. Boundaries

| Category | Guidance |
|----------|-----------|
| **Always do** | Run **lint + tests** before opening a PR; keep API **backwards compatible** or version endpoints; validate and parameterize **all** SQL touching user data; respect **row caps** and timeouts for large CSVs; keep **secrets** in `.env` only; match this spec’s stack (**React/Vite/Tailwind/Recharts**, **FastAPI/Pandas/SQLite**, **Groq tool-calling**, **uv** for Python). |
| **Ask first** | Adding new **dependencies**; changing **database schema** or migration strategy; introducing **background workers** or job queues; swapping **LLM vendor** or model; storing **PII** beyond what the public dataset implies; changing **CORS** origins or auth model; large **UI redesign** that breaks user workflows. |
| **Never do** | Commit **`.env`**, API keys, or tokens; commit **multi-gigabyte** CSVs or local `*.db` files; disable **SQL validation** to “make the model work”; run **unbounded** `SELECT *` from the browser or return millions of rows to the client; `print()` secrets or log **full** user queries if they may contain sensitive text; bypass **code review** for security-sensitive changes. |

---

## Document control

- **Owner**: DataLens core team (or solo maintainer) should keep this file updated when commands, ports, or architecture change.
- **Review cadence**: Revisit after any major feature in §1 (new data source, auth, or deployment target).
