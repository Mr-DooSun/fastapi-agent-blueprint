from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src._core.application.services.health_service import HealthService
from src._core.infrastructure.di.core_container import CoreContainer

router = APIRouter()


@router.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)


@router.get("/health/db")
@inject
async def database_health_check(
    health_service: HealthService = Depends(Provide[CoreContainer.health_service]),
):
    await health_service.check_database()
    return JSONResponse(content={"status": "healthy"}, status_code=200)
