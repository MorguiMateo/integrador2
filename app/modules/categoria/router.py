from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Path, Query, status

from app.modules.categoria import service
from app.modules.categoria.schema import CategoriaCreate, CategoriaRead, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaRead])
def listar_categorias(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,
    nombre: Annotated[Optional[str], Query(max_length=100, description="Filtro parcial por nombre")] = None,
    incluir_eliminados: Annotated[bool, Query(description="Si true, incluye filas con soft-delete")] = False,
) -> list[CategoriaRead]:
    return service.list_categorias(skip=skip, limit=limit, nombre=nombre, incluir_eliminados=incluir_eliminados)


@router.get("/{categoria_id}", response_model=CategoriaRead)
def obtener_categoria(categoria_id: Annotated[int, Path(ge=1)]) -> CategoriaRead:
    return service.get_categoria(categoria_id)


@router.post("", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear_categoria(payload: CategoriaCreate) -> CategoriaRead:
    return service.create_categoria(payload)


@router.put("/{categoria_id}", response_model=CategoriaRead)
def actualizar_categoria(categoria_id: Annotated[int, Path(ge=1)], payload: CategoriaUpdate) -> CategoriaRead:
    return service.update_categoria(categoria_id, payload)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: Annotated[int, Path(ge=1)]) -> None:
    service.delete_categoria(categoria_id)
