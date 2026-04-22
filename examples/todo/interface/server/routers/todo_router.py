from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from examples.todo.domain.services.todo_service import TodoService
from examples.todo.infrastructure.di.todo_container import TodoContainer
from examples.todo.interface.server.schemas.todo_schema import (
    CreateTodoRequest,
    TodoResponse,
    UpdateTodoRequest,
)
from src._core.application.dtos.base_response import SuccessResponse

router = APIRouter()


@router.post(
    "/todo",
    summary="Create todo",
    response_model=SuccessResponse[TodoResponse],
    response_model_exclude={"pagination"},
)
@inject
async def create_todo(
    item: CreateTodoRequest,
    todo_service: TodoService = Depends(Provide[TodoContainer.todo_service]),
) -> SuccessResponse[TodoResponse]:
    data = await todo_service.create_data(entity=item)
    return SuccessResponse(data=TodoResponse(**data.model_dump()))


@router.get(
    "/todos",
    summary="List todos",
    response_model=SuccessResponse[list[TodoResponse]],
    response_model_exclude={"pagination"},
)
@inject
async def list_todos(
    todo_service: TodoService = Depends(Provide[TodoContainer.todo_service]),
) -> SuccessResponse[list[TodoResponse]]:
    datas, pagination = await todo_service.get_data(page=1, page_size=100)
    return SuccessResponse(data=[TodoResponse(**d.model_dump()) for d in datas])


@router.get(
    "/todo/{id}",
    summary="Get todo",
    response_model=SuccessResponse[TodoResponse],
    response_model_exclude={"pagination"},
)
@inject
async def get_todo(
    id: int, todo_service: TodoService = Depends(Provide[TodoContainer.todo_service])
) -> SuccessResponse[TodoResponse]:
    data = await todo_service.get_data_by_data_id(data_id=id)
    return SuccessResponse(data=TodoResponse(**data.model_dump()))


@router.put(
    "/todo/{id}",
    summary="Update todo",
    response_model=SuccessResponse[TodoResponse],
    response_model_exclude={"pagination"},
)
@inject
async def update_todo(
    id: int,
    item: UpdateTodoRequest,
    todo_service: TodoService = Depends(Provide[TodoContainer.todo_service]),
) -> SuccessResponse[TodoResponse]:
    data = await todo_service.update_data_by_data_id(data_id=id, entity=item)
    return SuccessResponse(data=TodoResponse(**data.model_dump()))


@router.delete(
    "/todo/{id}",
    summary="Delete todo",
    response_model=SuccessResponse,
    response_model_exclude={"data", "pagination"},
)
@inject
async def delete_todo(
    id: int, todo_service: TodoService = Depends(Provide[TodoContainer.todo_service])
) -> SuccessResponse:
    success = await todo_service.delete_data_by_data_id(data_id=id)
    return SuccessResponse(success=success)
