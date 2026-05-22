from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from app.core.uow import UnitOfWork
from app.modules.unidad_medida import service
from app.modules.unidad_medida.schema import UnidadMedidaCreate, UnidadMedidaRead

router = APIRouter(prefix="/unidades-medida", tags=["unidades-medida"])

@router.get("", response_model=list[UnidadMedidaRead])
def listar_unidades_medida(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50
):

    with UnitOfWork() as uow:
        return service.list_unidades(uow, skip=skip, limit=limit)

@router.post("", response_model=UnidadMedidaRead, status_code=status.HTTP_201_CREATED)
def crear_unidades_medida(payload: UnidadMedidaCreate):

    try:
        with UnitOfWork() as uow:
            return service.create_unidad(uow, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe una unidad con ese nombre o símbolo")
        