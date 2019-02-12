import os

import urllib
import urllib.parse
import pytest
import yaml
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient

HOST = os.getenv("NF_SERVER_HOST", "http://127.0.0.1:5000")
HOSTNAME = urllib.parse.urlsplit(HOST).hostname
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "nfauthtoken")


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
