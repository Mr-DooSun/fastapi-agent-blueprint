from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol
from src.user.domain.dtos.user_dto import CreateUserDTO, UpdateUserDTO, UserDTO


class UserRepositoryProtocol(
    BaseRepositoryProtocol[CreateUserDTO, UserDTO, UpdateUserDTO]
):
    pass
