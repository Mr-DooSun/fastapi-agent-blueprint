from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from src._core.application.dtos.base_response import SuccessResponse
from examples.todo.domain.services.todo_service import TodoService
from examples.todo.infrastructure.di.todo_container import TodoContainer
from examples.todo.interface.server.schemas.todo_schema import CreateTodoRequest, UpdateTodoRequest, TodoResponse

router = APIRouter()

@router.post("/todo", summary="Create todo", response_model=SuccessResponse[TodoResponse], response_model_exclude={"pagination"})
@inject
async def create_todo(item: CreateTodoRequest, todo_service: TodoService = Depends(Provide[TodoContainer.todo_service])) -> SuccessResponse[TodoResponse]:
    data = await todo_service.create_data(entity=item)
    return SuccessResponse(data=TodoResponse(**data.model_dump()))

@router.get("/todos", summary="List todos", response_model=SuccessResponse[list[TodoResponse]], response_model_exclude={"pagination"})
@inject
async def list_todos(todo_service: TodoService = Depends(Provide[TodoContainer.todo_service])) -> SuccessResponse[list[TodoResponse]]:
    data = await todo_service.get_data_list()
    return SuccessResponse(data=[TodoResponse(**d.model_dump()) for d in data])

@router.get("/todo/{id}", summary="Get todo", response_model=SuccessResponse[TodoResponse], response_model_exclude={"pagination"})
@inject
async def get_todo(id: str, todo_service: TodoService = Depends(Provide[TodoContainer.todo_service])) -> SuccessResponse[TodoResponse]:
    data = await todo_service.get_data_by_data_id(data_id=id)
    return SuccessResponse(data=TodoResponse(**data.model_dump()))

@router.put("/todo/{id}", summary="Update todo", response_model=SuccessResponse[TodoResponse], response_model_exclude={"pagination"})
@inject
async def update_todo(id: str, item: UpdateTodoRequest, todo_service: TodoService = Depends(Provide[TodoContainer.todo_service])) -> SuccessResponse[TodoResponse]:
    data = await todo_service.update_data_by_data_id(data_id=id, entity=item)
    return SuccessResponse(data=TodoResponse(**data.model_dump()))

@router.delete("/todo/{id}", summary="Delete todo", response_model=SuccessResponse, response_model_exclude={"data", "pagination"})
@inject
async def delete_todo(id: str, todo_service: TodoService = Depends(Provide[TodoContainer.todo_service])) -> SuccessResponse:
    success = await todo_service.delete_data_by_data_id(data_id=id)
    return SuccessResponse(success=success)
