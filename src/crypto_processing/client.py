import aiohttp

from core.config import settings
from crypto_processing.schemas import (
    ApiKeyRefreshResponse,
    ClientRegistrationResponse,
    WebhookRegistrationResponse,
)


class CryptoProcessingClient:
    BASE_URL = settings.crypto_processing_base_url
    api_key = settings.crypto_processing_token
    timeout = aiohttp.ClientTimeout(total=10)

    def __init__(self):
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session and not self.session.closed:
            await self.session.close()

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    async def _request(self, method: str, path: str, json: dict | None = None) -> dict:
        if not self.session:
            raise RuntimeError("Client session is not initialized. Use 'async with CryptoProcessingClient() as client'.")

        url = f"{self.BASE_URL}{path}"
        async with self.session.request(method, url, headers=self._headers(), json=json) as resp:
            if resp.status < 200 or resp.status >= 300:
                text = await resp.text()
                raise Exception(f"Request failed [{resp.status}]: {url} — {text}")
            return await resp.json()

    async def refresh_api_key(self) -> ApiKeyRefreshResponse:
        payload = {"oldApiKey": self.api_key}
        raw = await self._request("POST", "/account/refresh-api-key", json=payload)
        return ApiKeyRefreshResponse.model_validate(raw)

    async def register_client(self) -> ClientRegistrationResponse:
        raw = await self._request("POST", "/client", json={})
        return ClientRegistrationResponse.model_validate(raw)

    async def register_webhook(self, webhook_url: str) -> WebhookRegistrationResponse:
        payload = {"webhookAddress": webhook_url}
        raw = await self._request("POST", "/webhook", json=payload)
        return WebhookRegistrationResponse.model_validate(raw)

    async def withdraw_funds(self, address: str, amount: int) -> bool:
        payload = {"amount": amount, "address": address}
        try:
            raw = await self._request("POST", "/withdrawal", json=payload)
        except Exception:
            return False
        return True
