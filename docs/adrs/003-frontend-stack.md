# ADR 003 - Frontend Stack Selection

## Context
DataLens needs a modern frontend framework for building an interactive dashboard with charts, filters, and chat interface.

## Options Considered
1. Vue.js - good option but smaller ecosystem than React
2. Angular - too heavy and complex for a 3 week project
3. Plain HTML/JS - too slow to build, no component reusability
4. React + Vite - fast build tool, huge ecosystem, required by project spec

## Charts Library
1. Chart.js - simpler but less React integration
2. Plotly - more features but heavier bundle size
3. Recharts - built specifically for React, declarative API, lightweight

## Decision
We chose React with Vite and Recharts for charts.

## Trade-offs
- We gain: fast development, component reusability, excellent Recharts integration with React
- We lose: slightly more complex setup than plain HTML
- React is the industry standard and aligns with project requirements
