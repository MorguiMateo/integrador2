from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, status

from app.modules.auth.dependencies import require_admin, require_admin_or_stock
from app.modules.ingrediente import service
from app.modules.ingrediente.schema import (
    IngredienteCreate,
    IngredienteRead,
    IngredienteUpdate,
)

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])

##router hace llamada a service y service a repositorio que conecta con la base de datos.  
@router.get("", response_model=list[IngredienteRead])
def listar_ingredientes(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,
    nombre: Annotated[Optional[str], Query(max_length=100, description="Filtro parcial por nombre")] = None,
    es_alergeno: Annotated[Optional[bool], Query(description="Filtrar por alérgeno")] = None,
) -> list[IngredienteRead]:
    return service.list_ingredientes(
        skip=skip,
        limit=limit,
        nombre=nombre,
        es_alergeno=es_alergeno,
    )

## por path recibe id y filtra  y se valida que este sea un entero positivo
@router.get("/{ingrediente_id}", response_model=IngredienteRead)
def obtener_ingrediente(ingrediente_id: Annotated[int, Path(ge=1)]) -> IngredienteRead:
    return service.get_ingrediente(ingrediente_id)

## lee el body json y lo valida con schema.
## Responde con 201 created en vez del 200 por default

@router.post(
    "",
    response_model=IngredienteRead,
    status_code=status.HTTP_201_CREATED,
    ## Antes de ejecutar la funcion corre require_admin. si el usuario no es admin corta con 401/403 sin llegar al service.
    dependencies=[Depends(require_admin)],
)
def crear_ingrediente(payload: IngredienteCreate) -> IngredienteRead:
    return service.create_ingrediente(payload)

## combina path param ingrediente_id con body JSON ingredienteUpdate. FastAPI sabe distinguilos automaticamente(el pathurl y el body json)
@router.put(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    # STOCK puede editar ingredientes (p.ej. ajustar stock); crear/eliminar siguen siendo ADMIN.
    dependencies=[Depends(require_admin_or_stock)],
)
def actualizar_ingrediente(
    ingrediente_id: Annotated[int, Path(ge=1)],
    payload: IngredienteUpdate,
) -> IngredienteRead:
    return service.update_ingrediente(ingrediente_id, payload)

##Responde sin body(no content) (204).
##Devuelve None porque 204 no tiene cuerpo de respuesta.

@router.delete(
    "/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def eliminar_ingrediente(ingrediente_id: Annotated[int, Path(ge=1)]) -> None:
    service.delete_ingrediente(ingrediente_id)
