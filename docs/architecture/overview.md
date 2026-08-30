# Architecture Overview

## Current state — Phase 0

```text
HTTP Client -> FastAPI -> /health
```

## Target architecture

```text
Web/API Client
      |
      v
API / Application
  |           |
  v           v
PostgreSQL   Redis
  |
  v
Async Jobs
  |      |
  v      v
Storage  AI Layer
```

## Principles
1. Start as a modular monolith.
2. Keep domain logic separated from infrastructure.
3. Introduce complexity only when justified.
4. Record major decisions as ADRs.
5. Treat tests, security, observability and deployment as first-class concerns.
