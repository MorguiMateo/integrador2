from __future__ import annotations

from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.uow import UnitOfWork
from app.modules.categoria.model import Categoria
from app.modules.categoria.schema import CategoriaCreate, CategoriaRead, CategoriaUpdate


def list_categorias(*, skip: int = 0, limit: int = 50, nombre: Optional[str] = None, incluir_eliminados: bool = False) -> list[CategoriaRead]:
    with UnitOfWork() as uow:
        categorias = uow.categorias.list(skip=skip, limit=limit, nombre=nombre, incluir_eliminados=incluir_eliminados)
        return [CategoriaRead.model_validate(c) for c in categorias]


def get_categoria(categoria_id: int) -> CategoriaRead:
    with UnitOfWork() as uow:
        categoria = uow.categorias.get(categoria_id)
        if categoria is None:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        return CategoriaRead.model_validate(categoria)


def _validate_parent(uow, parent_id: Optional[int], *, self_id: Optional[int] = None) -> None:
    if parent_id is None:
        return
    if self_id is not None and parent_id == self_id:
        raise ValueError("Una categoria no puede ser su propia padre")
    if uow.categorias.get(parent_id) is None:
        raise ValueError(f"Categoria padre {parent_id} no existe o está inactiva")


def create_categoria(data: CategoriaCreate) -> CategoriaRead:
    try:
        with UnitOfWork() as uow:
            _validate_parent(uow, data.parent_id)
            categoria = uow.categorias.save(Categoria(**data.model_dump()))
            return CategoriaRead.model_validate(categoria)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe una categoria con ese nombre")


def update_categoria(categoria_id: int, data: CategoriaUpdate) -> CategoriaRead:
    try:
        with UnitOfWork() as uow:
            categoria = uow.categorias.get(categoria_id)
            if categoria is None:
                raise HTTPException(status_code=404, detail="Categoria no encontrada")
            payload = data.model_dump(exclude_unset=True)
            if "parent_id" in payload:
                _validate_parent(uow, payload["parent_id"], self_id=categoria_id)
            for field, value in payload.items():
                setattr(categoria, field, value)
            categoria = uow.categorias.save(categoria)
            return CategoriaRead.model_validate(categoria)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe una categoria con ese nombre")


def delete_categoria(categoria_id: int) -> None:
    with UnitOfWork() as uow:
        if not uow.categorias.soft_delete(categoria_id):
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
