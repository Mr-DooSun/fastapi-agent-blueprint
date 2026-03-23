from src._core.domain.services.base_service import BaseService
from src.user.domain.dtos.user_dto import UserDTO
from src.user.domain.protocols.user_repository_protocol import UserRepositoryProtocol


class UserService(BaseService[UserDTO]):
    def __init__(self, user_repository: UserRepositoryProtocol) -> None:
        super().__init__(repository=user_repository)
