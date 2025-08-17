from typing import TYPE_CHECKING
from decimal import Decimal
from uuid import UUID

from sqlalchemy.dialects.mysql.types import DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infra.postgres.models.base import Base
from infra.postgres.mixins import CreateTimestampMixin

if TYPE_CHECKING:
    from infra.postgres.models.operation import Operation # noqa: F401


class CryptocurrencyReplenishment(Base, CreateTimestampMixin):
    __tablename__ = "cryptocurrency_replenishment"

    tx_id: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    from_address: Mapped[str] = mapped_column(String(255), nullable=False)
    to_address: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(precision=20, scale=6), nullable=False)
    crypto_type: Mapped[str] = mapped_column(String(255), nullable=False)
    operation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("operation.operation_id", onupdate="CASCADE", ondelete="NO ACTION"),
        nullable=False
    )

    operation: Mapped["Operation"] = relationship("Operation", back_populates="crypto_replenishment")
