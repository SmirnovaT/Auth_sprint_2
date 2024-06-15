from http import HTTPStatus

from fastapi import APIRouter, Depends, Request, status, Response, HTTPException

from src.constants.permissions import PERMISSIONS
from src.schemas.user import UserCreate, UserInDB, UserInDBWRole, Login
from src.services.user import UserService
from src.utils.jwt import check_token_and_role, validate_token
from src.schemas.user import PasswordChange

router = APIRouter(tags=["user"])


@router.post(
    "/signup",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def create_user(
    user_create: UserCreate, service: UserService = Depends(UserService)
) -> UserInDB:
    return await service.register(user_create)


@router.patch(
    "/{login}/roles/{role_id}",
    response_model=UserInDBWRole,
    status_code=status.HTTP_200_OK,
    summary="Смена роли у пользователя",
)
async def change_role(
    request: Request,
    login: str,
    role_id: str,
    service: UserService = Depends(UserService),
) -> UserInDBWRole:
    await check_token_and_role(request, PERMISSIONS["can_read_and_perform_roles"])

    return await service.change_user_role(login, role_id)


@router.delete(
    "/{login}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление роли у пользователя",
)
async def remove_role_from_user(
    request: Request,
    login: str,
    role_id: str,
    service: UserService = Depends(UserService),
) -> None:
    await check_token_and_role(request, PERMISSIONS["can_read_and_perform_roles"])

    await service.remove_user_role(login, role_id)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов по рефреш токену",
)
async def refresh_token(
    request: Request, response: Response, service: UserService = Depends(UserService)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Пользователь не авторизован, нет рефреш токена в cookies",
        )

    return await service.refresh_token(refresh_token, response)


@router.patch(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Смена пароля пользователем",
)
async def change_password(
    response: Response,
    password_data: Login,
    password_change_data: PasswordChange | None,
    service: UserService = Depends(UserService),
):
    return await service.change_password(response, password_data, password_change_data)


@router.get(
    "/logout",
    status_code=HTTPStatus.OK,
    summary="Выход пользователя",
)
async def logout(
    login,
    request: Request,
    response: Response,
    service: UserService = Depends(UserService),
):
    refresh_token = request.cookies.get("refresh_token")
    await validate_token(refresh_token)
    return await service.logout(login, refresh_token, response)
