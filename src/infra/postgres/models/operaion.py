from uuid import UUID
from decimal import Decimal
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DECIMAL, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infra.postgres.models.base import Base
from infra.postgres.mixins import CreateTimestampMixin


class OperationType(PyEnum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class OperationStatus(PyEnum):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class Operation(Base, CreateTimestampMixin):
    __tablename__ = "operation"

    operation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        index=True
    )
    wallet_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("wallet.wallet_id", onupdate="CASCADE", ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(255), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(precision=20, scale=6), nullable=False)
    fee: Mapped[Decimal] = mapped_column(DECIMAL(precision=20, scale=6), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(DECIMAL(precision=20, scale=6), nullable=False)

    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="operations")
    crypto_replenishment: Mapped[Optional["CryptocurrencyReplenishment"]] = relationship(
        "CryptocurrencyReplenishment", back_populates="operation", uselist=False
    )
