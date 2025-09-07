from celery import Celery

from app.core.config import settings
from app.services.celery_monitor import start_celery_monitor

celery_app = Celery("hello", broker=settings.REDIS_BROKER_URL, backend=settings.RESULT_BACKEND_URL)

# 加载配置
celery_app.config_from_object("app.core.celeryconfig")

# 加载任务
celery_app.autodiscover_tasks(["app.tasks.task"])


# 启动 Celery 监控
start_celery_monitor(celery_app)
