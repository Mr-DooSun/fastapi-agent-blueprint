import traceback

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src._core.application.dtos.base_response import ErrorResponse
from src._core.config import settings
from src._core.exceptions.base_exception import BaseCustomException


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except BaseCustomException as exc:
            content = jsonable_encoder(
                ErrorResponse(
                    message=f"Custom Exception: {exc.message}",
                    error_code=getattr(exc, "code", "CUSTOM_ERROR"),
                    error_details=getattr(exc, "details", None),
                )
            )
            return JSONResponse(status_code=exc.status_code, content=content)
        except Exception:
            # ============ [ DEBUG ] ============
            error_trace = traceback.format_exc()
            print(error_trace)
            # ===================================
            error_details = {"trace": error_trace} if settings.is_dev else None

            content = jsonable_encoder(
                ErrorResponse(
                    message="Internal server error",
                    error_code="INTERNAL_SERVER_ERROR",
                    error_details=error_details,
                )
            )
            return JSONResponse(
                status_code=500,
                content=content,
            )
