from .execution import async_run
from .celery_app import celery_app


@celery_app.task()
def run_workflow(command):
    return async_run(command)
