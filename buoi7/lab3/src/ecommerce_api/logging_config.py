import json
import logging
import logging.config
import re
import sys
import time
import uuid
from datetime import datetime, timezone

from flask import g, has_request_context, request


class JsonFormatter(logging.Formatter):
    """Emit one compact JSON object per log record."""

    STRUCTURED_FIELDS = (
        "event",
        "method",
        "route",
        "status",
        "latency_ms",
        "exception_type",
    )

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created, timezone.utc)
        payload = {
            "ts": timestamp.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "msg": record.getMessage(),
        }

        request_id = getattr(record, "request_id", None)
        if request_id is None and has_request_context():
            request_id = getattr(g, "request_id", None)
        if request_id:
            payload["rid"] = request_id

        for field in self.STRUCTURED_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _effective_level(app):
    configured = str(app.config.get("LOG_LEVEL", "INFO")).upper()
    level = logging.getLevelNamesMapping().get(configured, logging.INFO)
    if level == logging.DEBUG and not (app.debug or app.testing):
        return logging.INFO
    return level


def configure(app):
    level = _effective_level(app)
    app.config["LOG_LEVEL"] = logging.getLevelName(level)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "json",
                }
            },
            "root": {"level": level, "handlers": ["stdout"]},
        }
    )

    logger = app.logger
    logger.handlers.clear()
    logger.setLevel(level)
    logger.propagate = True

    @app.before_request
    def _start_request_log():
        candidate = request.headers.get("X-Request-Id", "").strip()
        if not re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", candidate):
            candidate = uuid.uuid4().hex
        g.request_id = candidate
        g.request_started_at = time.perf_counter()

    @app.after_request
    def _finish_request_log(response):
        request_id = getattr(g, "request_id", uuid.uuid4().hex)
        started_at = getattr(g, "request_started_at", time.perf_counter())
        response.headers["X-Request-Id"] = request_id
        app.logger.info(
            "http_request",
            extra={
                "event": "http.request.complete",
                "request_id": request_id,
                "method": request.method,
                "route": request.endpoint or "unmatched",
                "status": response.status_code,
                "latency_ms": int((time.perf_counter() - started_at) * 1000),
            },
        )
        return response
