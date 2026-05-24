from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Optional

from fastapi import APIRouter, Path, Query, status

from app.modules.producto import service
from app.modules.producto.schema import ProductoCreate, ProductoRead, ProductoUpdate

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("", response_model=list[ProductoRead])
def listar_productos(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,
    q: Annotated[Optional[str], Query(max_length=150, description="Filtro parcial por nombre")] = None,
    disponible: Annotated[Optional[bool], Query(description="Filtrar por disponibilidad")] = None,
    precio_min: Annotated[Optional[Decimal], Query(ge=0, description="Precio mínimo inclusivo")] = None,
    precio_max: Annotated[Optional[Decimal], Query(ge=0, description="Precio máximo inclusivo")] = None,
    incluir_eliminados: Annotated[bool, Query(description="Si true, incluye productos con soft-delete")] = False,
) -> list[ProductoRead]:
    return service.list_productos(
        skip=skip, limit=limit, q=q, disponible=disponible,
        precio_min=precio_min, precio_max=precio_max, incluir_eliminados=incluir_eliminados,
    )


@router.get("/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: Annotated[int, Path(ge=1)]) -> ProductoRead:
    return service.get_producto(producto_id)


@router.post("", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(payload: ProductoCreate) -> ProductoRead:
    return service.create_producto(payload)


@router.put("/{producto_id}", response_model=ProductoRead)
def actualizar_producto(producto_id: Annotated[int, Path(ge=1)], payload: ProductoUpdate) -> ProductoRead:
    return service.update_producto(producto_id, payload)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: Annotated[int, Path(ge=1)]) -> None:
    service.delete_producto(producto_id)
