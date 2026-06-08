from sqlmodel import select

from app.core.repository import BaseRepository
from app.modules.estado_pedido.model import EstadoPedido


class EstadoPedidoRepository(BaseRepository[EstadoPedido]):
    # EstadoPedido es una tabla de catálogo (PK = codigo, sin soft delete),
    # por eso base_stmt no filtra deleted_at, igual que UnidadMedidaRepository.
    model = EstadoPedido

    def base_stmt(self, *, include_deleted: bool = False):
        return select(self.model)

    def list(self) -> list[EstadoPedido]:
        stmt = self.base_stmt().order_by(EstadoPedido.orden)

        return list(self.session.exec(stmt).all())

    def get_by_codigo(self, codigo: str) -> EstadoPedido | None:
        return self.session.get(EstadoPedido, codigo)
