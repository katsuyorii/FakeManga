from celery import Celery

from .config import settings


celery_app = Celery(
    'worker',
    broker=settings.RABBIT_MQ_URL,
)