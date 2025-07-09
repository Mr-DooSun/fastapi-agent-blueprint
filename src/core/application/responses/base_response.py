# -*- coding: utf-8 -*-
from typing import Generic, Optional, TypeVar

from src.core.application.dtos.base_config import BaseConfig


class PaginationInfo(BaseConfig):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool
    next_page: Optional[int] = None
    previous_page: Optional[int] = None


ReturnType = TypeVar("ReturnType")


class BaseResponse(BaseConfig, Generic[ReturnType]):
    success: bool = True
    message: str = "Request processed successfully"
    data: Optional[ReturnType] = None
    pagination: Optional[PaginationInfo] = None
    exists: Optional[bool] = None
