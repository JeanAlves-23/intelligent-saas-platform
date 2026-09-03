# Intelligent SaaS Platform

> Portfolio project: a production-oriented SaaS platform evolving from a clean FastAPI core into a full-stack, cloud-native and AI-enabled system.

## Status
**Phase 0 — Foundation**

## Vision
Build a realistic multi-tenant SaaS product that demonstrates:
- Python + FastAPI
- PostgreSQL
- Redis
- Authentication and authorization
- Automated testing
- Docker
- GitHub Actions
- AWS
- Terraform
- Observability and security
- React/Next.js
- AI with RAG and LLM APIs

## Architecture

```text
Client -> FastAPI -> PostgreSQL
                 -> Redis
                 -> Background Jobs
                 -> Object Storage
                 -> AI Services
```

See [Architecture Overview](docs/architecture/overview.md).

## Local development

Prerequisites:
- Python 3.13
- uv
- Docker Desktop
- Git

```powershell
uv sync
Copy-Item .env.example .env
docker compose up -d
uv run pytest
uv run uvicorn app.main:app --reload
```

Open:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Quality checks:
```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Engineering standards
- Small, focused commits
- Pull requests for meaningful changes
- Automated tests for behavior
- No secrets committed to Git
- Documentation for architectural decisions
- CI must be green before merge

## Roadmap
See [PROJECT.md](PROJECT.md).

## License
MIT

## Development Workflow

This project follows a pull-request-based development workflow.

Changes are developed in feature branches, validated by automated tests and quality checks, and merged into `main` only after CI passes.