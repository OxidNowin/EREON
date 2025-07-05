from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.postgres.models.base import Base


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
