from celery import Celery
from core.config import settings

celery_app = Celery(
    'worker',
    backend=settings.REDIS_BACKEND,
    broker=settings.REDIS_BACKEND
)
celery_app.conf.task_routes = {'tasks.celery_worker.*': {'queue': 'main'}}
celery_app.conf.update(task_track_started=True)
