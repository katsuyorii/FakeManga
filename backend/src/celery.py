import sys

from pathlib import Path

from celery import Celery

from .config import settings


sys.path.append(str(Path(__file__).resolve().parent.parent))

celery_app = Celery(
    'worker',
    broker=settings.RABBIT_MQ_URL,
)

celery_app.autodiscover_tasks(["auth"])