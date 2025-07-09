# -*- coding: utf-8 -*-


from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.application.dtos.base_dto import IdListDto
from src.core.application.dtos.user_dto import (
    CoreCreateUserDto,
    CoreUpdateUserDto,
    CoreUserDto,
)
from src.core.application.responses.base_response import BaseResponse
from src.server.application.use_cases.user_use_case import UserUseCase
from src.server.infrastructure.di.server_container import ServerContainer

router = APIRouter()


@router.post(
    "/user",
    summary="유저 생성",
    tags=["유저"],
    response_model=BaseResponse[CoreUserDto],
    response_model_exclude={"pagination", "exists"},
)
@inject
async def create_user(
    create_data: CoreCreateUserDto,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse[CoreUserDto]:
    data = await user_use_case.create_data(create_data=create_data)
    return BaseResponse(data=data)


# ==========================================================================================


@router.post(
    "/users",
    summary="유저 생성 (복수)",
    tags=["유저"],
    response_model=BaseResponse[List[CoreUserDto]],
    response_model_exclude={"pagination", "exists"},
)
@inject
async def create_users(
    create_datas: List[CoreCreateUserDto],
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse[List[CoreUserDto]]:
    data = await user_use_case.create_datas(create_datas=create_datas)
    return BaseResponse(data=data)


# ==========================================================================================


@router.get(
    "/users",
    summary="유저 정보 모두 조회",
    tags=["유저"],
    response_model=BaseResponse[List[CoreUserDto]],
    response_model_exclude={"exists"},
)
@inject
async def get_users(
    page: int = 1,
    page_size: int = 10,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse[List[CoreUserDto]]:
    data, pagination = await user_use_case.get_datas(page=page, page_size=page_size)
    return BaseResponse(data=data, pagination=pagination)


# ==========================================================================================


@router.get(
    "/user/{user_id}",
    summary="유저 정보 조회",
    tags=["유저"],
    response_model=BaseResponse[CoreUserDto],
    response_model_exclude_none=True,
    response_model_exclude={"pagination", "exists"},
)
@inject
async def get_user_by_user_id(
    user_id: int,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse[CoreUserDto]:
    data = await user_use_case.get_data_by_data_id(data_id=user_id)
    return BaseResponse(data=data)


# ==========================================================================================


@router.post(
    "/users/by-ids",
    summary="ID 리스트로 유저 여러 명 조회",
    tags=["유저"],
    response_model=BaseResponse[List[CoreUserDto]],
    response_model_exclude={"pagination", "exists"},
)
@inject
async def get_users_by_ids(
    payload: IdListDto,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse[List[CoreUserDto]]:
    data = await user_use_case.get_datas_by_data_ids(payload=payload)
    return BaseResponse(data=data)


# ==========================================================================================


@router.put(
    "/user/{user_id}",
    summary="유저 수정",
    tags=["유저"],
    response_model=BaseResponse[CoreUserDto],
    response_model_exclude={"pagination", "exists"},
)
@inject
async def update_user_by_user_id(
    user_id: int,
    update_data: CoreUpdateUserDto,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse[CoreUserDto]:
    data = await user_use_case.update_data_by_data_id(
        data_id=user_id, update_data=update_data
    )
    return BaseResponse(data=data)


# ==========================================================================================


@router.delete(
    "/user/{user_id}",
    summary="유저 삭제",
    tags=["유저"],
    response_model=BaseResponse,
    response_model_exclude={"data", "pagination", "exists"},
)
@inject
async def delete_user_by_user_id(
    user_id: int,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse:
    success = await user_use_case.delete_data_by_data_id(data_id=user_id)
    return BaseResponse(success=success)
