import http
from time import sleep

import bravado
import bravado.exception
import pytest


def test_ping(client):
    assert client.ping.pingNextflowServer().response().metadata.status_code == http.HTTPStatus.OK


# def test_submit_existing(client):
#     r = client.submit.submitWorkflow(body={"workflow": "hello"}).response()
#     assert r.metadata.status_code == http.HTTPStatus.ACCEPTED

#
# def test_basic_workflow(client, basic_nf):
#     r = client.submit.submitWorkflow(body=basic_nf).response()
#     assert r.metadata.status_code == http.HTTPStatus.ACCEPTED
#     workflow_id = r.result.get("workflow_id")
#     r = client.status.checkWorkflowStatus(workflow_id=workflow_id).response()
#     assert r.result.get("status") == "RUNNING"
#     sleep(15)
#     r = client.status.checkWorkflowStatus(workflow_id=workflow_id).response()
#     assert r.result.get("status") == "COMPLETED"
#
#
# def test_basic_workflow_failing(client, basic_nf_failing):
#     r = client.submit.submitWorkflow(body=basic_nf_failing).response()
#     assert r.metadata.status_code == http.HTTPStatus.ACCEPTED
#     workflow_id = r.result.get("workflow_id")
#     r = client.status.checkWorkflowStatus(workflow_id=workflow_id).response()
#     assert r.result.get("status") == "RUNNING"
#     sleep(8)
#     r = client.status.checkWorkflowStatus(workflow_id=workflow_id).response()
#     assert r.result.get("status") == "FAILED"
#     assert r.result.get("error_code") == 1
#
#
# def test_submit_unauthenticated(unauthenticated_client):
#     with pytest.raises(bravado.exception.HTTPUnauthorized):
#         assert unauthenticated_client.ping.pingNextflowServer().response().metadata.status_code == http.HTTPStatus.UNAUTHORIZED
#         assert unauthenticated_client.submit.submitWorkflow(
#             body={"workflow": "hello"}).response().metadata.status_code == http.HTTPStatus.UNAUTHORIZED

# def test_submit_non_existent(client):
#     assert client.submit.submitWorkflow(body={"workflow": "hell"})
#            .response().metadata.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY

# nextflow run cellgeni/tracer --samplefile=samples.txt --genome=GRCh38 -c nf.config -profile docker --studyid=4187 -resume
