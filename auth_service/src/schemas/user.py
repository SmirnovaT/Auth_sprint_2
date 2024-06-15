from uuid import UUID

from src.schemas.model_config import BaseOrjsonModel


class UserCreate(BaseOrjsonModel):
    login: str
    email: str
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseOrjsonModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserInDBWRole(BaseOrjsonModel):
    id: UUID
    first_name: str
    last_name: str
    role_id: UUID


class Login(BaseOrjsonModel):
    user_login: str
    password: str


class PasswordChange(BaseOrjsonModel):
    new_login: str | None = None
    new_password: str | None = None
