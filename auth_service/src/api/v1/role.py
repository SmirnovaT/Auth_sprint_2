from fastapi import APIRouter, Depends, Request, status

from src.schemas.role import RoleGeneral
from src.constants.permissions import PERMISSIONS
from src.services.roles import RoleService
from src.utils.jwt import check_token_and_role

router = APIRouter(tags=["role"])


@router.get(
    "",
    response_model=list[RoleGeneral],
    status_code=status.HTTP_200_OK,
    summary="Просмотр всех ролей",
    description="Просмотр всех ролей в сервисе",
)
async def roles(
    request: Request,
    roles_service: RoleService = Depends(RoleService),
) -> list[RoleGeneral]:
    await check_token_and_role(request, PERMISSIONS["can_read_and_perform_roles"])

    all_roles = await roles_service.get_all_roles()

    return all_roles


@router.post(
    "",
    response_model=RoleGeneral,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой роли",
    description="Создание новой роли для разграничения прав пользователей",
)
async def role_creating(
    request: Request,
    role_name: str,
    roles_service: RoleService = Depends(RoleService),
) -> RoleGeneral:
    await check_token_and_role(request, PERMISSIONS["can_read_and_perform_roles"])

    created_role = await roles_service.create_role(role_name)

    return created_role


@router.patch(
    "/{old_role_name}",
    response_model=RoleGeneral,
    status_code=status.HTTP_200_OK,
    summary="Редактирование роли",
    description="Редактирование роли в сервисе",
)
async def role_updating(
    request: Request,
    old_role_name: str,
    new_role_name: str,
    roles_service: RoleService = Depends(RoleService),
) -> RoleGeneral:
    await check_token_and_role(request, PERMISSIONS["can_read_and_perform_roles"])

    updated_role = await roles_service.update_role(old_role_name, new_role_name)

    return updated_role


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление роли",
    description="Удаление роли из сервиса",
)
async def role_removing(
    request: Request,
    role_name: str,
    roles_service: RoleService = Depends(RoleService),
) -> None:
    await check_token_and_role(request, PERMISSIONS["can_read_and_perform_roles"])

    await roles_service.remove_role(role_name)
