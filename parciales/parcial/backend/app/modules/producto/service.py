from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.uow import UnitOfWork
from app.modules.categoria.model import Categoria
from app.modules.ingrediente.model import Ingrediente
from app.modules.producto.link_models import ProductoCategoria, ProductoIngrediente
from app.modules.producto.model import Producto
from app.modules.producto.schema import (
    ProductoCategoriaCreate,
    ProductoCreate,
    ProductoIngredienteCreate,
    ProductoUpdate,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _base_query():
    return (
        select(Producto)
        .where(Producto.deleted_at == None)  # noqa: E711
        .options(
            selectinload(Producto.categoria_links).selectinload(
                ProductoCategoria.categoria
            ),
            selectinload(Producto.ingrediente_links).selectinload(
                ProductoIngrediente.ingrediente
            ),
        )
    )


def _to_read_dict(producto: Producto) -> dict:
    categorias = [
        {"categoria": link.categoria, "es_principal": link.es_principal}
        for link in producto.categoria_links
        if link.categoria.deleted_at is None
    ]
    ingredientes = [
        {"ingrediente": link.ingrediente, "es_removible": link.es_removible}
        for link in producto.ingrediente_links
        if link.ingrediente.deleted_at is None
    ]
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio_base": producto.precio_base,
        "imagenes_url": producto.imagenes_url,
        "stock_cantidad": producto.stock_cantidad,
        "disponible": producto.disponible,
        "created_at": producto.created_at,
        "updated_at": producto.updated_at,
        "categorias": categorias,
        "ingredientes": ingredientes,
    }


def list_productos(
    uow: UnitOfWork,
    *,
    skip: int = 0,
    limit: int = 50,
    q: str | None = None,
    disponible: bool | None = None,
    precio_min: Decimal | None = None,
    precio_max: Decimal | None = None,
) -> list[dict]:
    stmt = _base_query()
    if q:
        stmt = stmt.where(Producto.nombre.ilike(f"%{q}%"))
    if disponible is not None:
        stmt = stmt.where(Producto.disponible == disponible)
    if precio_min is not None:
        stmt = stmt.where(Producto.precio_base >= precio_min)
    if precio_max is not None:
        stmt = stmt.where(Producto.precio_base <= precio_max)
    stmt = stmt.offset(skip).limit(limit).order_by(Producto.id)
    productos = uow.session.exec(stmt).all()
    return [_to_read_dict(p) for p in productos]


def get_producto(uow: UnitOfWork, producto_id: int) -> dict | None:
    stmt = _base_query().where(Producto.id == producto_id)
    producto = uow.session.exec(stmt).first()
    if producto is None:
        return None
    return _to_read_dict(producto)


def _validate_categorias(
    uow: UnitOfWork, items: list[ProductoCategoriaCreate]
) -> None:
    if not items:
        return
    ids = [i.categoria_id for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Categorias duplicadas en el payload")
    principales = sum(1 for i in items if i.es_principal)
    if principales > 1:
        raise ValueError("Solo una categoria puede ser principal por producto")
    stmt = select(Categoria.id).where(
        Categoria.id.in_(ids),
        Categoria.deleted_at == None,  # noqa: E711
    )
    found = set(uow.session.exec(stmt).all())
    missing = set(ids) - found
    if missing:
        raise ValueError(f"Categorias no encontradas o inactivas: {sorted(missing)}")


def _validate_ingredientes(
    uow: UnitOfWork, items: list[ProductoIngredienteCreate]
) -> None:
    if not items:
        return
    ids = [i.ingrediente_id for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Ingredientes duplicados en el payload")
    stmt = select(Ingrediente.id).where(
        Ingrediente.id.in_(ids),
        Ingrediente.deleted_at == None,  # noqa: E711
    )
    found = set(uow.session.exec(stmt).all())
    missing = set(ids) - found
    if missing:
        raise ValueError(f"Ingredientes no encontrados o inactivos: {sorted(missing)}")


def _sync_categoria_links(
    uow: UnitOfWork, producto_id: int, desired: list[ProductoCategoriaCreate]
) -> None:
    _validate_categorias(uow, desired)
    desired_by_cat: dict[int, ProductoCategoriaCreate] = {
        item.categoria_id: item for item in desired
    }

    existing = uow.session.exec(
        select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id
        )
    ).all()
    existing_by_cat: dict[int, ProductoCategoria] = {
        link.categoria_id: link for link in existing
    }

    for cat_id, item in desired_by_cat.items():
        link = existing_by_cat.get(cat_id)
        if link is None:
            uow.session.add(
                ProductoCategoria(
                    producto_id=producto_id,
                    categoria_id=cat_id,
                    es_principal=item.es_principal,
                )
            )
        else:
            link.es_principal = item.es_principal
            uow.session.add(link)

    for cat_id, link in existing_by_cat.items():
        if cat_id not in desired_by_cat:
            uow.session.delete(link)


def _sync_ingrediente_links(
    uow: UnitOfWork, producto_id: int, desired: list[ProductoIngredienteCreate]
) -> None:
    _validate_ingredientes(uow, desired)
    desired_by_ing: dict[int, ProductoIngredienteCreate] = {
        item.ingrediente_id: item for item in desired
    }

    existing = uow.session.exec(
        select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id
        )
    ).all()
    existing_by_ing: dict[int, ProductoIngrediente] = {
        link.ingrediente_id: link for link in existing
    }

    for ing_id, item in desired_by_ing.items():
        link = existing_by_ing.get(ing_id)
        if link is None:
            uow.session.add(
                ProductoIngrediente(
                    producto_id=producto_id,
                    ingrediente_id=ing_id,
                    es_removible=item.es_removible,
                )
            )
        else:
            link.es_removible = item.es_removible
            uow.session.add(link)

    for ing_id, link in existing_by_ing.items():
        if ing_id not in desired_by_ing:
            uow.session.delete(link)


def create_producto(uow: UnitOfWork, data: ProductoCreate) -> dict:
    _validate_categorias(uow, data.categorias)
    _validate_ingredientes(uow, data.ingredientes)

    producto = Producto(
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio_base=data.precio_base,
        imagenes_url=list(data.imagenes_url),
        stock_cantidad=data.stock_cantidad,
        disponible=data.disponible,
    )
    uow.session.add(producto)
    uow.session.flush()

    for item in data.categorias:
        uow.session.add(
            ProductoCategoria(
                producto_id=producto.id,
                categoria_id=item.categoria_id,
                es_principal=item.es_principal,
            )
        )

    for item in data.ingredientes:
        uow.session.add(
            ProductoIngrediente(
                producto_id=producto.id,
                ingrediente_id=item.ingrediente_id,
                es_removible=item.es_removible,
            )
        )

    uow.session.flush()
    reloaded = get_producto(uow, producto.id)
    assert reloaded is not None
    return reloaded


def update_producto(
    uow: UnitOfWork, producto_id: int, data: ProductoUpdate
) -> dict | None:
    producto = uow.session.get(Producto, producto_id)
    if producto is None or producto.deleted_at is not None:
        return None

    scalar_fields = data.model_dump(
        exclude_unset=True, exclude={"categorias", "ingredientes"}
    )
    for field, value in scalar_fields.items():
        setattr(producto, field, value)

    if data.categorias is not None:
        _sync_categoria_links(uow, producto_id, data.categorias)

    if data.ingredientes is not None:
        _sync_ingrediente_links(uow, producto_id, data.ingredientes)

    uow.session.add(producto)
    uow.session.flush()
    return get_producto(uow, producto_id)


def delete_producto(uow: UnitOfWork, producto_id: int) -> bool:
    producto = uow.session.get(Producto, producto_id)
    if producto is None or producto.deleted_at is not None:
        return False

    producto.deleted_at = _now()
    uow.session.add(producto)
    uow.session.flush()
    return True
