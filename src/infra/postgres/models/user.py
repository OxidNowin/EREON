from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, Text, CHAR

from infra.postgres.models.base import Base
from infra.postgres.mixins import CreateTimestampMixin


class User(Base, CreateTimestampMixin):
    __tablename__ = 'user'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    entry_code: Mapped[str] = mapped_column(CHAR(4), nullable=False)

    referral: Mapped["Referral"] = relationship(
        "Referral",
        back_populates="user",
        uselist=False,
        foreign_keys="[Referral.telegram_id]",
    )
    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        back_populates="user",
        uselist=False
    )
    referred_users: Mapped[list["Referral"]] = relationship(
        "Referral",
        back_populates="referrer",
        foreign_keys="[Referral.referred_by]"
    )
