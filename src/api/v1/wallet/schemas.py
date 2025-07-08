from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from infra.postgres.models import WalletCurrency
from processing.network import WalletAddressMatcher


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
            for network, address in WalletAddressMatcher().iter_matched(raw_addresses)
        ]


class WalletCurrencyList(BaseModel):
    currencies: list[str]
