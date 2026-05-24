from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status

from app.modules.auth.dependencies import require_admin, require_admin_or_stock
from app.modules.producto import service
from app.modules.producto.schema import ProductoCreate, ProductoRead, ProductoUpdate

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("", response_model=list[ProductoRead])
def listar_productos(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,
) -> list[ProductoRead]:
    return service.list_productos(skip=skip, limit=limit)


@router.get("/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: Annotated[int, Path(ge=1)]) -> ProductoRead:
    return service.get_producto(producto_id)


@router.post(
    "",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def crear_producto(payload: ProductoCreate) -> ProductoRead:
    return service.create_producto(payload)


@router.put(
    "/{producto_id}",
    response_model=ProductoRead,
    dependencies=[Depends(require_admin)],
)
def actualizar_producto(
    producto_id: Annotated[int, Path(ge=1)],
    payload: ProductoUpdate,
) -> ProductoRead:
    return service.update_producto(producto_id, payload)


@router.patch(
    "/{producto_id}/disponibilidad",
    response_model=ProductoRead,
    dependencies=[Depends(require_admin_or_stock)],
)
def cambiar_disponibilidad(
    producto_id: Annotated[int, Path(ge=1)],
    disponible: Annotated[bool, Body(embed=True, description="Nuevo valor de disponibilidad")],
) -> ProductoRead:
    return service.set_disponibilidad(producto_id, disponible)


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def eliminar_producto(producto_id: Annotated[int, Path(ge=1)]) -> None:
    service.delete_producto(producto_id)
