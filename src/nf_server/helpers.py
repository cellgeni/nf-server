import http
from functools import wraps

from flask import request, jsonify

from nf_server import app


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get("X-API-Key") != app.auth_token:
            return jsonify(message="Auth token missing from the request"), http.HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)

    return decorated_function