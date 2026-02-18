from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, Field, model_validator

from api.v1.base.schemas import DisplayDecimal
from infra.postgres.models import WalletCurrency
from crypto_processing.network import matcher


class Address(BaseModel):
    network: str = Field(..., description="Название сети криптовалюты", examples=["TRC20"])
    address: str = Field(..., description="Адрес кошелька в указанной сети", examples=["TQn9Y2khDD95J42FQtQTdwVVRqQjKCz9JQ"])


class WalletResponse(BaseModel):
    wallet_id: UUID = Field(..., description="Уникальный идентификатор кошелька")
    currency: WalletCurrency = Field(..., description="Тип криптовалюты кошелька", examples=["USDT"])
    balance: DisplayDecimal = Field(..., description="Текущий баланс кошелька в основной валюте")
    addresses: list[Address] = Field(..., description="Список адресов для пополнения кошелька")
    icon: str = Field("")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def set_icon_by_currency(self) -> "WalletResponse":
        currency_to_icon: dict[WalletCurrency, str] = {
            WalletCurrency.USDT: "https://assets.coingecko.com/coins/images/325/large/Tether-logo.png",
        }
        if not self.icon:
            self.icon = currency_to_icon.get(self.currency, "")
        return self

    @field_validator("addresses", mode="before")
    def parse_addresses(cls, raw_addresses: list[str]) -> list[dict]:
        if not raw_addresses:
            return []

        return [
            {"network": network, "address": address}
            for network, address in matcher.iter_matched(raw_addresses)
        ]


class WalletCurrencyList(BaseModel):
    currencies: list[str] = Field(..., description="Список поддерживаемых криптовалют")


class WithdrawRequest(BaseModel):
    address: str = Field(..., description="Адрес для вывода средств (автоматически определяется сеть)", examples=["TQn9Y2khDD95J42FQtQTdwVVRqQjKCz9JQ"])
    amount: Decimal = Field(..., description="Сумма для вывода в основной валюте кошелька", examples=["100.00", "50.50", "1000.00"])
