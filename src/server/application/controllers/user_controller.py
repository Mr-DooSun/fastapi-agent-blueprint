# -*- coding: utf-8 -*-


from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.applications.dtos.user_dto import CreateUserDto, UpdateUserDto
from src.core.applications.responses.user_response import UserResponse
from src.server.application.use_cases.user_use_case import UserUseCase
from src.server.infrastructure.di.server_container import ServerContainer

router = APIRouter()


@router.post("/user", summary="유저 생성", tags=["유저"])
@inject
async def create_user(
    create_data: CreateUserDto,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> UserResponse:
    data = await user_use_case.create_data(create_data=create_data)
    return UserResponse(data=data)


@router.post("/users", summary="유저 생성 (복수)", tags=["유저"])
@inject
async def create_users(
    create_datas: List[CreateUserDto],
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> UserResponse:
    data = await user_use_case.create_datas(create_datas=create_datas)
    return UserResponse(data=data)


@router.get("/users", summary="유저 정보 모두 조회", tags=["유저"])
@inject
async def get_users(
    page: int = 1,
    page_size: int = 10,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> UserResponse:
    data = await user_use_case.get_datas(page=page, page_size=page_size)
    return UserResponse(data=data)


@router.get("/user/{user_id}", summary="유저 정보 조회", tags=["유저"])
@inject
async def get_user_by_user_id(
    user_id: int,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> UserResponse:
    data = await user_use_case.get_data_by_data_id(data_id=user_id)
    return UserResponse(data=data)


@router.put("/user/{user_id}", summary="유저 수정", tags=["유저"])
@inject
async def update_user_by_user_id(
    user_id: int,
    update_data: UpdateUserDto,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> UserResponse:
    data = await user_use_case.update_data_by_data_id(
        data_id=user_id, update_data=update_data
    )
    return UserResponse(data=data)


@router.delete("/user/{user_id}", summary="유저 삭제", tags=["유저"])
@inject
async def delete_user_by_user_id(
    user_id: int,
    user_use_case: UserUseCase = Depends(
        Provide[ServerContainer.user_container.user_use_case]
    ),
) -> UserResponse:
    await user_use_case.delete_data_by_data_id(data_id=user_id)
    return UserResponse()
