"""
Tipos compartidos entre schemas.

`MoneyDecimal` y `QuantityDecimal` mantienen `Decimal` para la validación
interna pero se serializan a `float` en JSON. Esto evita que los frontends
tengan que parsear strings antes de usar `.toFixed()`.
"""

from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer


_to_float = PlainSerializer(
    lambda v: float(v) if v is not None else None,
    return_type=float,
    when_used="json",
)


# Importes a usar en los schemas en lugar de `Decimal` crudo.
MoneyDecimal = Annotated[Decimal, _to_float]
QuantityDecimal = Annotated[Decimal, _to_float]
