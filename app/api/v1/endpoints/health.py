from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/ready")
def readiness_check() -> dict[str, str]:
    # Future: add DB readiness checks here
    return {"status": "ready"}
