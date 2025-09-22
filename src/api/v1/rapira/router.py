import aiohttp

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/rates", tags=["Rapira"])


@router.get('')
async def get_rate_by_currency(currency: str | None = None):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.rapira.net/open/market/rates") as response:
            response.raise_for_status()
            rates = await response.json()
            data = rates.get("data")
            if currency is None:
                return data

    for rate in data:
        if rate["quoteCurrency"] == currency and rate["baseCurrency"] == "RUB":
            return rate

    raise HTTPException(status_code=404)
