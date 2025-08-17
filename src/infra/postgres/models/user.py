from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, Text, CHAR

from infra.postgres.models.base import Base
from infra.postgres.mixins import CreateTimestampMixin

if TYPE_CHECKING:
    from infra.postgres.models.wallet import Wallet # noqa: F401
    from infra.postgres.models.referral import Referral # noqa: F401


class User(Base, CreateTimestampMixin):
    __tablename__ = 'user'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    entry_code: Mapped[str | None] = mapped_column(CHAR(4), nullable=True)

    referral: Mapped["Referral"] = relationship(
        "Referral",
        back_populates="user",
        uselist=False,
        foreign_keys="[Referral.telegram_id]",
    )
    wallets: Mapped[list["Wallet"]] = relationship(
        "Wallet",
        back_populates="user"
    )
    referred_users: Mapped[list["Referral"]] = relationship(
        "Referral",
        back_populates="referrer",
        foreign_keys="[Referral.referred_by]"
    )
