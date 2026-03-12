from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol
from src._core.domain.services.base_service import BaseService
from src.user.domain.dtos.user_dto import CreateUserDTO, UpdateUserDTO, UserDTO


class UserService(BaseService[CreateUserDTO, UserDTO, UpdateUserDTO]):
    def __init__(
        self,
        user_repository: BaseRepositoryProtocol[CreateUserDTO, UserDTO, UpdateUserDTO],
    ) -> None:
        super().__init__(
            base_repository=user_repository,
            create_entity=CreateUserDTO,
            return_entity=UserDTO,
            update_entity=UpdateUserDTO,
        )
