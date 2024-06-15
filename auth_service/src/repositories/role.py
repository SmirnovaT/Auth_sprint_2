from uuid import UUID
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select


from src.db import models
from src.db.models import Role
from src.repositories.base import BaseRepository
from src.schemas.role import RoleGeneral


class RoleRepository(BaseRepository):
    """Репозиторий для взаимодействия с моделью Role"""

    model = models.Role

    async def get_roles(self) -> list[RoleGeneral]:
        """Получение всех ролей"""

        return await self.get(self.model)

    async def create_role(self, role_name: str) -> RoleGeneral:
        """Создание роли"""

        role_already_exist = await self.db.scalar(
            select(Role).where(self.model.name == role_name)
        )
        if role_already_exist:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Роль с названием '{role_name}' уже существует",
            )

        created_role = await self.create(Role(name=role_name))

        return created_role

    async def update_role(self, old_role_name: str, new_role_name: str) -> RoleGeneral:
        """Редактирование роли"""

        role_to_update = await self.db.scalar(
            select(Role).where(self.model.name == old_role_name)
        )
        if not role_to_update:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Роли с name '{old_role_name}' не существует",
            )

        role_to_update.name = new_role_name
        updated_role = await self.update(role_to_update)

        return updated_role

    async def remove_role(self, role_name: str) -> None:
        """Удаление роли"""

        role_to_delete = await self.db.scalar(
            select(Role).where(self.model.name == role_name)
        )
        if not role_to_delete:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Роли с name '{role_name}' не существует",
            )

        await self.delete(role_to_delete)

    async def role_id_by_name(self, role: str) -> UUID:
        """Получение id роли по названию роли"""

        query = select(self.model.id).where(self.model.name == role)

        result = await self.db.execute(query)
        role_id = result.scalars().first()

        return role_id
