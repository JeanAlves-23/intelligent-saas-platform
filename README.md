# Intelligent SaaS Platform

A production-oriented SaaS backend built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, multi-tenancy, RBAC, automated tests, and CI.

The project is designed as a portfolio-grade SaaS foundation with emphasis on clean architecture, tenant isolation, authorization, database integrity, and professional development workflow.

## Core Features

- User registration
- JWT authentication
- Current-user endpoint
- Organization creation
- Organization listing
- Organization update
- Organization deletion
- Multi-tenant organization access
- Membership management
- Organization RBAC
- Organization member listing
- Membership role updates
- Organization invitations
- Secure invitation tokens
- Invitation expiration
- Invitation acceptance
- Automatic membership creation
- PostgreSQL persistence
- Alembic database migrations
- Automated integration tests
- Ruff linting and formatting
- GitHub Actions CI
- Docker-based local infrastructure

## Technology Stack

### Backend

- Python 3.13
- FastAPI
- SQLAlchemy
- Pydantic
- PyJWT
- pwdlib with Argon2

### Database

- PostgreSQL
- Alembic

### Infrastructure

- Docker
- Docker Compose
- Redis

### Quality

- pytest
- Ruff
- GitHub Actions

## Architecture

The current domain model centers around users, organizations, memberships, and invitations.

```text
User
 |
 +---- Membership ---- Organization
 |                         |
 |                         +---- Members
 |                         +---- Roles
 |                         +---- Invitations
 |
 +---- Invitation Acceptance
```

A user can belong to multiple organizations through memberships.

Each membership defines the user's role inside a specific organization.

The current role hierarchy is:

```text
owner
  |
admin
  |
member
```

Higher roles inherit the permissions of lower roles.

## Multi-Tenancy

Organizations represent tenant boundaries.

Access to organization-scoped resources requires:

1. Authentication.
2. Membership in the requested organization.
3. Sufficient role for the requested operation.

This prevents users from accessing resources belonging to organizations where they do not have membership.

## Authentication

Authentication uses JWT access tokens.

Main authentication endpoints:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

Protected endpoints expect:

```text
Authorization: Bearer <access-token>
```

Passwords are never stored in plaintext.

Password hashing uses Argon2 through `pwdlib`.

## Organizations

Supported organization operations:

```text
GET    /organizations
POST   /organizations
GET    /organizations/{organization_id}
PATCH  /organizations/{organization_id}
DELETE /organizations/{organization_id}
```

Organization creators automatically receive an `owner` membership.

### Authorization

```text
Create organization -> authenticated user
Read organization   -> organization member
Update organization -> admin or owner
Delete organization -> owner
```

## Memberships

Organization membership endpoints:

```text
GET   /organizations/{organization_id}/members
PATCH /organizations/{organization_id}/members/{membership_id}
```

Member listing requires at least the `admin` role.

Membership role updates require the `owner` role.

Supported organization roles:

```text
owner
admin
member
```

## Invitations

Authorized users can invite new members into an organization.

Create invitation:

```text
POST /organizations/{organization_id}/invitations
```

Accept invitation:

```text
POST /invitations/{token}/accept
```

### Invitation Rules

```text
owner -> can invite admin or member
admin -> can invite member
member -> cannot create invitations
```

The `owner` role cannot be assigned through invitations.

Invitation tokens are generated using Python's cryptographically secure `secrets` module.

Invitations expire after a limited validity period and cannot be reused after acceptance.

The authenticated user's email must match the email associated with the invitation.

Successful acceptance creates the corresponding organization membership.

## Database

PostgreSQL is used as the primary database.

Database access is implemented with SQLAlchemy.

Schema evolution is handled with Alembic.

Apply all migrations with:

```powershell
uv run alembic upgrade head
```

Check the current migration:

```powershell
uv run alembic current
```

Check migration history:

```powershell
uv run alembic history
```

## Local Development

### Requirements

- Python 3.13+
- uv
- Docker Desktop
- Git

### Start Infrastructure

```powershell
docker compose up -d
```

Check containers:

```powershell
docker compose ps
```

### Install Dependencies

```powershell
uv sync
```

### Configure Environment

Create a `.env` file based on `.env.example`.

Typical variables include:

```text
APP_ENV=development
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/intelligent_saas
REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=replace-with-a-secure-random-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Do not commit real secrets.

### Apply Migrations

```powershell
uv run alembic upgrade head
```

### Run the API

```powershell
uv run uvicorn app.main:app --reload
```

The application will normally be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Testing

Run the complete test suite:

```powershell
uv run pytest
```

Run a specific test file:

```powershell
uv run pytest tests/integration/test_invitation_api.py -v
```

The integration tests use PostgreSQL and validate critical flows including:

- Authentication
- Organization lifecycle
- Multi-tenant authorization
- RBAC
- Membership management
- Invitation creation
- Invitation acceptance
- Database constraints
- Cascade deletion

## Code Quality

Run Ruff linting:

```powershell
uv run ruff check .
```

Check formatting:

```powershell
uv run ruff format --check .
```

Apply formatting:

```powershell
uv run ruff format .
```

Automatically fix supported lint issues:

```powershell
uv run ruff check . --fix
```

## Continuous Integration

GitHub Actions validates every Pull Request.

The CI pipeline:

```text
Checkout
   |
   v
Install Python / uv
   |
   v
Start PostgreSQL
   |
   v
Apply Alembic migrations
   |
   v
Ruff lint
   |
   v
Ruff format check
   |
   v
pytest
```

Changes are merged into `main` only after the required checks pass.

## Development Workflow

The project follows a branch and Pull Request workflow.

Typical flow:

```text
Issue
  |
  v
Branch
  |
  v
Implementation
  |
  v
Tests
  |
  v
Commit
  |
  v
Pull Request
  |
  v
CI
  |
  v
Merge
```

Branch examples:

```text
feature/28-organization-invitations
fix/...
docs/...
chore/...
```

Conventional commits are used where appropriate.

Examples:

```text
feat: add organization invitation service
fix: organize membership service test imports
docs: document organization invitation flow
chore: remove temporary validation endpoint
```

## Backend Core v1

The current milestone includes:

- Authentication
- Users
- Organizations
- Multi-tenancy
- Memberships
- RBAC
- Organization CRUD
- Member management
- Invitations
- Invitation acceptance
- PostgreSQL
- Alembic
- Integration tests
- CI

## Roadmap

Planned next phases:

```text
Backend Core v1
      |
      v
Frontend
      |
      v
Redis + Background Jobs
      |
      v
Deployment
      |
      v
AWS
      |
      v
Terraform
      |
      v
Observability
      |
      v
Security Hardening
      |
      v
AI / RAG
```

## Current Status

Backend Core v1 is the current completed foundation of the platform.

The next major milestone is the frontend, which will expose the existing authentication, organization, membership, RBAC, and invitation capabilities through a complete user interface.

## Frontend

The frontend is built with React, TypeScript, and Vite.

### Frontend Stack

- React
- TypeScript
- Vite
- React Router
- Axios
- TanStack Query
- ESLint
- Prettier

### Frontend Structure

```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── features/
│   ├── hooks/
│   ├── layouts/
│   ├── pages/
│   ├── router/
│   ├── services/
│   └── types/
├── .env.example
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### Frontend Environment

Create:

```text
frontend/.env
```

based on:

```text
frontend/.env.example
```

Example:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Run the Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

### Initial Routes

```text
/
/login
/register
/dashboard
```

### Backend Integration

The frontend uses Axios for HTTP communication and TanStack Query for server-state management.

The API base URL comes from:

```text
VITE_API_BASE_URL
```

The initial integration validates communication with:

```text
GET /health
```

### Frontend Validation

Run:

```powershell
cd frontend
npm run lint
npm run format:check
npm run build
```

### CORS

The FastAPI backend allows local frontend development from:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Production CORS configuration will be handled separately during deployment.