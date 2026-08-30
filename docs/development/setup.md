# Development Setup

Recommended Windows tools:
1. Git
2. Visual Studio Code
3. Docker Desktop
4. uv
5. GitHub CLI (`gh`)

Verify:
```powershell
git --version
docker --version
docker compose version
uv --version
code --version
gh --version
```

First setup:
```powershell
uv sync
Copy-Item .env.example .env
docker compose up -d
uv run pytest
uv run uvicorn app.main:app --reload
```

Recommended VS Code extensions:
- Python
- Pylance
- Ruff
- Docker
- GitHub Actions
- YAML
- Markdown All in One
- Mermaid Preview

Rules:
- Never commit `.env`.
- Prefer `uv run ...` for project commands.
- Keep `main` stable.
- Use feature branches for non-trivial changes.
