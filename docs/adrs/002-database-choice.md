# ADR 002 - Database Selection

## Context
DataLens needs to persist uploaded CSV data so page refresh does not lose data. We needed a database that is simple to set up, requires no separate server, and works cross-platform.

## Options Considered
1. PostgreSQL - powerful but requires separate server installation and configuration
2. MySQL - same issue as PostgreSQL, too heavy for local development
3. MongoDB - good for flexible schemas but overkill for tabular CSV data
4. SQLite - file-based, no server needed, works everywhere, perfect for local apps

## Decision
We chose SQLite with SQLAlchemy ORM.

## Trade-offs
- We gain: zero configuration, single file database, works cross-platform, no server needed
- We lose: not suitable for production with multiple concurrent users
- SQLite is perfect for this project scope which explicitly excludes production deployment
