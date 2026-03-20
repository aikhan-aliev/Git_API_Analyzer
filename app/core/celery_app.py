from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "repo_analyzer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

celery_app.conf.task_routes = {"app.workers.tasks.*": "main-queue"}
