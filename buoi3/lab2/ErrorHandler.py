from venv import logger

from flask import jsonify, request
from werkzeug.exceptions import HTTPException


class ProblemError(Exception):
    """Application error returned using the Problem Details format."""

    def __init__(self, title, detail, status):
        super().__init__(detail)
        self.title = title
        self.detail = detail
        self.status = status


def register_error_handler(app):
    @app.errorhandler(ProblemError)
    def handle_problem_error(error):
        response = jsonify({
            "type": request.path,
            "title": error.title,
            "status": error.status,
            "detail": error.detail,
        })
        response.status_code = error.status
        response.content_type = "application/problem+json"
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = jsonify({
            "type": request.path,
            "title": error.name,
            "status": error.code,
            "detail": error.description,
        })
        response.status_code = error.code
        response.content_type = "application/problem+json"
        return response
    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        logger.exception(
            "Unhandled exception while processing %s %s",
            request.method,
            request.path,
        )

        response = jsonify({
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred.",
            "instance": request.path,
        })
        response.status_code = 500
        response.content_type = "application/problem+json"
        return response