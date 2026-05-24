from __future__ import annotations
from typing import Annotated, Optional
from fastapi import APIRouter, Path, Query, status
from app.modules.ingrediente import service
from app.modules.ingrediente.schema import IngredienteCreate, IngredienteRead, IngredienteUpdate

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])


@router.get("", response_model=list[IngredienteRead])
def listar_ingredientes(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,
    nombre: Annotated[Optional[str], Query(max_length=100, description="Filtro parcial por nombre")] = None,
    es_alergeno: Annotated[Optional[bool], Query(description="Filtrar por alérgeno")] = None,
) -> list[IngredienteRead]:
    return service.list_ingredientes(skip=skip, limit=limit, nombre=nombre, es_alergeno=es_alergeno)


@router.get("/{ingrediente_id}", response_model=IngredienteRead)
def obtener_ingrediente(ingrediente_id: Annotated[int, Path(ge=1)]) -> IngredienteRead:
    return service.get_ingrediente(ingrediente_id)


@router.post("", response_model=IngredienteRead, status_code=status.HTTP_201_CREATED)
def crear_ingrediente(payload: IngredienteCreate) -> IngredienteRead:
    return service.create_ingrediente(payload)


@router.put("/{ingrediente_id}", response_model=IngredienteRead)
def actualizar_ingrediente(ingrediente_id: Annotated[int, Path(ge=1)], payload: IngredienteUpdate) -> IngredienteRead:
    return service.update_ingrediente(ingrediente_id, payload)


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ingrediente(ingrediente_id: Annotated[int, Path(ge=1)]) -> None:
    service.delete_ingrediente(ingrediente_id)
