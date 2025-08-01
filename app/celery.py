from celery import Celery

from app.core.config import settings
from app.services.celery_monitor import start_celery_monitor

celery_app = Celery("hello", broker=settings.REDIS_BROKER_URL, backend=settings.RESULT_BACKEND_URL)

celery_app.autodiscover_tasks(["app.tasks.task"])


# 启动 Celery 监控
start_celery_monitor(celery_app)
