import http

from flask import request, jsonify

from nf_server import app
from nf_server.helpers import auth_required
from nf_server.models import Workflow, Job


@app.route('/ping')
def ping():
    return jsonify(message="Nextflow server is up and running!"), http.HTTPStatus.OK


@app.route('/jobs', methods=["POST"])
@auth_required
def submit_job():
    data = request.args or request.get_json()
    workflow = data.get("workflow", "")
    params = data.get("params", {})
    wf = Workflow.query.get(name=workflow)
    command = wf.build_command(params)
    job = Job(workflow=wf, command=command)
    return jsonify(workflow_id=job.id), http.HTTPStatus.ACCEPTED


@app.route('/jobs/<job_id>', methods=["GET"])
@auth_required
def get_job(job_id):
    job = Job.query.get(id=job_id)
    return jsonify(status=job.status), http.HTTPStatus.OK


@app.route('/jobs/<job_id>', methods=["DELETE"])
@auth_required
def delete_job(job_id):
    job = Job.query.get(id=job_id)
    job.delete()
    return jsonify(status=job.status), http.HTTPStatus.OK


if __name__ == '__main__':
    app.run()
