from __future__ import annotations

from app.core.uow import UnitOfWork
from app.modules.ingrediente.model import Ingrediente
from app.modules.ingrediente.schema import IngredienteCreate, IngredienteUpdate


def list_ingredientes(
    uow: UnitOfWork,
    *,
    skip: int = 0,
    limit: int = 50,
    nombre: str | None = None,
    es_alergeno: bool | None = None,
) -> list[Ingrediente]:
    return uow.ingredientes.list(
        skip=skip, limit=limit, nombre=nombre, es_alergeno=es_alergeno
    )


def get_ingrediente(uow: UnitOfWork, ingrediente_id: int) -> Ingrediente | None:
    return uow.ingredientes.get(ingrediente_id)


def create_ingrediente(uow: UnitOfWork, data: IngredienteCreate) -> Ingrediente:
    return uow.ingredientes.save(Ingrediente(**data.model_dump()))


def update_ingrediente(
    uow: UnitOfWork, ingrediente_id: int, data: IngredienteUpdate
) -> Ingrediente | None:
    ingrediente = uow.ingredientes.get(ingrediente_id)
    if ingrediente is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ingrediente, field, value)
    return uow.ingredientes.save(ingrediente)


def delete_ingrediente(uow: UnitOfWork, ingrediente_id: int) -> bool:
    return uow.ingredientes.soft_delete(ingrediente_id)
