import re
from ninja.errors import AuthenticationError
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from ninja.errors import ValidationError as NinjaValidationError

from typing import Optional

from ninja import Schema
from ninja.responses import codes_2xx, codes_4xx


class APIError(Exception):
    status_code = 500
    detail = "Internal Server Error"

    def __init__(self, detail=None, status_code=None):
        if detail:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code

    def __str__(self):
        return self.detail


class ResponseDTO(Schema):
    success: bool
    error_type: Optional[str] = None
    detail: Optional[str] = ""

    @classmethod
    def from_status_code(cls, status_code: int, detail: Optional[str] = ""):
        if status_code in codes_2xx:
            return cls(success=True, detail=detail)
        elif status_code in codes_4xx:
            return cls(success=False, detail=detail)
        else:
            raise NotImplementedError


def camel_to_snake(name):
    p = re.compile(r"(?<!^)(?=[A-Z])")
    return p.sub("_", name).lower()


def api_exception_response(request, exc):
    status_code = 500
    error_msg = str(exc)
    error_type = camel_to_snake(exc.__class__.__name__)
    if isinstance(exc, APIError):
        status_code = exc.status_code
    elif isinstance(exc, DjangoValidationError):
        status_code = 400
        error_msg = exc.message
    elif isinstance(exc, NinjaValidationError):
        status_code = 422
        error_msg = exc.errors[0]["msg"]
    elif isinstance(exc, PermissionDenied):
        status_code = 403
    elif isinstance(exc, ObjectDoesNotExist):
        status_code = 404
    elif isinstance(exc, AuthenticationError):
        status_code = 401

    response = ResponseDTO(
        success=False,
        error_type=error_type,
        detail=error_msg,
    )

    return response, status_code
