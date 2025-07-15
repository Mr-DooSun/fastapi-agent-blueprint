# -*- coding: utf-8 -*-
from typing import List, Type, TypeVar

from src.core.application.dtos.common.base_config import ApiConfig
from src.core.domain.entities.entity import Entity

EntityType = TypeVar("EntityType", bound=Entity)


class BaseRequest(ApiConfig):
    def to_entity(self, entity_cls: Type[EntityType]) -> EntityType:
        return entity_cls(**self.model_dump())


class IdListDto(BaseRequest):
    ids: List[int]
