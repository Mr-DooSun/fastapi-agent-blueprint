# -*- coding: utf-8 -*-
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.exceptions.base_exception import BaseCustomException


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except BaseCustomException as exc:
            return JSONResponse(
                status_code=exc.status_code, content={"message": exc.message}
            )
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={"message": f"Internal server error: {str(exc)}"},
            )
