# celery_config.py
from celery import Celery
import tasks
celery_app = Celery(
    'fastapi_celery_download',
    broker='redis://127.0.0.1:6379/',
    backend='redis://127.0.0.1:6379/'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_soft_time_limit=3600,
    worker_time_limit=7200
)

celery_app.autodiscover_tasks(['tasks'])
