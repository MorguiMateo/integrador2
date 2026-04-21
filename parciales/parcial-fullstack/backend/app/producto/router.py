from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from app.core.database import get_session

from . import schema, service

router = APIRouter(prefix="/productos", tags=["Productos"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post(
    "/", response_model=schema.ProductoRead, status_code=status.HTTP_201_CREATED
)
def alta_producto(data: schema.ProductoCreate):
    try:
        producto = service.crear(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return service.construir_read(producto)


@router.get("/", response_model=List[schema.ProductoRead])
def listar_productos(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    q: Annotated[Optional[str], Query(min_length=1, max_length=60)] = None,
    activo: Annotated[Optional[bool], Query()] = None,
    precio_min: Annotated[Optional[float], Query(ge=0)] = None,
    precio_max: Annotated[Optional[float], Query(ge=0)] = None,
):
    productos = service.obtener_todos(
        session, skip, limit, q, activo, precio_min, precio_max
    )
    return [service.construir_read(p) for p in productos]


@router.get("/{id}", response_model=schema.ProductoRead)
def detalle_producto(
    session: SessionDep,
    id: Annotated[int, Path(gt=0)],
):
    producto = service.obtener_por_id(session, id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return service.construir_read(producto)


@router.put("/{id}", response_model=schema.ProductoRead)
def actualizar_producto(
    data: schema.ProductoUpdate,
    id: Annotated[int, Path(gt=0)],
):
    try:
        actualizado = service.actualizar(id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    if not actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return service.construir_read(actualizado)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    session: SessionDep,
    id: Annotated[int, Path(gt=0)],
):
    if not service.eliminar(session, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
