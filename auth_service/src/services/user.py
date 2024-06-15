from http import HTTPStatus

from fastapi import Depends, Response, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from werkzeug.security import generate_password_hash

from src.core.config import settings
from src.core.logger import auth_logger
from src.db.cache import AsyncCacheService
from src.db.models import User
from src.db.postgres import get_session
from src.repositories.role import RoleRepository
from src.schemas.user import UserCreate, UserInDB, UserInDBWRole, Login
from src.repositories.user import UserRepository
from src.utils.jwt import validate_token, create_access_and_refresh_tokens
from src.schemas.user import PasswordChange


class UserService:
    """Сервис для взаимодействия с моделью User"""

    def __init__(
        self,
        db: AsyncSession = Depends(get_session),
        repository: UserRepository = Depends(),
        cache: AsyncCacheService = Depends(AsyncCacheService),
        role_repository: RoleRepository = Depends(RoleRepository),
    ):
        self.repository = repository
        self.db = db
        self.cache = cache
        self.role_repository = role_repository

    async def register(self, user_create: UserCreate) -> UserInDB:
        """Регистрация пользователя"""

        user_dto = jsonable_encoder(user_create)
        user = User(**user_dto)
        role_id = await self.role_repository.role_id_by_name(settings.default_user_role)
        user.role_id = role_id
        return await self.repository.create_user(user)

    async def change_user_role(self, login: str, role_id: str) -> UserInDBWRole:
        """Изменение роли пользователя"""

        return await self.repository.update_user_role(login, role_id)

    async def remove_user_role(self, login: str, role_id: str) -> None:
        """Удаление роли у пользователя"""

        return await self.repository.remove_user_role(login, role_id)

    async def refresh_token(
        self, refresh_token: str, response: Response
    ) -> JSONResponse:
        """Обновление токенов по рефреш токену"""

        decoded_refresh_token = await validate_token(refresh_token)

        user_login = decoded_refresh_token.get("user_login")
        user_role = await self.repository.get_role_by_login(user_login)

        if await self.cache.get_data_by_key(user_login) != refresh_token:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="У пользователя не совпадает рефреш токен из редиса и из cookies",
            )

        await self.update_all_token(user_login, user_role, response)

        return JSONResponse(content={"message": "Токен обновлен"})

    async def login(self, response: Response, data: Login):
        """Аутентификация пользователя"""

        user = jsonable_encoder(data)
        user = Login(**user)
        user_db = await self.repository.check_login(user.user_login, user.password)
        role = await self.repository.role_name_by_id(user_db.role_id)

        await self.update_all_token(user.user_login, role, response)
        return JSONResponse(content={"message": "Вход успешно выполнен"})

    async def change_password(
        self, response: Response, password_data: dict, password_change_data: dict | None
    ) -> JSONResponse:
        """Смена пароля пользователем"""

        user = jsonable_encoder(password_data)
        user = Login(**user)

        user_to_update = await self.repository.check_login(
            user.user_login, user.password
        )
        new_login_data = jsonable_encoder(password_change_data)
        new_login_data = PasswordChange(**new_login_data)

        if new_login_data.new_password:
            user_to_update.password = generate_password_hash(
                new_login_data.new_password
            )
        if new_login_data.new_login:
            user_to_update.login = new_login_data.new_login

        await self.repository.update(user_to_update)

        role = await self.repository.role_name_by_id(user_to_update.role_id)

        await self.update_all_token(user_to_update.login, role, response)

        auth_logger.info("Пароль и логин успешно обновлены")

        return JSONResponse(content={"message": "Пароль и логин успешно обновлены"})

    async def update_all_token(
        self, user_login: str, role: str, response: Response
    ) -> None:
        """Обновление токенов"""

        access_token, refresh_token = await create_access_and_refresh_tokens(
            user_login, role
        )

        response.set_cookie("access_token", access_token)
        response.set_cookie("refresh_token", refresh_token)

        await self.cache.create_or_update_record(user_login, refresh_token)

        auth_logger.info("Токены обновлены")

    async def logout(self, login, refresh_token: str, response: Response):
        await self.cache.delete_record(login)
        await self.cache.create_or_update_record("black_list", refresh_token)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
