from http import HTTPStatus
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.db import models
from src.db.models import Role, User
from src.repositories.base import BaseRepository
from src.schemas.user import UserInDB, UserInDBWRole


class UserRepository(BaseRepository):
    """Репозиторий для взаимодействия с моделью User"""

    model = models.User

    async def create_user(self, user: User) -> UserInDB:
        """Создание пользователя"""

        return await self.create(user)

    async def update_user_role(self, login: str, role_id: str) -> UserInDBWRole:
        """Изменение роли пользователя"""

        user_to_update = await self.db.scalar(
            select(User).where(self.model.login == login)
        )
        if not user_to_update:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Пользователя с login '{login}' не существует",
            )

        role = await self.db.scalar(select(Role).where(Role.id == role_id))
        if not role:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Роли с id '{role_id}' не существует",
            )

        user_to_update.role_id = role_id
        updated_user = await self.update(user_to_update)

        return updated_user

    async def remove_user_role(self, login: str, role_id: str) -> None:
        """Удаление роли у пользователя"""

        user_to_role_delete = await self.db.scalar(
            select(User).where(self.model.login == login)
        )
        if not user_to_role_delete:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Пользователя с login '{login}' не существует",
            )

        role = await self.db.scalar(select(Role).where(Role.id == role_id))
        if not role:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Роли с id '{role_id}' не существует",
            )

        user_to_role_delete.role_id = None
        await self.update(user_to_role_delete)

    async def get_user(self, login: str) -> UserInDB:
        """Получение пользователя по логину"""

        user = await self.db.scalar(select(User).where(self.model.login == login))
        return user

    async def get_role_by_login(self, login: str) -> str:
        """Получение роли пользователя по логину"""

        query = (
            select(self.model)
            .options(joinedload(self.model.role))
            .where(self.model.login == login)
        )

        result = await self.db.execute(query)
        user = result.scalars().first()

        return user.role.name if user else None

    async def check_login(self, login: str, password: str) -> Any:
        """Проверка логина и пароля пользователя"""

        query = select(self.model).where(self.model.login == login)
        result = await self.db.execute(query)
        user = result.scalar()

        if not (user and user.check_password(password)):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=f"Неверный логин или пароль"
            )
        return user

    async def role_name_by_id(self, role_id: UUID) -> str:
        """Получение названия роли по id роли"""

        query = (
            select(self.model)
            .options(joinedload(self.model.role))
            .where(self.model.role_id == role_id)
        )

        result = await self.db.execute(query)
        user = result.scalars().first()

        return user.role.name if user else None
