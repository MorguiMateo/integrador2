from __future__ import annotations
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.core.uow import UnitOfWork
from app.modules.ingrediente.model import Ingrediente
from app.modules.ingrediente.schema import IngredienteCreate, IngredienteRead, IngredienteUpdate

##trae la lista del repo y la pasa a schema para devolverla como json
def list_ingredientes(*, skip: int = 0, limit: int = 50, nombre: Optional[str] = None, es_alergeno: Optional[bool] = None) -> list[IngredienteRead]:
    with UnitOfWork() as uow:
        ingredientes = uow.ingredientes.list(skip=skip, limit=limit, nombre=nombre, es_alergeno=es_alergeno)
        return [IngredienteRead.model_validate(i) for i in ingredientes]

##busca por id, si no existe tira 404
def get_ingrediente(ingrediente_id: int) -> IngredienteRead:
    with UnitOfWork() as uow:
        ingrediente = uow.ingredientes.get(ingrediente_id)
        if ingrediente is None:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return IngredienteRead.model_validate(ingrediente)

##crea el ingrediente. si el nombre ya existe, la base tira IntegrityError y lo devolvemos como 409
def create_ingrediente(data: IngredienteCreate) -> IngredienteRead:
    try:
        with UnitOfWork() as uow:
            ingrediente = uow.ingredientes.save(Ingrediente(**data.model_dump()))
            return IngredienteRead.model_validate(ingrediente)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe un ingrediente con ese nombre")

##exclude_unset hace que solo se actualicen los campos que el cliente realmente mando, el resto no se pisa
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

##si no existe tira 404, y si lo usa un producto activo tira 409. recien ahi lo borra
def delete_ingrediente(ingrediente_id: int) -> None:
    with UnitOfWork() as uow:
        if uow.ingredientes.get(ingrediente_id) is None:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        if uow.ingredientes.tiene_productos_activos(ingrediente_id):
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar: el ingrediente está en uso por un producto activo.",
            )
        uow.ingredientes.delete(ingrediente_id)
