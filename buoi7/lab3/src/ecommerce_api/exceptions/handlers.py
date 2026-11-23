from flask import jsonify
from werkzeug.exceptions import HTTPException

from ecommerce_api.exceptions.AppException import ApiError


def _format_message(detail):
    """Convert Flask-Smorest/Webargs validation details to readable text."""
    if isinstance(detail, str):
        return detail
    if isinstance(detail, (list, tuple)):
        return "; ".join(filter(None, (_format_message(item) for item in detail)))
    if isinstance(detail, dict):
        parts = []
        for key, value in detail.items():
            message = _format_message(value)
            if not message:
                continue
            parts.append(message if key == "json" else f"{key}: {message}")
        return "; ".join(parts)
    return str(detail)


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify({"code": error.code, "message": error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        status = error.code or 500
        code = (error.name or "internal_server_error").lower().replace(" ", "_")
        if status == 422:
            code = "validation_error"

        message = error.description
        error_data = getattr(error, "data", {})
        if isinstance(error_data, dict):
            message = error_data.get("message") or error_data.get("messages") or message
        message = _format_message(message)

        return jsonify({"code": code, "message": message}), status

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(
            "request.unhandled_exception",
            extra={"event": "request.unhandled_exception", "exception_type": type(error).__name__},
        )
        return jsonify({"code": "internal_error"}), 500
