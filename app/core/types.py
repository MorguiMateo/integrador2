from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer


_to_float = PlainSerializer(
    lambda v: float(v) if v is not None else None,
    return_type=float,
    when_used="json",
)


MoneyDecimal = Annotated[Decimal, _to_float]
QuantityDecimal = Annotated[Decimal, _to_float]
