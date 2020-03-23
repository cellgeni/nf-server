import os

from celery.task import PeriodicTask
from datetime import timedelta

from nf_server.models import Job


class UpdateJobStatusTask(PeriodicTask):
    run_every = timedelta(seconds=os.getenv('STATUS_CHECKING_INTERVAL_SEC', 5))

    def run(self, **kwargs):
        Job.update_jobs()