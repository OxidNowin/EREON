from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DECIMAL, text, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infra.postgres.models.base import Base
from infra.postgres.mixins import CreateTimestampMixin


class SbpPayment(Base, CreateTimestampMixin):
    __tablename__ = "sbp_payment"

    sbp_payment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        index=True
    )
    operation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("operation.operation_id", onupdate="CASCADE", ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )
    rub_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_rub: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    total_amount_rub: Mapped[int] = mapped_column(Integer, nullable=False)
    crypto_amount: Mapped[Decimal] = mapped_column(DECIMAL(precision=20, scale=6), nullable=False)
    fee_crypto: Mapped[Decimal] = mapped_column(DECIMAL(precision=20, scale=6), nullable=False, server_default="0")
    total_amount_crypto: Mapped[Decimal] = mapped_column(DECIMAL(precision=20, scale=6), nullable=False)
    currency: Mapped[str] = mapped_column(String(32), nullable=False)
    exchange: Mapped[Decimal] = mapped_column(DECIMAL(precision=20, scale=6), nullable=False)
    sbp_url: Mapped[str] = mapped_column(Text, nullable=False)
    outgoing_payment_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    operation: Mapped["Operation"] = relationship("Operation", back_populates="sbp_payments") 
    