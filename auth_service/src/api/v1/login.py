from http import HTTPStatus
from typing import Annotated

from fastapi import (
    APIRouter, Depends, Header,
    HTTPException, Request, Response, status,
)
from fastapi.responses import RedirectResponse

from src.constants.oauth_providers import OAUTH_PROVIDERS
from src.core.logger import auth_logger
from src.schemas.user import Login
from src.services.oauth import YandexOAuthService
from src.services.user import UserService
from src.services.auth_history import AuthHistoryService
from src.utils.general import make_random_string

router = APIRouter(tags=["login"])


@router.post(
    "/",
    status_code=HTTPStatus.OK,
    summary="Аутентификация пользователя",
    description="Предоставление пользователю JWT токена "
                "при вводе корректных логина и пароля.",
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
        auth_logger.error(f"Error while login: {exc}")
        await history_service.set_history(
            login=data.user_login, user_agent=user_agent, success=False
        )
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail=f"Что-то пошло не так. "
                                                        f"Проверьте логин или пароль."
        )


@router.get(
    "/oauth/{oauth_provider}",
    response_class=RedirectResponse,
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
    summary="Войти в онлайн-кинотеатр с помощью OAuth",
    description="Аутентификация с помощью провайдера OAuth",
)
async def oauth_login(
        request: Request,
        oauth_provider: str,
        yandex_service: YandexOAuthService = Depends(YandexOAuthService),
) -> RedirectResponse:
    if oauth_provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such provider for OAuth in Online Cinema"
        )

    session_state = make_random_string()
    request.session["state"] = session_state

    if oauth_provider == "yandex":
        redirect_url = await yandex_service.generate_redirect_url(session_state)

        return RedirectResponse(redirect_url)


@router.get(
    "/oauth/{oauth_provider}/redirect",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
    response_class=Response,
    summary="Выдача access и refresh токенов с помощью OAuth",
    description="Аутентификация с помощью провайдера OAuth",

)
async def oauth_login_redirect(
        request: Request,
        response: Response,
        yandex_service: YandexOAuthService = Depends(YandexOAuthService),
        user_service: UserService = Depends(UserService),
        history_service: AuthHistoryService = Depends(AuthHistoryService),
) -> Response:
    session_state = request.query_params.get("state")
    code = request.query_params.get("code")
    if not session_state or not code:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Something gone wrong with session state or code."
        )

    oauth_provider = request.path_params.get("oauth_provider")
    if not oauth_provider:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No 'oauth_provider' parameter in request."
        )

    if oauth_provider == "yandex":
        service_user = await yandex_service.get_service_user(code)
        user_data = Login(user_login=service_user.login, password=service_user.password)

        try:
            await user_service.login(response, user_data)
            await history_service.set_history(
                login=user_data.user_login, user_agent=request.headers["user-agent"], success=True
            )
        except Exception as exc:
            auth_logger.error(f"Error while OAuth login: {exc}")
            await history_service.set_history(
                login=user_data.user_login, user_agent=request.headers["user-agent"], success=False
            )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=f"Что-то пошло не так. "
                                                            f"Проверьте логин или пароль."
            )

    return Response()
