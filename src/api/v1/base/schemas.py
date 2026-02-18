from decimal import Decimal
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel
from pydantic.functional_serializers import PlainSerializer

DisplayDecimal = Annotated[
    Decimal,
    PlainSerializer(
        lambda v: str(v.quantize(Decimal("0.01"))),
        return_type=str,
    ),
]


class PaginationParams(BaseModel):
    limit: int | None = Query(None, ge=1, le=100, description="Количество элементов на странице")
    offset: int | None = Query(None, ge=0, description="Смещение от начала списка")
