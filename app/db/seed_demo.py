"""Seed de datos de prueba: 3 productos con sus ingredientes, stock y categoría.

Idempotente: se puede correr varias veces sin duplicar (busca por nombre).
Requiere que las unidades de medida ya estén seedeadas (run_seed / lifespan).

Uso:  .venv/bin/python3.13 -m app.db.seed_demo
"""
from decimal import Decimal

from sqlmodel import Session, select

from app.core.database import engine
from app.modules.categoria.model import Categoria
from app.modules.ingrediente.model import Ingrediente
from app.modules.producto.model import Producto
from app.modules.producto.link_models import ProductoCategoria, ProductoIngrediente
from app.modules.unidad_medida.model import UnidadMedida


# --- helpers get-or-create (idempotencia) -----------------------------------

def _get_unidad(session: Session, simbolo: str) -> UnidadMedida:
    unidad = session.exec(
        select(UnidadMedida).where(UnidadMedida.simbolo == simbolo)
    ).first()
    if not unidad:
        raise RuntimeError(
            f"Falta la unidad de medida '{simbolo}'. Corré primero el seed base (run_seed)."
        )
    return unidad


def _get_or_create_categoria(session: Session, nombre: str, descripcion: str) -> Categoria:
    cat = session.exec(select(Categoria).where(Categoria.nombre == nombre)).first()
    if cat:
        return cat
    cat = Categoria(nombre=nombre, descripcion=descripcion)
    session.add(cat)
    session.flush()
    return cat


def _get_or_create_ingrediente(
    session: Session, nombre: str, stock: int, es_alergeno: bool
) -> Ingrediente:
    ing = session.exec(select(Ingrediente).where(Ingrediente.nombre == nombre)).first()
    if ing:
        return ing
    ing = Ingrediente(nombre=nombre, stock_cantidad=stock, es_alergeno=es_alergeno)
    session.add(ing)
    session.flush()
    return ing


# --- definición de los 3 productos ------------------------------------------
# Cada ingrediente: (nombre, stock_propio, es_alergeno, cantidad, simbolo_unidad, es_removible)
PRODUCTOS = [
    {
        "nombre": "Hamburguesa Clásica",
        "descripcion": "Medallón de carne, queso cheddar y vegetales en pan de papa.",
        "precio_base": Decimal("5500.00"),
        "stock": 50,
        "unidad_venta": "ud",
        "categoria": "Hamburguesas",
        "imagen": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",
        "ingredientes": [
            ("Pan de papa",        200, True,  1,   "ud", False),
            ("Medallón de carne",  150, False, 150, "g",  False),
            ("Queso cheddar",      180, True,  40,  "g",  True),
            ("Lechuga",            120, False, 20,  "g",  True),
            ("Tomate",             120, False, 30,  "g",  True),
        ],
    },
    {
        "nombre": "Pizza Muzzarella",
        "descripcion": "Pizza a la piedra con salsa de tomate, muzzarella y orégano.",
        "precio_base": Decimal("8000.00"),
        "stock": 30,
        "unidad_venta": "ud",
        "categoria": "Pizzas",
        "imagen": "https://images.unsplash.com/photo-1513104890138-7c749659a591",
        "ingredientes": [
            ("Masa de pizza",     80,  True,  1,   "ud", False),
            ("Salsa de tomate",   100, False, 100, "g",  False),
            ("Muzzarella",        90,  True,  200, "g",  False),
            ("Aceitunas",         60,  False, 30,  "g",  True),
            ("Orégano",           50,  False, 5,   "g",  True),
        ],
    },
    {
        "nombre": "Limonada Natural",
        "descripcion": "Limonada exprimida al momento con menta fresca.",
        "precio_base": Decimal("2500.00"),
        "stock": 100,
        "unidad_venta": "ud",
        "categoria": "Bebidas",
        "imagen": "https://images.unsplash.com/photo-1621263764928-df1444c5e859",
        "ingredientes": [
            ("Limón",  300, False, 3,   "ud", False),
            ("Agua",   500, False, 500, "ml", False),
            ("Azúcar", 400, False, 50,  "g",  True),
            ("Menta",  40,  False, 5,   "g",  True),
        ],
    },
]

CATEGORIAS_DESC = {
    "Hamburguesas": "Hamburguesas artesanales.",
    "Pizzas": "Pizzas a la piedra.",
    "Bebidas": "Bebidas frías y naturales.",
}


def seed_demo(session: Session) -> None:
    for data in PRODUCTOS:
        # Idempotencia: si el producto ya existe (por nombre, no borrado), se omite.
        existing = session.exec(
            select(Producto).where(
                Producto.nombre == data["nombre"],
                Producto.deleted_at.is_(None),
            )
        ).first()
        if existing:
            print(f"• '{data['nombre']}' ya existe (id={existing.id}), se omite.")
            continue

        categoria = _get_or_create_categoria(
            session, data["categoria"], CATEGORIAS_DESC[data["categoria"]]
        )
        unidad_venta = _get_unidad(session, data["unidad_venta"])

        producto = Producto(
            nombre=data["nombre"],
            descripcion=data["descripcion"],
            precio_base=data["precio_base"],
            stock_cantidad=data["stock"],
            disponible=True,
            imagenes_url=[data["imagen"]],
            unidad_venta_id=unidad_venta.id,
        )
        session.add(producto)
        session.flush()  # asigna producto.id

        # Categoría principal
        session.add(
            ProductoCategoria(
                producto_id=producto.id,
                categoria_id=categoria.id,
                es_principal=True,
            )
        )

        # Ingredientes + stock propio + asociación con cantidad/unidad
        for nombre, stock, alergeno, cantidad, simbolo, removible in data["ingredientes"]:
            ingrediente = _get_or_create_ingrediente(session, nombre, stock, alergeno)
            unidad = _get_unidad(session, simbolo)
            session.add(
                ProductoIngrediente(
                    producto_id=producto.id,
                    ingrediente_id=ingrediente.id,
                    es_removible=removible,
                    unidad_medida_id=unidad.id,
                    cantidad=float(cantidad),
                )
            )

        print(f"✓ '{producto.nombre}' creado (id={producto.id}, stock={producto.stock_cantidad}).")

    session.flush()


if __name__ == "__main__":
    with Session(engine) as session:
        seed_demo(session)
        session.commit()
    print("✓ Seed de productos de prueba completado.")
