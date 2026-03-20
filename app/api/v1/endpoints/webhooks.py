import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.config import settings
from app.db.models.repository import Repository
from app.db.models.webhook_event import WebhookEvent
from app.workers.tasks import run_analysis_job
from app.db.models.analysis_job import AnalysisJob

router = APIRouter()


def _verify_github_signature(payload: bytes, signature_header: str | None) -> bool:
    """Verify X-Hub-Signature-256 from GitHub."""
    if not signature_header:
        return False
    if not settings.WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured
    expected = "sha256=" + hmac.new(
        settings.WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
):
    """Receive and process GitHub webhook push events."""
    payload_bytes = await request.body()

    if not _verify_github_signature(payload_bytes, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = x_github_event or "unknown"

    # Only process push events
    if event_type not in ("push", "create"):
        return {"status": "ignored", "event": event_type}

    # Identify the repository
    gh_repo = payload.get("repository", {})
    full_name = gh_repo.get("full_name", "").lower()

    repo = db.query(Repository).filter(Repository.full_name == full_name).first()

    # Store webhook event  
    event = WebhookEvent(
        repository_id=repo.id if repo else None,
        event_type=event_type,
        delivery_id=request.headers.get("X-GitHub-Delivery", "unknown"),
        payload_json=payload,
        status="received",
    )
    db.add(event)

    if repo:
        # Trigger analysis job
        branch_ref = payload.get("ref", "")
        branch = branch_ref.replace("refs/heads/", "") if branch_ref.startswith("refs/heads/") else None
        commit_sha = payload.get("after") or payload.get("head_commit", {}).get("id")

        job = AnalysisJob(
            repository_id=repo.id,
            status="pending",
            trigger_source="webhook",
            branch=branch,
            commit_sha=commit_sha,
        )
        db.add(job)
        db.flush()

        event.processed_at = datetime.now(timezone.utc)
        event.status = "processed"
        db.commit()

        run_analysis_job.delay(str(job.id))
        return {"status": "queued", "job_id": str(job.id)}

    db.commit()
    return {"status": "repository_not_registered"}
