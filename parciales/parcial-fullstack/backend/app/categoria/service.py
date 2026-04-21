from typing import List, Optional

from sqlmodel import Session, select

from .model import Categoria
from .schema import CategoriaCreate, CategoriaUpdate


def crear(session: Session, data: CategoriaCreate) -> Categoria:
    nueva = Categoria(**data.model_dump())
    session.add(nueva)
    session.commit()
    session.refresh(nueva)
    return nueva


def obtener_todas(
    session: Session,
    skip: int = 0,
    limit: int = 20,
    q: Optional[str] = None,
    activo: Optional[bool] = None,
) -> List[Categoria]:
    statement = select(Categoria)
    if q:
        like = f"%{q.lower()}%"
        statement = statement.where(
            (Categoria.codigo.ilike(like)) | (Categoria.descripcion.ilike(like))
        )
    if activo is not None:
        statement = statement.where(Categoria.activo == activo)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def obtener_por_id(session: Session, id: int) -> Optional[Categoria]:
    return session.get(Categoria, id)


def obtener_por_codigo(session: Session, codigo: str) -> Optional[Categoria]:
    return session.exec(select(Categoria).where(Categoria.codigo == codigo)).first()


def actualizar(
    session: Session, id: int, data: CategoriaUpdate
) -> Optional[Categoria]:
    categoria = session.get(Categoria, id)
    if not categoria:
        return None
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(categoria, campo, valor)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


def eliminar(session: Session, id: int) -> bool:
    categoria = session.get(Categoria, id)
    if not categoria:
        return False
    session.delete(categoria)
    session.commit()
    return True
