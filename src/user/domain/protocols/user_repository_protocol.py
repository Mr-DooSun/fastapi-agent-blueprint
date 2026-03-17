from pydantic import BaseModel

from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol
from src.user.domain.dtos.user_dto import UserDTO


class UserRepositoryProtocol(BaseRepositoryProtocol[BaseModel, UserDTO, BaseModel]):
    pass
