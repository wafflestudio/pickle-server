from logging import getLogger
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from ninja import Schema
from ninja.errors import AuthenticationError
from ninja.errors import ValidationError as NinjaValidationError
from ninja.responses import codes_2xx, codes_4xx

from seeya_server.utils import camel_to_snake

logger = getLogger(__name__)


class SeeyaApiError(Exception):
    __match_args__ = ("detail", "status_code")
    detail: str
    status_code: int

    def __init__(self, detail: Optional[str] = None, status_code: Optional[int] = None):
        self.detail = detail or "Internal Server Error"
        self.status_code = status_code or 500

    def __str__(self):
        return self.detail


class ErrorResponseSchema(Schema):
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


def api_exception_response(request, exc: Exception):
    status_code: int = 500
    error_msg: str = str(exc)
    error_type: str = camel_to_snake(exc.__class__.__name__)

    match exc:
        case SeeyaApiError(detail, code):
            status_code = code
        case DjangoValidationError():
            status_code = 400
            error_msg = exc.message
        case IntegrityError():
            status_code = 409  # Conflict
            error_msg = exc.__cause__.args[0].split(" ")[0]
        case NinjaValidationError():
            status_code = 422
            error_msg = exc.errors[0]["msg"]
        case PermissionDenied():
            status_code = 403
            error_msg = "권한이 없습니다."
        case ObjectDoesNotExist():
            status_code = 404
            error_msg = "요청한 리소스를 찾을 수 없습니다."
        case AuthenticationError():
            status_code = 401
            error_msg = "인증이 필요합니다."
        case _:
            status_code = 500
            error_msg = "알 수 없는 에러가 발생했습니다."
            logger.error(f"Unhandled exception: {str(exc)}")

    response = ErrorResponseSchema(
        success=False,
        error_type=error_type,
        detail=error_msg,
    )

    return response, status_code
