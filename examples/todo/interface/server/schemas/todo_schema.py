from datetime import datetime
from typing import Optional
from pydantic import Field
from src._core.application.dtos.base_request import BaseRequest
from src._core.application.dtos.base_response import BaseResponse

class TodoResponse(BaseResponse):
    id: str
    title: str
    description: Optional[str] = None
    done: bool
    created_at: datetime
    updated_at: datetime

class CreateTodoRequest(BaseRequest):
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

class UpdateTodoRequest(BaseRequest):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    done: Optional[bool] = None
