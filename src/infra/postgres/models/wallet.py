from enum import Enum as PyEnum
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    UUID as PGUUID,
    text,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import ARRAY, String, DECIMAL

from infra.postgres.models.base import Base
from infra.postgres.mixins import CreateUpdateTimestampMixin

if TYPE_CHECKING:
    from infra.postgres.models.user import User # noqa: F401
    from infra.postgres.models.operation import Operation # noqa: F401


class WalletCurrency(str, PyEnum):
    USDT = "USDT"


class WalletStatus(str, PyEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class Wallet(Base, CreateUpdateTimestampMixin):
    __tablename__ = "wallet"

    wallet_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        index=True,
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", onupdate="CASCADE", ondelete="NO ACTION"),
        nullable=False
    )
    currency: Mapped[WalletCurrency] = mapped_column(
        Enum(WalletCurrency, name="wallet_currency_enum", native_enum=False),
        nullable=False,
    )
    balance: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=20, scale=6),
        nullable=False,
        default=Decimal("0.0"),
        server_default="0.0",
    )
    addresses: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default="{}"
    )
    status: Mapped[WalletStatus] = mapped_column(
        Enum(WalletStatus, name="wallet_status_enum", native_enum=False),
        default=WalletStatus.ACTIVE,
        server_default=WalletStatus.ACTIVE,
        nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="wallets")
    operations: Mapped[list["Operation"]] = relationship("Operation", back_populates="wallet")

    __table_args__ = (
        UniqueConstraint("currency", "telegram_id", name="uq_wallet_currency_telegram_id"),
    )
