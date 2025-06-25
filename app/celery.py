from celery import Celery

from app.core.config import settings
from app.services.celery_monitor import start_celery_monitor

celery_app = Celery("hello", broker=settings.REDIS_BROKER_URL)

celery_app.autodiscover_tasks(["app.tasks.task"])

start_celery_monitor(celery_app)
