from __future__ import annotations
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.core.uow import UnitOfWork
from app.modules.ingrediente.model import Ingrediente
from app.modules.ingrediente.schema import IngredienteCreate, IngredienteRead, IngredienteUpdate

##llama al list del repository y convierte cada objeto ingrediente a schema IngredienteRead con model_validate. 
## devuelve una lista lista para transformar a json. 
def list_ingredientes(*, skip: int = 0, limit: int = 50, nombre: Optional[str] = None, es_alergeno: Optional[bool] = None) -> list[IngredienteRead]:
    with UnitOfWork() as uow:
        ingredientes = uow.ingredientes.list(skip=skip, limit=limit, nombre=nombre, es_alergeno=es_alergeno)
        return [IngredienteRead.model_validate(i) for i in ingredientes]

##Busca por id. si el repository devuelve none, lanza 404. si existe lo convierte a schema.
def get_ingrediente(ingrediente_id: int) -> IngredienteRead:
    with UnitOfWork() as uow:
        ingrediente = uow.ingredientes.get(ingrediente_id)
        if ingrediente is None:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return IngredienteRead.model_validate(ingrediente)

##data.model_dump convierte el schema IngredienteCreate a diccionario.
##ingrediente (**...) crea el objeto ORM(objeto definido en la base de datos)
##save() lo persiste en la base. si la base lanza error de nombre duplicado, atrapa el error y lo convierte en un 409 para que sea facil de leer
def create_ingrediente(data: IngredienteCreate) -> IngredienteRead:
    try:
        with UnitOfWork() as uow:
            ingrediente = uow.ingredientes.save(Ingrediente(**data.model_dump()))
            return IngredienteRead.model_validate(ingrediente)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe un ingrediente con ese nombre")

##exclude_upset = true itera los campos que el cliente realmente mando, no todos. si mando solo el nombre sin aclarar es_alergeno
## ese campo no se pisa y luego setattr actualiza cada campo y save lo persiste. tambien atrapa el integrityError y lo transforma en 409
def update_ingrediente(ingrediente_id: int, data: IngredienteUpdate) -> IngredienteRead:
    try:
        with UnitOfWork() as uow:
            ingrediente = uow.ingredientes.get(ingrediente_id)
            if ingrediente is None:
                raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(ingrediente, field, value)
            ingrediente = uow.ingredientes.save(ingrediente)
            return IngredienteRead.model_validate(ingrediente)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe un ingrediente con ese nombre")

##Verifica que el ingrediente exista → 404 si no.
##Verifica que no esté siendo usado por algún producto activo → 409 si está en uso.
##si pasa ambas llamadas al delete real del repository.
def delete_ingrediente(ingrediente_id: int) -> None:
    with UnitOfWork() as uow:
        if uow.ingredientes.get(ingrediente_id) is None:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        if uow.ingredientes.tiene_productos_activos(ingrediente_id):
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar: el ingrediente está en uso por un producto activo.",
            )
        uow.ingredientes.delete(ingrediente_id)
