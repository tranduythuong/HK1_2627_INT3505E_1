class ApiError(Exception):
    """Base class for expected business and API errors."""

    status_code = 500
    code = "internal_error"

    def __init__(self, code=None, message="", status=None):
        super().__init__(message)
        self.code = code or type(self).code
        self.status_code = status or type(self).status_code
        self.message = message


class NotFound(ApiError):
    status_code = 404
    code = "not_found"


class Conflict(ApiError):
    status_code = 409
    code = "conflict"


class OutOfStock(Conflict):
    code = "out_of_stock"


class InvalidInput(ApiError):
    status_code = 422
    code = "validation_error"
