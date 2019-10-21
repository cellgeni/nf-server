import os
import urllib.parse

import pytest
import yaml
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient

HOST = os.getenv("NF_SERVER_HOST", "http://127.0.0.1:5000")
HOSTNAME = urllib.parse.urlsplit(HOST).hostname
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "nfauthtoken")
TEST_FILES_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "basic_nf")


def get_test_file(filename):
    return os.path.join(TEST_FILES_ROOT, f"{filename}")


def get_client(auth_token=AUTH_TOKEN):
    with open(os.getenv("SWAGGER_SCHEMA", "swagger.yml")) as f:
        spec = yaml.load(f)

    http_client = RequestsClient()
    http_client.set_api_key(
        HOSTNAME, auth_token,
        param_name='X-API-Key', param_in='header'
    )
    _client = SwaggerClient.from_spec(spec, http_client=http_client)
    _client.swagger_spec.api_url = HOST
    return _client


@pytest.fixture(scope='module')
def client():
    return get_client()


@pytest.fixture(scope='module')
def unauthenticated_client():
    return get_client(auth_token='')


def get_basic_nf(failing=False):
    with open(get_test_file("basic.nf")) as f1:
        wf = f1.read()
    with open(get_test_file("docker.config")) as f2:
        docker_config = f2.read()
    with open(get_test_file("sample.fa")) as f3:
        sample_fa = f3.read()
    return {"workflow": "basic.nf",
            "wf_params": {
                "in": "sample.fa"
            },
            "nf_params": {
            },
            "file_inputs": {
                "docker.config": docker_config,
                "sample.fa": sample_fa,
                "basic.nf": wf if not failing else wf.replace("input.fa", "input.fa && exit 1")
            }}


@pytest.fixture(scope='function')
def basic_nf():
    return get_basic_nf()


@pytest.fixture(scope='function')
def basic_nf_failing():
    return get_basic_nf(failing=True)
