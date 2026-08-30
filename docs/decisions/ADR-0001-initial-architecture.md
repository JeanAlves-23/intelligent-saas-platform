# ADR-0001 — Initial Architecture

- Status: Accepted
- Date: 2026-08-30

## Context
This portfolio project should demonstrate practical engineering without unnecessary initial complexity.

## Decision
Use Python 3.13, FastAPI, SQLAlchemy 2.x, PostgreSQL, Redis, Docker Compose, uv, Ruff, Pytest and GitHub Actions. Start as a modular monolith.

## Consequences
This gives fast feedback, simple local setup and a clear path to cloud deployment. Microservices will be introduced only when a concrete requirement justifies them.
