from fastapi import FastAPI

from app.api.routes.auth import router as auth_router

app = FastAPI(
    title="Intelligent SaaS Platform",
    version="0.1.0",
    description="Portfolio-grade SaaS platform backend.",
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return the application health status."""
    return {"status": "ok"}


app.include_router(auth_router)
