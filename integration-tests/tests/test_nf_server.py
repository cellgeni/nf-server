# nextflow run cellgeni/tracer --samplefile=samples.txt --genome=GRCh38 -c nf.config -profile docker --studyid=4187 -resume
import http

import bravado
import bravado.exception
import pytest


# @pytest.mark.skip(reason="skipping for speed")
def test_ping(client):
    assert client.ping.pingNextflowServer().response().metadata.status_code == http.HTTPStatus.OK


def test_submit_existing(client):
    r = client.submit.submitWorkflow(body={"workflow": "hello"}).response()
    assert r.metadata.status_code == http.HTTPStatus.ACCEPTED
    workflow_id = r.result.get("workflow_id")


# def test_submit_non_existent(client):
#     assert client.submit.submitWorkflow(body={"workflow": "hell"}).response().metadata.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY


def test_submit_unauthenticated(unauthenticated_client):
    with pytest.raises(bravado.exception.HTTPUnauthorized):
        assert unauthenticated_client.ping.pingNextflowServer().response().metadata.status_code == http.HTTPStatus.UNAUTHORIZED
        assert unauthenticated_client.submit.submitWorkflow(body={"workflow": "hello"}).response().metadata.status_code == http.HTTPStatus.UNAUTHORIZED
