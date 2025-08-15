import asyncio

import aiohttp

from banking.providers.alfa.schemas import AlfaScope
from core.config import settings
from infra.redis.redis_api import RedisAPI
from banking.providers.alfa.exceptions import AlfaTokenError


class AlfaTokenService:
    """Сервис для управления токенами доступа к Alfa Bank API"""
    
    TOKEN_KEY_PREFIX = "alfa:access_token"
    TOKEN_EXPIRATION_SECONDS = 60 * 55  # 55 минут
    TOKEN_ENDPOINT = f"{settings.alfa_base_url}/oidc/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    SEMAPHORE = asyncio.Semaphore(100)
    
    def __init__(self, redis: RedisAPI):
        self._redis = redis
        # Кэш токенов в памяти для каждого scope
        self._cached_tokens: dict[str, str] = {}
    
    def _get_token_key(self, scope: AlfaScope) -> str:
        """Получить ключ для кэширования токена определенного scope"""
        return f"{self.TOKEN_KEY_PREFIX}:{scope.value}"
    
    async def get_access_token(self, scope: AlfaScope) -> str:
        """Получить действующий токен доступа для указанного scope"""
        scope_key = scope.value
        
        # Проверяем кэш в памяти
        if scope_key in self._cached_tokens:
            return self._cached_tokens[scope_key]
        
        # Проверяем кэш в Redis
        token_key = self._get_token_key(scope)
        token = await self._redis.get(token_key)
        if token:
            self._cached_tokens[scope_key] = token
            return token
        
        # Получаем новый токен
        new_token = await self._fetch_new_token(scope)
        await self._cache_token(scope, new_token)
        return new_token
    
    async def _fetch_new_token(self, scope: AlfaScope) -> str:
        """Получить новый токен от Alfa Bank API для указанного scope"""
        payload = (
            "grant_type=client_credentials"
            f"&client_id={settings.alfa_client_id}"
            f"&client_secret={settings.alfa_client_secret}"
            f"&scope={scope.value}"
        )

        async with self.SEMAPHORE:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.TOKEN_ENDPOINT, data=payload, headers=self.headers) as resp:
                    if resp.status != 200:
                        try:
                            error_data = await resp.json()
                        except Exception:
                            error_data = {}

                        raise AlfaTokenError(
                            message=f"Ошибка получения токена от Alfa Bank",
                            status_code=resp.status,
                            response_data=error_data
                        )

                    data = await resp.json()
        return data["access_token"]
    
    async def _cache_token(self, scope: AlfaScope, token: str) -> None:
        """Кэшировать токен в Redis и памяти для указанного scope"""
        scope_key = scope.value
        self._cached_tokens[scope_key] = token
        token_key = self._get_token_key(scope)
        await self._redis.set(
            token_key, 
            token, 
            expire=self.TOKEN_EXPIRATION_SECONDS
        )
    
    async def invalidate_token(self, scope: AlfaScope) -> None:
        """Инвалидировать токен для указанного scope"""
        scope_key = scope.value
        
        if scope_key in self._cached_tokens:
            del self._cached_tokens[scope_key]
        
        token_key = self._get_token_key(scope)
        await self._redis.delete(token_key)
    
    async def invalidate_all_tokens(self) -> None:
        """Инвалидировать все токены"""
        self._cached_tokens.clear()
        
        # Удаляем все токены из Redis
        for scope in AlfaScope:
            token_key = self._get_token_key(scope)
            await self._redis.delete(token_key) 