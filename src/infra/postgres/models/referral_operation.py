from decimal import Decimal
from enum import Enum as PyEnum
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Enum, DECIMAL

from infra.postgres.mixins import CreateUpdateTimestampMixin
from infra.postgres.models.base import Base


class ReferralOperationType(PyEnum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class ReferralOperationStatus(PyEnum):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class ReferralOperation(Base, CreateUpdateTimestampMixin):
    __tablename__ = "referral_operation"

    referral_operation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        index=True
    )
    referral_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("referral.telegram_id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[ReferralOperationStatus] = mapped_column(
        Enum(ReferralOperationStatus, name="referral_operation_status_enum", native_enum=False),
        nullable=False,
    )
    operation_type: Mapped[ReferralOperationType] = mapped_column(
        Enum(ReferralOperationType, name="referral_operation_type_enum", native_enum=False),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(DECIMAL(precision=20, scale=6), nullable=False)
