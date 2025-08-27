# -*- coding: utf-8 -*-
import traceback

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.application.dtos.base_response import ErrorResponse
from src.core.exceptions.base_exception import BaseCustomException


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
            content = jsonable_encoder(
                ErrorResponse(
                    message="Internal server error",
                    error_code="INTERNAL_SERVER_ERROR",
                    error_details={"trace": error_trace},
                )
            )
            return JSONResponse(
                status_code=500,
                content=content,
            )
