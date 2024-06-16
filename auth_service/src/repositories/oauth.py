from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import DatabaseError

from src.core.logger import auth_logger
from src.db import models
from src.db.models import OAuthAccount
from src.repositories.base import BaseRepository


class OAuthRepository(BaseRepository):
    """Репозиторий для взаимодействия с моделью OAuthAccount"""

    model = models.OAuthAccount

    async def create_oauth_account(
            self, new_oauth_account: OAuthAccount,
    ) -> OAuthAccount | None:
        """
        Creates new OAuth account
        """

        return await self.create(new_oauth_account)

    async def get_oauth_user(
            self, oauth_user_id: str, oauth_provider_name: str,
    ) -> OAuthAccount | None:
        """
        Finds user in OAuthAccount
        """
        try:
            oauth_user = await self.db.scalar(
                select(self.model).where(
                    self.model.oauth_user_id == oauth_user_id,
                    self.model.oauth_provider_name == oauth_provider_name,
                )
            )

            return oauth_user
        except DatabaseError as db_err:
            auth_logger.error(
                f"Возникла ошибка в ходе запроса на поиск аккаунта пользователя "
                f"к {self.model}: {db_err}",
            )

            raise HTTPException(
                status_code=500,
                detail=f"Возникла ошибка в ходе запроса к {self.model}: {db_err}",
            )
