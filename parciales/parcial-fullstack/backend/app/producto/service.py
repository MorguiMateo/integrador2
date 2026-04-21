from typing import List, Optional

from sqlmodel import Session, select

from app.categoria.model import Categoria
from app.core.uow import UnitOfWork
from app.ingrediente.model import Ingrediente

from .link_models import ProductoIngrediente
from .model import Producto
from .schema import ProductoCreate, ProductoUpdate


def _cargar_categorias(session: Session, ids: List[int]) -> List[Categoria]:
    if not ids:
        return []
    categorias = session.exec(
        select(Categoria).where(Categoria.id.in_(ids))
    ).all()
    if len(categorias) != len(set(ids)):
        encontradas = {c.id for c in categorias}
        faltantes = [i for i in ids if i not in encontradas]
        raise ValueError(f"Categorías no encontradas: {faltantes}")
    return list(categorias)


def _validar_ingredientes(session: Session, ids: List[int]) -> None:
    if not ids:
        return
    encontrados = session.exec(
        select(Ingrediente.id).where(Ingrediente.id.in_(ids))
    ).all()
    faltantes = set(ids) - set(encontrados)
    if faltantes:
        raise ValueError(f"Ingredientes no encontrados: {sorted(faltantes)}")


def crear(data: ProductoCreate) -> Producto:
    """Alta de producto dentro de una Unit of Work.

    Se crea el producto, se enlazan categorías (N:N) y se agregan
    los ingredientes con su cantidad y unidad (1:N vía ProductoIngrediente).
    """
    with UnitOfWork() as uow:
        _validar_ingredientes(uow.session, [i.ingrediente_id for i in data.ingredientes])
        categorias = _cargar_categorias(uow.session, data.categoria_ids)

        producto = Producto(
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio=data.precio,
            stock=data.stock,
            activo=data.activo,
            categorias=categorias,
        )
        uow.session.add(producto)
        uow.session.flush()

        for item in data.ingredientes:
            uow.session.add(
                ProductoIngrediente(
                    producto_id=producto.id,
                    ingrediente_id=item.ingrediente_id,
                    cantidad=item.cantidad,
                    unidad=item.unidad,
                )
            )

        uow.commit()
        uow.session.refresh(producto)
        _ = producto.categorias
        _ = [(pi.ingrediente, pi.cantidad, pi.unidad) for pi in producto.ingredientes_link]
        return producto


def obtener_todos(
    session: Session,
    skip: int = 0,
    limit: int = 20,
    q: Optional[str] = None,
    activo: Optional[bool] = None,
    precio_min: Optional[float] = None,
    precio_max: Optional[float] = None,
) -> List[Producto]:
    statement = select(Producto)
    if q:
        like = f"%{q.lower()}%"
        statement = statement.where(Producto.nombre.ilike(like))
    if activo is not None:
        statement = statement.where(Producto.activo == activo)
    if precio_min is not None:
        statement = statement.where(Producto.precio >= precio_min)
    if precio_max is not None:
        statement = statement.where(Producto.precio <= precio_max)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def obtener_por_id(session: Session, id: int) -> Optional[Producto]:
    return session.get(Producto, id)


def actualizar(id: int, data: ProductoUpdate) -> Optional[Producto]:
    with UnitOfWork() as uow:
        producto = uow.session.get(Producto, id)
        if not producto:
            return None

        payload = data.model_dump(exclude_unset=True)

        for campo in ("nombre", "descripcion", "precio", "stock", "activo"):
            if campo in payload:
                setattr(producto, campo, payload[campo])

        if "categoria_ids" in payload and payload["categoria_ids"] is not None:
            producto.categorias = _cargar_categorias(
                uow.session, payload["categoria_ids"]
            )

        if "ingredientes" in payload and payload["ingredientes"] is not None:
            _validar_ingredientes(
                uow.session, [i["ingrediente_id"] for i in payload["ingredientes"]]
            )
            producto.ingredientes_link.clear()
            uow.session.flush()
            for item in payload["ingredientes"]:
                uow.session.add(
                    ProductoIngrediente(
                        producto_id=producto.id,
                        ingrediente_id=item["ingrediente_id"],
                        cantidad=item["cantidad"],
                        unidad=item["unidad"],
                    )
                )

        uow.session.add(producto)
        uow.commit()
        uow.session.refresh(producto)
        _ = producto.categorias
        _ = [(pi.ingrediente, pi.cantidad, pi.unidad) for pi in producto.ingredientes_link]
        return producto


def eliminar(session: Session, id: int) -> bool:
    producto = session.get(Producto, id)
    if not producto:
        return False
    session.delete(producto)
    session.commit()
    return True


def construir_read(producto: Producto) -> dict:
    """Arma el diccionario con la forma que espera ProductoRead.

    Mezcla la relación N:N de categorías y el objeto de asociación de ingredientes.
    """
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": producto.precio,
        "stock": producto.stock,
        "activo": producto.activo,
        "categorias": producto.categorias,
        "ingredientes": [
            {
                "cantidad": pi.cantidad,
                "unidad": pi.unidad,
                "ingrediente": pi.ingrediente,
            }
            for pi in producto.ingredientes_link
        ],
    }
