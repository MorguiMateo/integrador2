##  - uow.py — define UnitOfWork, el context manager que abre una sesión de base de datos, instancia todos los repositories, y al salir hace commit si todo fue bien o rollback si hubo error.f
from __future__ import annotations
from types import TracebackType
from typing import Optional, Type
from sqlmodel import Session

from app.core.database import engine
from app.modules.categoria.repository import CategoriaRepository
from app.modules.ingrediente.repository import IngredienteRepository
from app.modules.producto.repository import ProductoRepository
from app.modules.usuario.repository import UsuarioRepository
from app.modules.unidad_medida.repository import UnidadMedidaRepository


class UnitOfWork:
    def __enter__(self) -> "UnitOfWork":
        self.session = Session(engine, expire_on_commit=False)
        self.categorias = CategoriaRepository(self.session)
        self.ingredientes = IngredienteRepository(self.session)
        self.productos = ProductoRepository(self.session)
        self.usuarios = UsuarioRepository(self.session)
        self.unidades_medida = UnidadMedidaRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            self.session.close()
