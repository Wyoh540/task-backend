from celery import Celery

from app.core.config import settings

celery_app = Celery("hello", broker=settings.REDIS_BROKER_URL)

celery_app.autodiscover_tasks(["app.task.task"])
