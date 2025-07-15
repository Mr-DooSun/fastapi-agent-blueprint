# -*- coding: utf-8 -*-


from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.core.application.dtos.common.base_request import IdListDto
from src.core.application.dtos.common.base_response import SuccessResponse
from src.core.application.dtos.user.users_dto import (
    CoreCreateUsersRequest,
    CoreUpdateUsersRequest,
    CoreUsersResponse,
)
from src.core.common.dto_utils import dtos_to_entities, entities_to_dtos
from src.core.domain.entities.user.users_entity import (
    CoreCreateUsersEntity,
    CoreUpdateUsersEntity,
)
from src.server.application.use_cases.user.users_use_case import UsersUseCase
from src.server.infrastructure.di.server_container import ServerContainer

router = APIRouter()


# ==========================================================================================


@router.post(
    "/user",
    summary="유저 생성",
    response_model=SuccessResponse[CoreUsersResponse],
    response_model_exclude={"pagination"},
)
@inject
async def create_user(
    create_data: CoreCreateUsersRequest,
    user_use_case: UsersUseCase = Depends(
        Provide[ServerContainer.user_container.users_use_case]
    ),
) -> SuccessResponse[CoreUsersResponse]:
    data = await user_use_case.create_data(
        create_data=create_data.to_entity(CoreCreateUsersEntity)
    )
    return SuccessResponse(data=CoreUsersResponse.from_entity(data))


# ==========================================================================================


@router.post(
    "/users",
    summary="유저 생성 (복수)",
    response_model=SuccessResponse[List[CoreUsersResponse]],
    response_model_exclude={"pagination"},
)
@inject
async def create_users(
    create_datas: List[CoreCreateUsersRequest],
    user_use_case: UsersUseCase = Depends(
        Provide[ServerContainer.user_container.users_use_case]
    ),
) -> SuccessResponse[List[CoreUsersResponse]]:
    entities = dtos_to_entities(create_datas, CoreCreateUsersEntity)
    datas = await user_use_case.create_datas(create_datas=entities)
    return SuccessResponse(data=entities_to_dtos(datas, CoreUsersResponse))


# ==========================================================================================


@router.get(
    "/users",
    summary="유저 정보 모두 조회",
    response_model=SuccessResponse[List[CoreUsersResponse]],
)
@inject
async def get_users(
    page: int = 1,
    page_size: int = Query(10, alias="pageSize"),
    user_use_case: UsersUseCase = Depends(
        Provide[ServerContainer.user_container.users_use_case]
    ),
) -> SuccessResponse[List[CoreUsersResponse]]:
    datas, pagination = await user_use_case.get_datas(page=page, page_size=page_size)
    return SuccessResponse(
        data=entities_to_dtos(datas, CoreUsersResponse), pagination=pagination
    )


# ==========================================================================================


@router.get(
    "/user/{user_id}",
    summary="유저 정보 조회",
    response_model=SuccessResponse[CoreUsersResponse],
    response_model_exclude_none=True,
    response_model_exclude={"pagination"},
)
@inject
async def get_user_by_user_id(
    user_id: int,
    user_use_case: UsersUseCase = Depends(
        Provide[ServerContainer.user_container.users_use_case]
    ),
) -> SuccessResponse[CoreUsersResponse]:
    data = await user_use_case.get_data_by_data_id(data_id=user_id)
    return SuccessResponse(data=CoreUsersResponse.from_entity(data))


# ==========================================================================================


@router.post(
    "/users/by-ids",
    summary="ID 리스트로 유저 여러 명 조회",
    response_model=SuccessResponse[List[CoreUsersResponse]],
    response_model_exclude={"pagination"},
)
@inject
async def get_users_by_ids(
    payload: IdListDto,
    user_use_case: UsersUseCase = Depends(
        Provide[ServerContainer.user_container.users_use_case]
    ),
) -> SuccessResponse[List[CoreUsersResponse]]:
    datas = await user_use_case.get_datas_by_data_ids(payload=payload)
    return SuccessResponse(data=entities_to_dtos(datas, CoreUsersResponse))


# ==========================================================================================


@router.put(
    "/user/{user_id}",
    summary="유저 수정",
    response_model=SuccessResponse[CoreUsersResponse],
    response_model_exclude={"pagination"},
)
@inject
async def update_user_by_user_id(
    user_id: int,
    update_data: CoreUpdateUsersRequest,
    user_use_case: UsersUseCase = Depends(
        Provide[ServerContainer.user_container.users_use_case]
    ),
) -> SuccessResponse[CoreUsersResponse]:
    data = await user_use_case.update_data_by_data_id(
        data_id=user_id, update_data=update_data.to_entity(CoreUpdateUsersEntity)
    )
    return SuccessResponse(data=CoreUsersResponse.from_entity(data))


# ==========================================================================================


@router.delete(
    "/user/{user_id}",
    summary="유저 삭제",
    response_model=SuccessResponse,
    response_model_exclude={"data", "pagination"},
)
@inject
async def delete_user_by_user_id(
    user_id: int,
    users_use_case: UsersUseCase = Depends(
        Provide[ServerContainer.user_container.users_use_case]
    ),
) -> SuccessResponse:
    success = await users_use_case.delete_data_by_data_id(data_id=user_id)
    return SuccessResponse(success=success)
