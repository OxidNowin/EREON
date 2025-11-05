import json
import redis.asyncio as redis

from core.config import settings


class RedisAPI:
    _pool: redis.ConnectionPool = redis.ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=15,
        decode_responses=True,
    )

    def __init__(self):
        self._client = redis.Redis(connection_pool=self._pool)

    async def close(self):
        await self._client.aclose()

    async def set(self, key: str, value: str, expire: int = 0):
        await self._client.set(name=key, value=value, ex=expire or None)

    async def get(self, key: str) -> str | None:
        return await self._client.get(name=key)

    async def delete(self, key: str):
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))

    async def incr(self, key: str) -> int:
        return await self._client.incr(key)

    async def expire(self, key: str, seconds: int) -> bool:
        return await self._client.expire(key, seconds)

    async def ping(self) -> bool:
        return await self._client.ping()

    async def lpush(self, key: str, value: str):
        """Добавить значение в начало списка"""
        await self._client.lpush(key, value)

    async def rpush(self, key: str, value: str):
        """Добавить значение в конец списка"""
        await self._client.rpush(key, value)

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> list[str]:
        """Получить элементы списка"""
        return await self._client.lrange(key, start, end)

    async def llen(self, key: str) -> int:
        """Получить длину списка"""
        return await self._client.llen(key)

    async def ltrim(self, key: str, start: int, end: int):
        """Обрезать список до указанного диапазона"""
        await self._client.ltrim(key, start, end)

    async def set_json(self, key: str, value: dict, expire: int = 0):
        """Сохранить JSON объект"""
        await self._client.set(name=key, value=json.dumps(value), ex=expire or None)

    async def get_json(self, key: str) -> dict | None:
        """Получить JSON объект"""
        value = await self._client.get(name=key)
        if value:
            return json.loads(value)
        return None

    async def lpush_json(self, key: str, value: dict):
        """Добавить JSON объект в начало списка"""
        await self._client.lpush(key, json.dumps(value))

    async def rpush_json(self, key: str, value: dict):
        """Добавить JSON объект в конец списка"""
        await self._client.rpush(key, json.dumps(value))

    async def lrange_json(self, key: str, start: int = 0, end: int = -1) -> list[dict]:
        """Получить список JSON объектов"""
        values = await self._client.lrange(key, start, end)
        return [json.loads(v) for v in values]
