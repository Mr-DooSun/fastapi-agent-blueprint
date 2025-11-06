from typing import TypeVar

from src._core.application.dtos.base_config import ApiConfig
from src._core.domain.entities.entity import Entity

EntityType = TypeVar("EntityType", bound=Entity)


class BaseRequest(ApiConfig):
    def to_entity(self, entity_cls: type[EntityType]) -> EntityType:
        return entity_cls(**self.model_dump())
