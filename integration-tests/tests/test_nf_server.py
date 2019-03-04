# nextflow run cellgeni/tracer --samplefile=samples.txt --genome=GRCh38 -c nf.config -profile docker --studyid=4187 -resume
import http
from time import sleep

import bravado
import bravado.exception
import pytest


def test_ping(client):
    assert client.ping.pingNextflowServer().response().metadata.status_code == http.HTTPStatus.OK


def test_submit_existing(client):
    r = client.submit.submitWorkflow(body={"workflow": "hello"}).response()
    assert r.metadata.status_code == http.HTTPStatus.ACCEPTED


def test_basic_workflow(client):
    with open("basic_nf/basic.nf") as f1:
        wf = f1.read()
    with open("basic_nf/docker.config") as f2:
        docker_config = f2.read()
    with open("basic_nf/sample.fa") as f3:
        sample_fa = f3.read()
    r = client.submit.submitWorkflow(body={"workflow": "basic.nf",
                                           "wf_params": {
                                               "in": "sample.fa"
                                           },
                                           "nf_params": {
                                           },
                                           "file_inputs": {
                                               "docker.config": docker_config,
                                               "sample.fa": sample_fa,
                                               "basic.nf": wf
                                           }}).response()
    assert r.metadata.status_code == http.HTTPStatus.ACCEPTED
    workflow_id = r.result.get("workflow_id")
    r = client.status.checkWorkflowStatus(workflow_id=workflow_id).response()
    assert r.result.get("status") == "RUNNING"
    sleep(10)
    r = client.status.checkWorkflowStatus(workflow_id=workflow_id).response()
    assert r.result.get("status") == "COMPLETED"


# def test_submit_non_existent(client):
#     assert client.submit.submitWorkflow(body={"workflow": "hell"}).response().metadata.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY


def test_submit_unauthenticated(unauthenticated_client):
    with pytest.raises(bravado.exception.HTTPUnauthorized):
        assert unauthenticated_client.ping.pingNextflowServer().response().metadata.status_code == http.HTTPStatus.UNAUTHORIZED
        assert unauthenticated_client.submit.submitWorkflow(
            body={"workflow": "hello"}).response().metadata.status_code == http.HTTPStatus.UNAUTHORIZED
