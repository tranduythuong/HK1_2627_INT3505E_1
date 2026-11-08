import json

from flask import jsonify
from werkzeug.exceptions import HTTPException

from ecommerce_api.exceptions.AppException import ApiError


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
        if not isinstance(message, str):
            message = json.dumps(message, ensure_ascii=False)

        return jsonify({"code": code, "message": message}), status

    @app.errorhandler(Exception)
    def handle_unexpected_error(_error):
        app.logger.exception("Unhandled application error")
        return jsonify({"code": "internal_error"}), 500
