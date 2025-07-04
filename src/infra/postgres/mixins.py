from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class CreateTimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )


class UpdateTimestampMixin:
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )


class CreateUpdateTimestampMixin(CreateTimestampMixin, UpdateTimestampMixin):
    ...
