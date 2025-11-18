from fastapi import FastAPI

from src._apps.server.bootstrap import bootstrap_app
from src._core.application.dtos.base_response import ErrorResponse
from src._core.config import settings


def create_app():
    app = FastAPI(
        title="FastAPI Layered Architecture (Monolith)",
        description="DDD 기반 모놀리식 아키텍처 - 각 도메인이 독립적으로 구성됨",
        version="1.0.0",
        root_path="/api",
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        responses={
            400: {"model": ErrorResponse, "description": "잘못된 요청"},
            401: {"model": ErrorResponse, "description": "인증 필요 또는 토큰 불일치"},
            403: {"model": ErrorResponse, "description": "권한 없음"},
            404: {"model": ErrorResponse, "description": "해당 리소스 없음"},
            500: {"model": ErrorResponse, "description": "서버 오류"},
        },
    )

    bootstrap_app(app)

    return app


app = create_app()
