# -*- coding: utf-8 -*-
from abc import ABC
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from src.core.applications.responses.pagination_response import PaginationResponse

dto_model_config = ConfigDict(
    extra="ignore",
    frozen=True,
    populate_by_name=True,
    loc_by_alias=True,
    alias_generator=to_camel,
    ser_json_timedelta="iso8601",
    ser_json_bytes="utf8",
)


class BaseResponse(ABC, BaseModel):
    success: bool = True
    message: str = "Request processed successfully"
    data: Optional[Any] = None
    pagination: Optional[PaginationResponse] = None

    model_config = dto_model_config
