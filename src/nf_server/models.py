import enum
from datetime import datetime as dt
from typing import Dict

from sqlalchemy_utils import ChoiceType

from nf_server import db


class Status(enum.Enum):
    REGISTERED = 0
    STARTED = 1
    SUCCEEDED = 2
    FAILED = 3
    CANCELLED = 4


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

    def delete(self):
        pass