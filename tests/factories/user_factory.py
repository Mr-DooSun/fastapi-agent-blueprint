from datetime import datetime

from src.user.domain.dtos.user_dto import CreateUserDTO, UpdateUserDTO, UserDTO


def make_user_dto(
    id: int = 1,
    username: str = "testuser",
    full_name: str = "Test User",
    email: str = "test@example.com",
    password: str = "hashed_password",
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> UserDTO:
    now = datetime.now()
    return UserDTO(
        id=id,
        username=username,
        full_name=full_name,
        email=email,
        password=password,
        created_at=created_at or now,
        updated_at=updated_at or now,
    )


def make_create_user_dto(
    username: str = "testuser",
    full_name: str = "Test User",
    email: str = "test@example.com",
    password: str = "hashed_password",
) -> CreateUserDTO:
    return CreateUserDTO(
        username=username,
        full_name=full_name,
        email=email,
        password=password,
    )


def make_update_user_dto(
    username: str | None = None,
    full_name: str | None = None,
    email: str | None = None,
    password: str | None = None,
) -> UpdateUserDTO:
    return UpdateUserDTO(
        username=username,
        full_name=full_name,
        email=email,
        password=password,
    )
