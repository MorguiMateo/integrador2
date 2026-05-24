from __future__ import annotations
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.core.uow import UnitOfWork
from app.modules.ingrediente.model import Ingrediente
from app.modules.ingrediente.schema import IngredienteCreate, IngredienteRead, IngredienteUpdate


def list_ingredientes(*, skip: int = 0, limit: int = 50, nombre: Optional[str] = None, es_alergeno: Optional[bool] = None) -> list[IngredienteRead]:
    with UnitOfWork() as uow:
        ingredientes = uow.ingredientes.list(skip=skip, limit=limit, nombre=nombre, es_alergeno=es_alergeno)
        return [IngredienteRead.model_validate(i) for i in ingredientes]


def get_ingrediente(ingrediente_id: int) -> IngredienteRead:
    with UnitOfWork() as uow:
        ingrediente = uow.ingredientes.get(ingrediente_id)
        if ingrediente is None:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return IngredienteRead.model_validate(ingrediente)


def create_ingrediente(data: IngredienteCreate) -> IngredienteRead:
    try:
        with UnitOfWork() as uow:
            ingrediente = uow.ingredientes.save(Ingrediente(**data.model_dump()))
            return IngredienteRead.model_validate(ingrediente)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe un ingrediente con ese nombre")


def update_ingrediente(ingrediente_id: int, data: IngredienteUpdate) -> IngredienteRead:
    try:
        with UnitOfWork() as uow:
            ingrediente = uow.ingredientes.get(ingrediente_id)
            if ingrediente is None:
                raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(ingrediente, field, value)
            ingrediente = uow.ingredientes.save(ingrediente)
            return IngredienteRead.model_validate(ingrediente)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe un ingrediente con ese nombre")


def delete_ingrediente(ingrediente_id: int) -> None:
    try:
        with UnitOfWork() as uow:
            if not uow.ingredientes.delete(ingrediente_id):
                raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    except IntegrityError:
        raise HTTPException(status_code=409, detail="No se puede eliminar: el ingrediente está en uso por un producto")
