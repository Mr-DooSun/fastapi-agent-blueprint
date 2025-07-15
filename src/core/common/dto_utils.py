# -*- coding: utf-8 -*-
from typing import List, Type, TypeVar

from src.core.application.dtos.common.base_request import BaseRequest
from src.core.application.dtos.common.base_response import BaseResponse
from src.core.domain.entities.entity import Entity

EntityType = TypeVar("EntityType", bound=Entity)
RequestDtoType = TypeVar("RequestDtoType", bound=BaseRequest)
ResponseDtoType = TypeVar("ResponseDtoType", bound=BaseResponse)


def dtos_to_entities(
    dtos: List[RequestDtoType], entity_cls: Type[EntityType]
) -> List[EntityType]:
    return [dto.to_entity(entity_cls) for dto in dtos]


def entities_to_dtos(
    entities: List[EntityType], dto_cls: Type[ResponseDtoType]
) -> List[ResponseDtoType]:
    return [dto_cls.from_entity(entity) for entity in entities]
