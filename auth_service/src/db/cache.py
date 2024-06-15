from abc import abstractmethod, ABC
from typing import Any

from fastapi import Depends
from redis.asyncio import Redis

from src.core.config import settings
from src.core.logger import auth_logger


redis: Redis | None = None


async def get_redis() -> Redis:
    return redis


class BaseAsyncCacheService(ABC):

    @abstractmethod
    async def create_or_update_record(self, key, value):
        pass

    @abstractmethod
    async def get_data_by_key(self, key):
        pass

    @abstractmethod
    async def delete_record(self, key):
        pass


class AsyncCacheService(BaseAsyncCacheService):
    """Имплементация класса для кеширования данных"""

    def __init__(self, cache: Redis = Depends(get_redis)):
        self.cache = cache

    async def create_or_update_record(self, key: str, value: Any) -> None:
        """Сохранение и обновление рефреш токена"""

        await self.cache.set(key, value, ex=settings.cache_expire_in_seconds)

    async def get_data_by_key(self, key: str) -> Any:
        """Получение данных из кеша по ключу"""

        try:
            data = await self.cache.get(key)
        except Exception as exc:
            auth_logger.error(
                f"Ошибка при взятии значения по ключу {key} из кеша: {exc}"
            )
            return None
        return data

    async def delete_record(self, key: str):
        try:
            await self.cache.delete(key)
        except Exception as exc:
            auth_logger.error(f"Ошибка при удалении записи по ключу {key}")
