from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.uow import UnitOfWork
from app.modules.categoria import service
from app.modules.categoria.schema import (
    CategoriaCreate,
    CategoriaRead,
    CategoriaUpdate,
)

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaRead])
def listar_categorias(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,  # ge=0: no negativos
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,  # le=100: evita traer miles de filas
    nombre: Annotated[
        str | None, Query(max_length=100, description="Filtro parcial por nombre")
    ] = None,
    incluir_eliminados: Annotated[
        bool,
        Query(description="Si true, incluye filas con soft-delete (eliminado=true)"),
    ] = False,
):
    with UnitOfWork() as uow:
        return service.list_categorias(
            uow,
            skip=skip,
            limit=limit,
            nombre=nombre,
            incluir_eliminados=incluir_eliminados,
        )


@router.get("/{categoria_id}", response_model=CategoriaRead)
def obtener_categoria(
    categoria_id: Annotated[int, Path(ge=1)],
):
    with UnitOfWork() as uow:
        categoria = service.get_categoria(uow, categoria_id)
        if categoria is None:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        return categoria


@router.post("", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear_categoria(payload: CategoriaCreate):
    try:
        with UnitOfWork() as uow:
            return service.create_categoria(uow, payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Ya existe una categoria con ese nombre"
        )


@router.put("/{categoria_id}", response_model=CategoriaRead)
def actualizar_categoria(
    categoria_id: Annotated[int, Path(ge=1)],
    payload: CategoriaUpdate,
):
    try:
        with UnitOfWork() as uow:
            categoria = service.update_categoria(uow, categoria_id, payload)
            if categoria is None:
                raise HTTPException(status_code=404, detail="Categoria no encontrada")
            return categoria
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Ya existe una categoria con ese nombre"
        )


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    categoria_id: Annotated[int, Path(ge=1)],
):
    with UnitOfWork() as uow:
        if not service.delete_categoria(uow, categoria_id):
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
