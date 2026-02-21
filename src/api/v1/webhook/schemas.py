from typing import Literal

from pydantic import BaseModel, Field
from decimal import Decimal


class CryptocurrencyReplenishmentCreate(BaseModel):
    tx_id: str = Field(..., description="ID транзакции")
    from_address: str = Field(..., description="Адрес отправителя (base58)")
    to_address: str = Field(..., description="Адрес получателя (base58)")
    amount: Decimal = Field(..., description="Сумма в USDT")
    crypto_type: str = Field(..., description="Тип криптовалюты (например, USDT)")
    type: Literal["refill", "withdraw"] = Field(..., description="Тип операции")
