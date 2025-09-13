
import os
from celery import Celery

CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery = Celery("eddsec", broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery.autodiscover_tasks(["worker", "worker.plugins"])
