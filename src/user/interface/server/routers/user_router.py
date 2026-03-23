from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src._core.application.dtos.base_response import SuccessResponse
from src.user.domain.services.user_service import UserService
from src.user.infrastructure.di.user_container import UserContainer
from src.user.interface.server.dtos.user_dto import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter()


# ==========================================================================================


@router.post(
    "/user",
    summary="유저 생성",
    response_model=SuccessResponse[UserResponse],
    response_model_exclude={"pagination"},
)
@inject
async def create_user(
    item: CreateUserRequest,
    user_service: UserService = Depends(Provide[UserContainer.user_service]),
) -> SuccessResponse[UserResponse]:
    data = await user_service.create_data(entity=item)
    return SuccessResponse(data=UserResponse(**data.model_dump(exclude={"password"})))


# ==========================================================================================


@router.post(
    "/users",
    summary="유저 생성 (복수)",
    response_model=SuccessResponse[list[UserResponse]],
    response_model_exclude={"pagination"},
)
@inject
async def create_users(
    items: list[CreateUserRequest],
    user_service: UserService = Depends(Provide[UserContainer.user_service]),
) -> SuccessResponse[list[UserResponse]]:
    datas = await user_service.create_datas(entities=items)
    return SuccessResponse(
        data=[UserResponse(**data.model_dump(exclude={"password"})) for data in datas]
    )


# ==========================================================================================


@router.get(
    "/users",
    summary="유저 정보 모두 조회",
    response_model=SuccessResponse[list[UserResponse]],
)
@inject
async def get_user(
    page: int = 1,
    page_size: int = Query(10, alias="pageSize"),
    user_service: UserService = Depends(Provide[UserContainer.user_service]),
) -> SuccessResponse[list[UserResponse]]:
    datas, pagination = await user_service.get_datas(page=page, page_size=page_size)
    return SuccessResponse(
        data=[UserResponse(**data.model_dump(exclude={"password"})) for data in datas],
        pagination=pagination,
    )


# ==========================================================================================


@router.get(
    "/user/by-ids",
    summary="ID 리스트로 유저 여러 명 조회",
    response_model=SuccessResponse[list[UserResponse]],
    response_model_exclude={"pagination"},
)
@inject
async def get_user_by_ids(
    ids: list[int] = Query(..., description="쉼표로 구분된 ID 리스트 (예: 0,1,2)"),
    user_service: UserService = Depends(Provide[UserContainer.user_service]),
) -> SuccessResponse[list[UserResponse]]:
    datas = await user_service.get_datas_by_data_ids(data_ids=ids)
    return SuccessResponse(
        data=[UserResponse(**data.model_dump(exclude={"password"})) for data in datas]
    )


# ==========================================================================================


@router.get(
    "/user/{user_id}",
    summary="유저 정보 조회",
    response_model=SuccessResponse[UserResponse],
    response_model_exclude_none=True,
    response_model_exclude={"pagination"},
)
@inject
async def get_user_by_user_id(
    user_id: int,
    user_service: UserService = Depends(Provide[UserContainer.user_service]),
) -> SuccessResponse[UserResponse]:
    data = await user_service.get_data_by_data_id(data_id=user_id)
    return SuccessResponse(data=UserResponse(**data.model_dump(exclude={"password"})))


# ==========================================================================================


@router.put(
    "/user/{user_id}",
    summary="유저 수정",
    response_model=SuccessResponse[UserResponse],
    response_model_exclude={"pagination"},
)
@inject
async def update_user_by_user_id(
    user_id: int,
    item: UpdateUserRequest,
    user_service: UserService = Depends(Provide[UserContainer.user_service]),
) -> SuccessResponse[UserResponse]:
    data = await user_service.update_data_by_data_id(data_id=user_id, entity=item)
    return SuccessResponse(data=UserResponse(**data.model_dump(exclude={"password"})))


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
    user_service: UserService = Depends(Provide[UserContainer.user_service]),
) -> SuccessResponse:
    success = await user_service.delete_data_by_data_id(data_id=user_id)
    return SuccessResponse(success=success)
