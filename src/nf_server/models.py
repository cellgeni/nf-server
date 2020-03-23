import enum
import os
from datetime import datetime as dt
from typing import Dict

from sqlalchemy_utils import ChoiceType

from nf_server import db, jenkins

NEXTFLOW_JOB = os.getenv("NEXTFLOW_JOB_NAME")


class Status(enum.Enum):
    REGISTERED = 0
    STARTED = 1
    SUCCEEDED = 2
    FAILED = 3
    CANCELLED = 4

    mapping = {
        'FAILURE': FAILED,
        'ABORTED': CANCELLED,
        'SUCCESS': SUCCEEDED,
        'NOT_BUILT': STARTED,
        'UNSTABLE': SUCCEEDED
    }

    @classmethod
    def from_jenkins(cls, status):
        return cls.mapping[status]


class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    @staticmethod
    def _append_params(cmd, params):
        if params:
            for param, value in params.items():
                cmd += f" --{param}={value}"
        return cmd

    def build_command(self, params: Dict = None):
        cmd = f"nextflow -log log run {self.name} -resume"
        cmd = self._append_params(cmd, params)
        return cmd

    def __str__(self):
        return self.name


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jenkins_id = db.Column(db.Integer, nullable=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'), nullable=False)
    workflow = db.relationship('Workflow', backref=db.backref('jobs', lazy=True))
    command = db.Column(db.String(200), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False,
                              default=dt.utcnow)
    started_on = db.Column(db.DateTime)
    finished_on = db.Column(db.DateTime)
    status = db.Column(ChoiceType(Status), impl=db.Integer())

    def __str__(self):
        return self.id

    def submit(self):
        queue_num = jenkins.build_job(NEXTFLOW_JOB, {'COMMAND': self.workflow.build_command()})
        queue_item = jenkins.get_queue_item(queue_num)
        job = jenkins.get_build_info(NEXTFLOW_JOB, queue_item['executable']['number'])
        self.jenkins_id = job['id']
        db.session.commit()

    def delete(self):
        jenkins.delete_build(NEXTFLOW_JOB, self.jenkins_id)
        self.status = Status.CANCELLED
        db.session.commit()

    @classmethod
    def update_jobs(cls):
        unfinished = cls.query.filter(cls.status.in_([Status.STARTED, Status.REGISTERED]))
        for job in unfinished:
            jenkins_info = jenkins.get_build_info(NEXTFLOW_JOB, job.jenkins_id)
            job.status = Status.from_jenkins(jenkins_info['status'])
        db.session.commit()
