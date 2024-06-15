from uuid import UUID

from fastapi import APIRouter, Depends, status, Request
from fastapi_pagination import Page, paginate

from src.constants.permissions import PERMISSIONS
from src.schemas.auth_history import AuthHistoryInDB
from src.services.auth_history import AuthHistoryService
from src.utils.jwt import check_token_and_role

router = APIRouter(tags=["auth-history"])


@router.get(
    "/{user_id}",
    response_model=Page[AuthHistoryInDB],
    status_code=status.HTTP_200_OK,
    summary="Получение истории аутентификаций пользователя",
)
async def get_auth_history(
    request: Request,
    user_id: UUID,
    service: AuthHistoryService = Depends(AuthHistoryService),
) -> Page[AuthHistoryInDB]:
    await check_token_and_role(request, PERMISSIONS["can_read_auth_history"])

    history_items = await service.get_history(user_id)
    return paginate(history_items)
