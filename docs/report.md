# DataLens - Final Project Report

## What the Agent Did Well
The coding agent (Cursor) performed exceptionally well at generating boilerplate code. When asked to create the FastAPI backend structure, it produced all 6 endpoints with proper error handling, CORS configuration, and Pydantic validation in a single prompt. The agent correctly identified that a 5.8M row CSV needed sampling for SQLite performance and implemented 100k row sampling without being asked.

The agent also did well at understanding the tool-calling pattern for Groq integration. It correctly structured the chat endpoint with function definitions that the LLM could invoke to query the dataset.

## Where We Had to Intervene
1. The agent initially tried to skip writing tests, saying it would add them later. We pushed back and required tests to be written alongside the implementation.

2. When setting up the database, the agent used a hardcoded table name instead of dynamic table names per dataset. We caught this and redirected it to use dataset-specific table names so multiple CSVs could be stored.

3. The agent generated a CORS configuration that only allowed one origin. We corrected it to properly allow localhost:5173 for the React frontend.

## What We Would Do Differently
- Start the frontend earlier in parallel with backend
- Write more granular tasks in todo.md from day one
- Test the full stack integration earlier instead of at the end

## How the 6 Skills Affected Agent Behavior
- spec-driven-development: Forced us to write SPEC.md before any code, which prevented scope creep
- planning-and-task-breakdown: Helped us break work into small verifiable chunks
- incremental-implementation: Kept us from writing too much code at once
- test-driven-development: Reminded us to write tests alongside code
- documentation-and-adrs: Prompted us to document decisions as they happened
- git-workflow-and-versioning: Kept our commits atomic and descriptive

## Maria's Contribution

I built the LLM Chat Interface (ChatPanel.jsx) and Executive Summary 
(ExecutiveSummary.jsx) components. These connect to the Groq AI backend 
to provide natural language data querying and automated insights generation.