from uuid import UUID
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    VARCHAR,
    UUID as PGUUID,
    text,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.postgres.models.base import Base
from infra.postgres.mixins import CreateUpdateTimestampMixin


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
        unique=True,
        nullable=False
    )
    token: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)
    status: Mapped[WalletStatus] = mapped_column(
        Enum(WalletStatus, name="wallet_status_enum", native_enum=False),
        default=WalletStatus.ACTIVE,
        server_default=WalletStatus.ACTIVE,
        nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="wallet")
