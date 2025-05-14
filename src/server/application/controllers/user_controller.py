# -*- coding: utf-8 -*-


from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.application.dtos.user_dto import CoreCreateUserDto, CoreUpdateUserDto
from src.core.application.responses.base_response import BaseResponse
from src.server.application.use_cases.user_use_case import UserUseCase
from src.server.infrastructure.di.server_container import ServerContainer

router = APIRouter()


@router.post(
    "/user",
    summary="유저 생성",
    tags=["유저"],
    response_model=BaseResponse,
    response_model_exclude_none=True,
)
@inject
async def create_user(
    create_data: CoreCreateUserDto,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse:
    data = await user_use_case.create_data(create_data=create_data)
    return BaseResponse(data=data)


@router.post(
    "/users",
    summary="유저 생성 (복수)",
    tags=["유저"],
    response_model=BaseResponse,
    response_model_exclude_none=True,
)
@inject
async def create_users(
    create_datas: List[CoreCreateUserDto],
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse:
    data = await user_use_case.create_datas(create_datas=create_datas)
    return BaseResponse(data=data)


@router.get(
    "/users",
    summary="유저 정보 모두 조회",
    tags=["유저"],
    response_model=BaseResponse,
    response_model_exclude_none=True,
)
@inject
async def get_users(
    page: int = 1,
    page_size: int = 10,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse:
    data, pagination = await user_use_case.get_datas(page=page, page_size=page_size)
    return BaseResponse(data=data, pagination=pagination)


@router.get(
    "/user/{user_id}",
    summary="유저 정보 조회",
    tags=["유저"],
    response_model=BaseResponse,
    response_model_exclude_none=True,
)
@inject
async def get_user_by_user_id(
    user_id: int,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse:
    data = await user_use_case.get_data_by_data_id(data_id=user_id)
    return BaseResponse(data=data)


@router.put(
    "/user/{user_id}",
    summary="유저 수정",
    tags=["유저"],
    response_model=BaseResponse,
    response_model_exclude_none=True,
)
@inject
async def update_user_by_user_id(
    user_id: int,
    update_data: CoreUpdateUserDto,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse:
    data = await user_use_case.update_data_by_data_id(
        data_id=user_id, update_data=update_data
    )
    return BaseResponse(data=data)


@router.delete(
    "/user/{user_id}",
    summary="유저 삭제",
    tags=["유저"],
    response_model=BaseResponse,
    response_model_exclude_none=True,
)
@inject
async def delete_user_by_user_id(
    user_id: int,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> BaseResponse:
    await user_use_case.delete_data_by_data_id(data_id=user_id)
    return BaseResponse()
