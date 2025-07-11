from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from infra.postgres.models import WalletCurrency
from crypto_processing.network import matcher


class Address(BaseModel):
    network: str
    address: str


class WalletResponse(BaseModel):
    wallet_id: UUID
    currency: WalletCurrency
    balance: Decimal
    addresses: list[Address]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("addresses", mode="before")
    def parse_addresses(cls, raw_addresses: list[str]) -> list[dict]:
        if not raw_addresses:
            return []

        return [
            {"network": network, "address": address}
            for network, address in matcher.iter_matched(raw_addresses)
        ]


class WalletCurrencyList(BaseModel):
    currencies: list[str]
