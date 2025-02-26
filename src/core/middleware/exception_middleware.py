# -*- coding: utf-8 -*-
import traceback

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.applications.responses.base import BaseResponse
from src.core.exceptions.base_exception import BaseCustomException


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except BaseCustomException as exc:
            content = jsonable_encoder(
                BaseResponse(success=False, message=f"Custom Exception: {exc.message}")
            )
            return JSONResponse(status_code=exc.status_code, content=content)
        except Exception as exc:
            # DEBUG
            error_trace = traceback.format_exc()
            print(error_trace)
            content = jsonable_encoder(
                BaseResponse(
                    success=False,
                    message=f"Internal server error: {str(exc)}",
                )
            )
            return JSONResponse(
                status_code=500,
                content=content,
            )
