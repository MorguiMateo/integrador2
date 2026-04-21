from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from app.core.database import get_session

from . import schema, service

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post(
    "/", response_model=schema.IngredienteRead, status_code=status.HTTP_201_CREATED
)
def alta_ingrediente(data: schema.IngredienteCreate, session: SessionDep):
    if service.obtener_por_nombre(session, data.nombre):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un ingrediente con el nombre '{data.nombre}'",
        )
    return service.crear(session, data)


@router.get("/", response_model=List[schema.IngredienteRead])
def listar_ingredientes(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    q: Annotated[Optional[str], Query(min_length=1, max_length=60)] = None,
    es_alergeno: Annotated[Optional[bool], Query()] = None,
):
    return service.obtener_todos(session, skip, limit, q, es_alergeno)


@router.get("/{id}", response_model=schema.IngredienteRead)
def detalle_ingrediente(
    session: SessionDep,
    id: Annotated[int, Path(gt=0)],
):
    ingrediente = service.obtener_por_id(session, id)
    if not ingrediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente no encontrado",
        )
    return ingrediente


@router.put("/{id}", response_model=schema.IngredienteRead)
def actualizar_ingrediente(
    session: SessionDep,
    data: schema.IngredienteUpdate,
    id: Annotated[int, Path(gt=0)],
):
    actualizado = service.actualizar(session, id, data)
    if not actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente no encontrado",
        )
    return actualizado


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ingrediente(
    session: SessionDep,
    id: Annotated[int, Path(gt=0)],
):
    if not service.eliminar(session, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente no encontrado",
        )
