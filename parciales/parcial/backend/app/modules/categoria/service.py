from __future__ import annotations

from app.core.uow import UnitOfWork
from app.modules.categoria.model import Categoria
from app.modules.categoria.schema import CategoriaCreate, CategoriaUpdate


def list_categorias(
    uow: UnitOfWork,
    *,
    skip: int = 0,
    limit: int = 50,
    nombre: str | None = None,
    incluir_eliminados: bool = False,
) -> list[Categoria]:
    return uow.categorias.list(
        skip=skip, limit=limit, nombre=nombre, incluir_eliminados=incluir_eliminados
    )


def get_categoria(uow: UnitOfWork, categoria_id: int) -> Categoria | None:
    return uow.categorias.get(categoria_id)


def _validate_parent(
    uow: UnitOfWork, parent_id: int | None, *, self_id: int | None = None
) -> None:
    if parent_id is None:
        return
    if self_id is not None and parent_id == self_id:
        raise ValueError("Una categoria no puede ser su propia padre")
    if uow.categorias.get(parent_id) is None:
        raise ValueError(f"Categoria padre {parent_id} no existe o está inactiva")


def create_categoria(uow: UnitOfWork, data: CategoriaCreate) -> Categoria:
    _validate_parent(uow, data.parent_id)
    return uow.categorias.save(Categoria(**data.model_dump()))


def update_categoria(
    uow: UnitOfWork, categoria_id: int, data: CategoriaUpdate
) -> Categoria | None:
    categoria = uow.categorias.get(categoria_id)
    if categoria is None:
        return None
    payload = data.model_dump(exclude_unset=True)
    if "parent_id" in payload:
        _validate_parent(uow, payload["parent_id"], self_id=categoria_id)
    for field, value in payload.items():
        setattr(categoria, field, value)
    return uow.categorias.save(categoria)


def delete_categoria(uow: UnitOfWork, categoria_id: int) -> bool:
    return uow.categorias.soft_delete(categoria_id)
