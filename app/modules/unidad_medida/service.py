from __future__ import annotations
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.core.uow import UnitOfWork
from app.modules.unidad_medida.model import UnidadMedida
from app.modules.unidad_medida.schema import UnidadMedidaCreate, UnidadMedidaRead


def list_unidades(*, skip: int = 0, limit: int = 50) -> list[UnidadMedidaRead]:
    with UnitOfWork() as uow:
        unidades = uow.unidades_medida.list(skip=skip, limit=limit)
        return [UnidadMedidaRead.model_validate(u) for u in unidades]


def create_unidad(data: UnidadMedidaCreate) -> UnidadMedidaRead:
    try:
        with UnitOfWork() as uow:
            unidad = uow.unidades_medida.save(UnidadMedida(**data.model_dump()))
            return UnidadMedidaRead.model_validate(unidad)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe una unidad con ese nombre o símbolo")
