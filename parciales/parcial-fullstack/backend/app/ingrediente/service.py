from typing import List, Optional

from sqlmodel import Session, select

from .model import Ingrediente
from .schema import IngredienteCreate, IngredienteUpdate


def crear(session: Session, data: IngredienteCreate) -> Ingrediente:
    nuevo = Ingrediente(**data.model_dump())
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


def obtener_todos(
    session: Session,
    skip: int = 0,
    limit: int = 20,
    q: Optional[str] = None,
    es_alergeno: Optional[bool] = None,
) -> List[Ingrediente]:
    statement = select(Ingrediente)
    if q:
        like = f"%{q.lower()}%"
        statement = statement.where(Ingrediente.nombre.ilike(like))
    if es_alergeno is not None:
        statement = statement.where(Ingrediente.es_alergeno == es_alergeno)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def obtener_por_id(session: Session, id: int) -> Optional[Ingrediente]:
    return session.get(Ingrediente, id)


def obtener_por_nombre(session: Session, nombre: str) -> Optional[Ingrediente]:
    return session.exec(
        select(Ingrediente).where(Ingrediente.nombre == nombre)
    ).first()


def actualizar(
    session: Session, id: int, data: IngredienteUpdate
) -> Optional[Ingrediente]:
    ingrediente = session.get(Ingrediente, id)
    if not ingrediente:
        return None
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(ingrediente, campo, valor)
    session.add(ingrediente)
    session.commit()
    session.refresh(ingrediente)
    return ingrediente


def eliminar(session: Session, id: int) -> bool:
    ingrediente = session.get(Ingrediente, id)
    if not ingrediente:
        return False
    session.delete(ingrediente)
    session.commit()
    return True
