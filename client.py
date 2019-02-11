import yaml
import os
from bravado.client import SwaggerClient

HOST = os.getenv("CASBIN_HOST", "http://127.0.0.1:5000")

with open(os.path.join(os.path.dirname(__file__), "swagger.yml")) as f:
    spec = yaml.load(f)
    client = SwaggerClient.from_spec(spec)
    client.swagger_spec.api_url = HOST

