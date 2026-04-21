from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from app.core.database import get_session

from . import schema, service

router = APIRouter(prefix="/categorias", tags=["Categorías"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post(
    "/", response_model=schema.CategoriaRead, status_code=status.HTTP_201_CREATED
)
def alta_categoria(data: schema.CategoriaCreate, session: SessionDep):
    if service.obtener_por_codigo(session, data.codigo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una categoría con el código '{data.codigo}'",
        )
    return service.crear(session, data)


@router.get("/", response_model=List[schema.CategoriaRead])
def listar_categorias(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    q: Annotated[Optional[str], Query(min_length=1, max_length=60)] = None,
    activo: Annotated[Optional[bool], Query()] = None,
):
    return service.obtener_todas(session, skip, limit, q, activo)


@router.get("/{id}", response_model=schema.CategoriaRead)
def detalle_categoria(
    session: SessionDep,
    id: Annotated[int, Path(gt=0)],
):
    categoria = service.obtener_por_id(session, id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    return categoria


@router.put("/{id}", response_model=schema.CategoriaRead)
def actualizar_categoria(
    session: SessionDep,
    data: schema.CategoriaUpdate,
    id: Annotated[int, Path(gt=0)],
):
    actualizada = service.actualizar(session, id, data)
    if not actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    return actualizada


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    session: SessionDep,
    id: Annotated[int, Path(gt=0)],
):
    if not service.eliminar(session, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
