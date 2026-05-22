from app.core.repository import BaseRepository
from app.modules.unidad_medida.model import UnidadMedida
from sqlmodel import select

class UnidadMedidaRepository(BaseRepository[UnidadMedida]):
    model = UnidadMedida

    def base_stmt(self, *, include_deleted: bool = False):
        return select(self.model)

    def list(self, *, skip: int = 0, limit: int = 50) -> list[UnidadMedida]:
        stmt = self.base_stmt()
        stmt = stmt.offset(skip).limit(limit).order_by(UnidadMedida.id)

        return list(self.session.exec(stmt).all())
