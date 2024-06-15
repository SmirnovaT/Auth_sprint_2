from fastapi import Depends

from src.repositories.role import RoleRepository
from src.schemas.role import RoleGeneral


class RoleService:
    """Имплементация класса для взаимодействия с ролями пользователей"""

    def __init__(
        self,
        repository: RoleRepository = Depends(RoleRepository),
    ):
        self.repository = repository

    async def get_all_roles(self) -> list[RoleGeneral]:
        """Получение всех ролей, заведенных в сервисе"""

        all_roles = await self.repository.get_roles()

        return all_roles

    async def create_role(self, role_name: str) -> RoleGeneral:
        """Создание новой роли"""

        created_role = await self.repository.create_role(role_name)

        return created_role

    async def update_role(self, old_role_name: str, new_role_name: str) -> RoleGeneral:
        """Изменение роли"""

        updated_role = await self.repository.update_role(old_role_name, new_role_name)

        return updated_role

    async def remove_role(self, role_name: str) -> None:
        """Удаление роли"""

        await self.repository.remove_role(role_name)
