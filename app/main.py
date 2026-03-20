from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import health, auth, repositories, analysis, reports, webhooks

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json"
)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(repositories.router, prefix="/api/v1/repositories", tags=["repositories"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(webhooks.router, prefix="/api/v1", tags=["webhooks"])

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the GitHub Repo Risk Analyzer API"}
