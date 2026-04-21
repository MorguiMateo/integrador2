from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import select

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
    stmt = select(Ingrediente).where(Ingrediente.deleted_at == None)  # noqa: E711
    if nombre:
        stmt = stmt.where(Ingrediente.nombre.ilike(f"%{nombre}%"))
    if es_alergeno is not None:
        stmt = stmt.where(Ingrediente.es_alergeno == es_alergeno)
    stmt = stmt.offset(skip).limit(limit).order_by(Ingrediente.id)
    return list(uow.session.exec(stmt).all())


def get_ingrediente(uow: UnitOfWork, ingrediente_id: int) -> Ingrediente | None:
    ingrediente = uow.session.get(Ingrediente, ingrediente_id)
    if ingrediente is None or ingrediente.deleted_at is not None:
        return None
    return ingrediente


def create_ingrediente(uow: UnitOfWork, data: IngredienteCreate) -> Ingrediente:
    ingrediente = Ingrediente(**data.model_dump())
    uow.session.add(ingrediente)
    uow.session.flush()
    uow.session.refresh(ingrediente)
    return ingrediente


def update_ingrediente(
    uow: UnitOfWork, ingrediente_id: int, data: IngredienteUpdate
) -> Ingrediente | None:
    ingrediente = uow.session.get(Ingrediente, ingrediente_id)
    if ingrediente is None or ingrediente.deleted_at is not None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ingrediente, field, value)
    uow.session.add(ingrediente)
    uow.session.flush()
    uow.session.refresh(ingrediente)
    return ingrediente


def delete_ingrediente(uow: UnitOfWork, ingrediente_id: int) -> bool:
    ingrediente = uow.session.get(Ingrediente, ingrediente_id)
    if ingrediente is None or ingrediente.deleted_at is not None:
        return False
    ingrediente.deleted_at = datetime.now(timezone.utc)
    uow.session.add(ingrediente)
    uow.session.flush()
    return True
