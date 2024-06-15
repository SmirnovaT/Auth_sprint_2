from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response

from src.core.logger import auth_logger
from src.schemas.user import Login
from src.services.user import UserService
from src.services.auth_history import AuthHistoryService

router = APIRouter(tags=["login"])


@router.post(
    "/",
    summary="Аутентификация пользователя",
    status_code=HTTPStatus.OK,
    description="Предоставление пользователю JWT токена при вводе корректных логина и пароля.",
)
async def login(
    data: Login,
    response: Response,
    service: UserService = Depends(UserService),
    user_agent: Annotated[str | None, Header()] = None,
    history_service: AuthHistoryService = Depends(AuthHistoryService),
):
    try:
        res = await service.login(response, data)
        await history_service.set_history(
            login=data.user_login, user_agent=user_agent, success=True
        )
        return res
    except Exception as exc:
        auth_logger.error(f"Error: {exc}")
        await history_service.set_history(
            login=data.user_login, user_agent=user_agent, success=False
        )
        raise
