import http
import logging
import os
import re
import subprocess
import uuid
from functools import wraps
from time import sleep
from typing import Dict

from flask import Flask, request, jsonify

from .tasks import run_workflow

MAX_RETRIES = 3

class Status:
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


app = Flask(__name__)
auth_token = os.getenv("AUTH_TOKEN", "nfauthtoken")
app.auth_token = auth_token

WORKFLOW_PATH = os.getenv("WORKFLOW_PATH", os.getcwd())


def build_command(dir_name, workflow, wf_params: Dict = None, nf_params: Dict = None):
    cmd = f"cd {dir_name} && nextflow -log log run {workflow} -w work -resume"
    for param, value in wf_params.items():
        cmd += f" --{param}={value}"
    for param, value in nf_params.items():
        cmd += f" -{param} {value}"
    return cmd


def get_wf_status(workflow_id):
    i = 0
    while i < MAX_RETRIES:
        try:
            with open(os.path.join(WORKFLOW_PATH, workflow_id, "log")) as f:
                content = f.readlines()
                logging.info(f"Content: {content}")
                if re.search("Goodbye", content[-1]):
                    return Status.COMPLETED
                else:
                    # job failed condition check
                    pass
                break
        except FileNotFoundError:
            sleep(1)
            i += 1
            pass
    return Status.RUNNING


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
    workdir = os.path.join(WORKFLOW_PATH, wf_name)
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
    status = get_wf_status(workflow_id)
    return jsonify(status=status), http.HTTPStatus.OK


if __name__ == '__main__':
    app.run()
