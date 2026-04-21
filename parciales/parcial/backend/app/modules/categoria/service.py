from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import select

from app.core.uow import UnitOfWork
from app.modules.categoria.model import Categoria
from app.modules.categoria.schema import CategoriaCreate, CategoriaUpdate


def list_categorias(
    uow: UnitOfWork,
    *,
    skip: int = 0,
    limit: int = 50,
    nombre: str | None = None,
) -> list[Categoria]:
    stmt = select(Categoria).where(Categoria.deleted_at == None)  # noqa: E711
    if nombre:
        stmt = stmt.where(Categoria.nombre.ilike(f"%{nombre}%"))
    stmt = stmt.offset(skip).limit(limit).order_by(Categoria.id)
    return list(uow.session.exec(stmt).all())


def get_categoria(uow: UnitOfWork, categoria_id: int) -> Categoria | None:
    categoria = uow.session.get(Categoria, categoria_id)
    if categoria is None or categoria.deleted_at is not None:
        return None
    return categoria


def _validate_parent(
    uow: UnitOfWork, parent_id: int | None, *, self_id: int | None = None
) -> None:
    if parent_id is None:
        return
    if self_id is not None and parent_id == self_id:
        raise ValueError("Una categoria no puede ser su propia padre")
    parent = uow.session.get(Categoria, parent_id)
    if parent is None or parent.deleted_at is not None:
        raise ValueError(f"Categoria padre {parent_id} no existe o está inactiva")


def create_categoria(uow: UnitOfWork, data: CategoriaCreate) -> Categoria:
    _validate_parent(uow, data.parent_id)
    categoria = Categoria(**data.model_dump())
    uow.session.add(categoria)
    uow.session.flush()
    uow.session.refresh(categoria)
    return categoria


def update_categoria(
    uow: UnitOfWork, categoria_id: int, data: CategoriaUpdate
) -> Categoria | None:
    categoria = uow.session.get(Categoria, categoria_id)
    if categoria is None or categoria.deleted_at is not None:
        return None
    payload = data.model_dump(exclude_unset=True)
    if "parent_id" in payload:
        _validate_parent(uow, payload["parent_id"], self_id=categoria_id)
    for field, value in payload.items():
        setattr(categoria, field, value)
    uow.session.add(categoria)
    uow.session.flush()
    uow.session.refresh(categoria)
    return categoria


def delete_categoria(uow: UnitOfWork, categoria_id: int) -> bool:
    categoria = uow.session.get(Categoria, categoria_id)
    if categoria is None or categoria.deleted_at is not None:
        return False
    categoria.deleted_at = datetime.now(timezone.utc)
    uow.session.add(categoria)
    uow.session.flush()
    return True
