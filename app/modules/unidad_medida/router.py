from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.modules.unidad_medida import service
from app.modules.unidad_medida.schema import UnidadMedidaCreate, UnidadMedidaRead

router = APIRouter(prefix="/unidades-medida", tags=["unidades-medida"])


@router.get("", response_model=list[UnidadMedidaRead])
def listar_unidades_medida(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,
) -> list[UnidadMedidaRead]:
    return service.list_unidades(skip=skip, limit=limit)


@router.post("", response_model=UnidadMedidaRead, status_code=status.HTTP_201_CREATED)
def crear_unidades_medida(payload: UnidadMedidaCreate) -> UnidadMedidaRead:
    return service.create_unidad(payload)
