import http
import os
import re
import subprocess
import uuid
from functools import wraps
from threading import Thread
from typing import Dict

from flask import Flask, request, jsonify

from execution import async_run


class Status:
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


app = Flask(__name__)
auth_token = os.getenv("AUTH_TOKEN", "nfauthtoken")
app.auth_token = auth_token


def build_command(dir_name, workflow, wf_params: Dict = None, nf_params: Dict = None):
    cmd = f"nextflow -log {dir_name}/log run {workflow} -w {dir_name}"
    for param, value in wf_params:
        cmd += f" -{param} {value}"
    for param, value in nf_params:
        cmd += f" -{param} {value}"
    return cmd


def get_wf_status(workflow_id):
    with open(os.path.join(workflow_id, "log")) as f:
        if re.search("Goodbye", f.readlines()[-1]):
            return Status.COMPLETED
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
    # wf_name: str, wf_params: Dict, nf_params: Dict
    data = request.args or request.get_json()
    workflow = data.get("workflow", "")
    wf_params = data.get("wf_params", {})
    nf_params = data.get("nf_params", {})
    dir_name = str(uuid.uuid4())
    os.mkdir(dir_name)
    command = build_command(dir_name, workflow, wf_params, nf_params)
    t = Thread(target=async_run(command=command))
    t.start()

    return jsonify(workflow_id=dir_name), http.HTTPStatus.ACCEPTED


@app.route('/status/<workflow_id>', methods=["GET"])
@auth_required
def check_status(workflow_id):
    status = get_wf_status(workflow_id)
    return jsonify(status=status), http.HTTPStatus.OK


if __name__ == '__main__':
    app.run()