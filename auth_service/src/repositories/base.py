from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import auth_logger
from src.db.postgres import get_session
from src.db import models


class BaseRepository:
    """Базовый класс, который предоставляет основные
    операции CRUD для взаимодействия с базой данных"""

    model = models

    def __init__(self, db: AsyncSession = Depends(get_session)):
        """Функция инициализирует репозиторий с сессией БД"""

        self.db = db

    async def get(self, table: Any) -> list[Any]:
        """Базовая функция по получению всех сущностей в БД"""

        try:
            return list(await self.db.scalars(select(table)))
        except DatabaseError as db_err:
            auth_logger.error(
                f"Возникла ошибка в ходе запроса к таблице '{table}': {db_err}",
            )

            raise HTTPException(
                status_code=500,
                detail=f"Возникла ошибка в ходе запроса к таблице '{table}'",
            )

    async def create(self, item: Any) -> Any:
        """Базовая функция по созданию сущности в БД"""

        try:
            self.db.add(item)
            await self.db.commit()
            await self.db.refresh(item)
            return item

        except IntegrityError as exc:
            auth_logger.error(exc)
            constraint_name = exc.orig.args[0].split('"')[1]
            field_name = constraint_name.split("_")[1]

            raise HTTPException(
                status_code=400,
                detail=f"Значение поля: '{field_name}' не уникально",
            )

    async def update(self, item: Any) -> Any:
        """Базовая функция по изменению сущности в БД"""

        try:
            await self.db.commit()
            await self.db.refresh(item)
            return item
        except DatabaseError as db_err:
            auth_logger.error(
                f"Возникла ошибка в ходе запроса к БД на изменение: {db_err}",
            )

            raise HTTPException(
                status_code=500,
                detail=f"Возникла ошибка в ходе запроса к БД на изменение: {db_err}",
            )

    async def delete(self, item: Any) -> None:
        """Базовая функция по удалению сущности из БД"""

        try:
            await self.db.delete(item)
            await self.db.commit()
        except DatabaseError as db_err:
            auth_logger.error(
                f"Возникла ошибка в ходе запроса к БД на удаление: {db_err}",
            )

            raise HTTPException(
                status_code=500,
                detail=f"Возникла ошибка в ходе запроса к БД на удаление: {db_err}",
            )
