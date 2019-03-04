import os

from celery import Celery

CELERY_BROKER_URL = 'CELERY_BROKER_URL'
CELERY_RESULT_BACKEND = 'CELERY_RESULT_BACKEND'
MB = 1024 * 1024

app_config = dict()

app_config['MAX_CONTENT_LENGTH'] = 400 * MB
app_config[CELERY_BROKER_URL] = os.getenv(CELERY_BROKER_URL, 'redis://localhost:6379/0')
app_config[CELERY_RESULT_BACKEND] = os.getenv(CELERY_RESULT_BACKEND, 'redis://localhost:6379/0')

celery_app = Celery("nf_server", broker=app_config[CELERY_BROKER_URL], backend=app_config[CELERY_RESULT_BACKEND])
celery_app.conf.update(app_config)
celery_app.autodiscover_tasks(packages=["nf_server"])
