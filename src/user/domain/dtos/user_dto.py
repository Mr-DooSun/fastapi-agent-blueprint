from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

UserRole = Literal["user", "admin"]
USER_ROLE_USER: UserRole = "user"
USER_ROLE_ADMIN: UserRole = "admin"


class UserDTO(BaseModel):
    id: int = Field(..., description="User unique identifier")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    role: UserRole = Field(default=USER_ROLE_USER, description="User role")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")
