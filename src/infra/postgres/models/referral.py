from typing import TYPE_CHECKING
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Integer, Enum

from infra.postgres.models.base import Base

if TYPE_CHECKING:
    from infra.postgres.models.user import User # noqa: F401


class ReferralType(PyEnum):
    FIXED_INCOME = "FIXED_INCOME"
    PERCENTAGE_INCOME = "PERCENTAGE_INCOME"


class Referral(Base):
    __tablename__ = "referral"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    referred_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("user.telegram_id", onupdate="CASCADE", ondelete="NO ACTION"),
        nullable=True,
        index=True,
    )
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    type: Mapped[ReferralType | None] = mapped_column(
        Enum(ReferralType, name="referral_type_enum", native_enum=False),
        nullable=True,
    )
    referral_count: Mapped[int] = mapped_column(Integer, server_default="0")
    balance: Mapped[int] = mapped_column(Integer, server_default="0")


    user: Mapped["User"] = relationship(
        "User",
        back_populates="referral",
        foreign_keys=[telegram_id]
    )
    referrer: Mapped["User"] = relationship(
        "User",
        back_populates="referred_users",
        foreign_keys=[referred_by]
    )
