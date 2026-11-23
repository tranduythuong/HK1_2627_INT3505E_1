"""Sunset middleware example for a deprecated API endpoint.

Run with: python app.py
The default sunset is 2026-12-31 23:59:59 UTC. Set V1_SUNSET to an ISO
8601 timestamp to exercise the 410 response before that date.
"""

import logging
import os
from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps

from flask import Flask, jsonify, request


log = logging.getLogger("sunset")


def http_date(dt):
    """Format an aware datetime as an HTTP date in GMT."""
    return format_datetime(dt.astimezone(timezone.utc), usegmt=True)


def deprecate_at(sunset_date, replacement=None):
    def decorate(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            now = datetime.now(timezone.utc)
            sunset_header = http_date(sunset_date)

            if now >= sunset_date:
                return jsonify({
                    "error": "gone",
                    "sunset": sunset_header,
                    "use_instead": replacement,
                }), 410

            result = fn(*args, **kwargs)
            body, status = result if isinstance(result, tuple) else (result, 200)
            response = jsonify(body)
            response.status_code = status
            response.headers["Sunset"] = sunset_header
            response.headers["Deprecation"] = "true"
            if replacement:
                response.headers["Link"] = (
                    f"<{replacement}>; rel=\"successor-version\""
                )

            log.warning("deprecated_call %s %s", request.path, request.remote_addr)
            return response

        return inner

    return decorate


app = Flask(__name__)
V1_SUNSET = datetime.fromisoformat(
    os.environ.get("V1_SUNSET", "2026-12-31T23:59:59+00:00")
)
if V1_SUNSET.tzinfo is None:
    V1_SUNSET = V1_SUNSET.replace(tzinfo=timezone.utc)


@app.route("/api/v1/users/<int:uid>")
@deprecate_at(V1_SUNSET, replacement="/api/v2/users")
def get_v1(uid):
    return {"id": uid, "full_name": "Nguy\u1ec5n V\u0103n A"}


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
