from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.invitations import router as invitations_router
from app.api.routes.organizations import router as organizations_router

app = FastAPI(
    title="Intelligent SaaS Platform",
    version="0.1.0",
    description="Portfolio-grade SaaS platform backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return the application health status."""
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(organizations_router)
app.include_router(invitations_router)
