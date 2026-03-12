from src._core.application.use_cases.base_use_case import BaseUseCase
from src.user.domain.dtos.user_dto import CreateUserDTO, UpdateUserDTO, UserDTO
from src.user.domain.services.user_service import UserService


class UserUseCase(BaseUseCase[CreateUserDTO, UserDTO, UpdateUserDTO]):
    def __init__(self, user_service: UserService) -> None:
        super().__init__(
            base_service=user_service,
            create_entity=CreateUserDTO,
            return_entity=UserDTO,
            update_entity=UpdateUserDTO,
        )

    async def process_user(self, dto: UserDTO) -> UserDTO:
        return dto
