import http
import logging
import os
import re
import subprocess
import uuid
from abc import ABC, abstractmethod
from functools import wraps
from time import sleep
from typing import Dict

from flask import Flask, request, jsonify

from .tasks import run_workflow

BASE_PATH = 'BASE_PATH'


class Status:
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Workflow:

    def __init__(self, id):
        self.id = id


class WorkflowTracker(ABC):
    """
    an abstract class is needed cause there can be other ways to track workflow status,
    e.g. Nextflow Tower, then we would query Tower's API for the workflow status
    """

    @staticmethod
    @abstractmethod
    def get_wf_status(workflow_id):
        pass


class FileSystemWorkflowTracker(WorkflowTracker):

    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    @staticmethod
    def _construct_log_path(workflow):
        return os.path.join(app.config[BASE_PATH], workflow.id, "log")

    def _parse_log_status(self, workflow):
        with open(self._construct_log_path(workflow)) as f:
            content = f.read().strip()
            lines = content.split('\n')
            logging.info(f"Content: {lines}")
            if re.search("Goodbye", lines[-1]):
                m = re.search(r"(exit status)(\D*)(\d+)", content)
                if m:
                    exit_code = m.groups()[2]
                    return Status.FAILED, int(exit_code)
                else:
                    return Status.COMPLETED, None
            return Status.RUNNING, None

    def get_wf_status(self, workflow: Workflow):
        TIMEOUT = 1
        i = 0
        while i < self.max_retries:
            try:
                return self._parse_log_status(workflow)
            except FileNotFoundError:
                sleep(TIMEOUT)
                i += 1
                pass
        return Status.RUNNING, None


class NfServerApp(Flask):

    def __init__(self):
        super().__init__(__name__)
        self.workflow_tracker = FileSystemWorkflowTracker()
        self._init_configs()

    def _init_configs(self):
        auth_token = os.getenv("AUTH_TOKEN", "nfauthtoken")
        self.auth_token = auth_token
        self.config[BASE_PATH] = os.getenv(BASE_PATH, os.getcwd())

    def get_wf_status(self, workflow_id):
        workflow = Workflow(workflow_id)
        return self.workflow_tracker.get_wf_status(workflow)


app = NfServerApp()


def build_command(dir_name, workflow, wf_params: Dict = None, nf_params: Dict = None):
    cmd = f"cd {dir_name} && nextflow -log log run {workflow} -w work -resume"
    for param, value in wf_params.items():
        cmd += f" --{param}={value}"
    for param, value in nf_params.items():
        cmd += f" -{param} {value}"
    return cmd


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get("X-API-Key") != app.auth_token:
            return jsonify(message="Auth token missing from the request"), http.HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)

    return decorated_function


@app.route('/ping')
@auth_required
def ping():
    if subprocess.run("nextflow -version".split()).returncode == 0:
        return jsonify(message="Nextflow server is up and running!"), http.HTTPStatus.OK
    else:
        return jsonify(message="Nextflow is not running"), http.HTTPStatus.SERVICE_UNAVAILABLE


@app.route('/submit', methods=["POST"])
@auth_required
def submit_workflow():
    data = request.args or request.get_json()
    workflow = data.get("workflow", "")
    wf_params = data.get("wf_params", {})
    nf_params = data.get("nf_params", {})
    file_inputs = data.get("file_inputs", {})
    wf_name = str(uuid.uuid4())
    workdir = os.path.join(BASE_PATH, wf_name)
    os.mkdir(workdir)
    for filename, content in file_inputs.items():
        with open(os.path.join(workdir, filename), 'w') as f:
            f.write(content)
    command = build_command(workdir, workflow, wf_params, nf_params)
    run_workflow.delay(command=command)
    return jsonify(workflow_id=wf_name), http.HTTPStatus.ACCEPTED


@app.route('/status/<workflow_id>', methods=["GET"])
@auth_required
def check_status(workflow_id):
    status, error_code = app.get_wf_status(workflow_id)
    # swagger 2.0 doesn't support null type
    if error_code:
        return jsonify(status=status, error_code=error_code), http.HTTPStatus.OK
    else:
        return jsonify(status=status), http.HTTPStatus.OK


if __name__ == '__main__':
    app.run()
