from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.uow import UnitOfWork
from app.modules.producto import service
from app.modules.producto.schema import (
    ProductoCreate,
    ProductoRead,
    ProductoUpdate,
)

router = APIRouter(prefix="/productos", tags=["productos"])

##uow al service
##
##
##

@router.get("", response_model=list[ProductoRead])
def listar_productos(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,
    q: Annotated[
        str | None, Query(max_length=150, description="Filtro parcial por nombre")
    ] = None,
    disponible: Annotated[
        bool | None, Query(description="Filtrar por disponibilidad")
    ] = None,
    precio_min: Annotated[
        Decimal | None, Query(ge=0, description="Precio mínimo inclusivo")
    ] = None,
    precio_max: Annotated[
        Decimal | None, Query(ge=0, description="Precio máximo inclusivo")
    ] = None,
    incluir_eliminados: Annotated[
        bool,
        Query(description="Si true, incluye productos con soft-delete (eliminado=true)"),
    ] = False,
):
    with UnitOfWork() as uow:
        return service.list_productos(
            uow,
            skip=skip,
            limit=limit,
            q=q,
            disponible=disponible,
            precio_min=precio_min,
            precio_max=precio_max,
            incluir_eliminados=incluir_eliminados,
        )


@router.get("/{producto_id}", response_model=ProductoRead)
def obtener_producto(
    producto_id: Annotated[int, Path(ge=1)],
):
    with UnitOfWork() as uow:
        producto = service.get_producto(uow, producto_id)
        if producto is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return producto


@router.post("", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(payload: ProductoCreate):
    try:
        with UnitOfWork() as uow:
            return service.create_producto(uow, payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflicto de datos del producto")


@router.put("/{producto_id}", response_model=ProductoRead)
def actualizar_producto(
    producto_id: Annotated[int, Path(ge=1)],
    payload: ProductoUpdate,
):
    try:
        with UnitOfWork() as uow:
            producto = service.update_producto(uow, producto_id, payload)
            if producto is None:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            return producto
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflicto de datos del producto")


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: Annotated[int, Path(ge=1)],
):
    with UnitOfWork() as uow:
        if not service.delete_producto(uow, producto_id):
            raise HTTPException(status_code=404, detail="Producto no encontrado")
