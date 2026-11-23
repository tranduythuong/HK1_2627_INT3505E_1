"""Header-based API versioning for the users endpoint.

Run with: python app.py
"""

from functools import wraps

from flask import Flask, jsonify, request


LATEST = "2"
SUPPORTED = {"1", "2", "2024-06-20"}
USERS = {1: {"f": "V\u0103n", "l": "Nguy\u1ec5n", "e": "a@vnu.vn"}}

app = Flask(__name__)


def api_version(supported=SUPPORTED, default=LATEST):
    """Read and validate X-API-Version, then mark the served version."""

    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            version = request.headers.get("X-API-Version", default)
            if version not in supported:
                return jsonify(error="unsupported version"), 400

            result = fn(version, *args, **kwargs)
            status = 200
            if isinstance(result, tuple):
                result, status = result

            response = jsonify(result)
            response.status_code = status
            response.headers["X-API-Version-Served"] = version
            return response

        return wrapper

    return decorate


@app.get("/users/<int:uid>")
@api_version()
def get_user(version, uid):
    user = USERS.get(uid)
    if user is None:
        return {"error": "not found"}, 404

    versions = {
        "1": {
            "id": uid,
            "full_name": user["f"] + " " + user["l"],
        },
        "2": {
            "id": uid,
            "first_name": user["f"],
            "last_name": user["l"],
            "email": user["e"],
        },
        "2024-06-20": {
            "id": uid,
            "first_name": user["f"],
            "last_name": user["l"],
            "email": user["e"],
        },
    }
    return versions[version]


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
