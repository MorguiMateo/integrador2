from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.uow import UnitOfWork
from app.modules.ingrediente import service
from app.modules.ingrediente.schema import (
    IngredienteCreate,
    IngredienteRead,
    IngredienteUpdate,
)

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])


@router.get("", response_model=list[IngredienteRead])
def listar_ingredientes(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,
    nombre: Annotated[
        str | None, Query(max_length=100, description="Filtro parcial por nombre")
    ] = None,
    es_alergeno: Annotated[
        bool | None, Query(description="Filtrar por alérgeno")
    ] = None,
):
    with UnitOfWork() as uow:
        return service.list_ingredientes(
            uow, skip=skip, limit=limit, nombre=nombre, es_alergeno=es_alergeno
        )


@router.get("/{ingrediente_id}", response_model=IngredienteRead)
def obtener_ingrediente(
    ingrediente_id: Annotated[int, Path(ge=1)],
):
    with UnitOfWork() as uow:
        ingrediente = service.get_ingrediente(uow, ingrediente_id)
        if ingrediente is None:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return ingrediente


@router.post("", response_model=IngredienteRead, status_code=status.HTTP_201_CREATED)
def crear_ingrediente(payload: IngredienteCreate):
    try:
        with UnitOfWork() as uow:
            return service.create_ingrediente(uow, payload)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Ya existe un ingrediente con ese nombre"
        )


@router.put("/{ingrediente_id}", response_model=IngredienteRead)
def actualizar_ingrediente(
    ingrediente_id: Annotated[int, Path(ge=1)],
    payload: IngredienteUpdate,
):
    try:
        with UnitOfWork() as uow:
            ingrediente = service.update_ingrediente(uow, ingrediente_id, payload)
            if ingrediente is None:
                raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
            return ingrediente
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Ya existe un ingrediente con ese nombre"
        )


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ingrediente(
    ingrediente_id: Annotated[int, Path(ge=1)],
):
    # Soft-delete: marca deleted_at en lugar de borrar la fila; así no rompe
    # los links N:N con productos existentes.
    with UnitOfWork() as uow:
        if not service.delete_ingrediente(uow, ingrediente_id):
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
