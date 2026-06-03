from sqlmodel import select

from app.core.repository import BaseRepository
from app.modules.direccion_entrega.model import DireccionEntrega


class DireccionEntregaRepository(BaseRepository[DireccionEntrega]):

    model = DireccionEntrega

    def list_by_usuario(
        self,
        usuario_id: int,
    ) -> list[DireccionEntrega]:

        statement = (
            self.base_stmt()
            .where(DireccionEntrega.usuario_id == usuario_id)
        )

        return self.session.exec(statement).all()

    def get_principal(
        self,
        usuario_id: int,
    ) -> DireccionEntrega | None:

        statement = (
            self.base_stmt()
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.es_principal == True)  
        )

        return self.session.exec(statement).first()

    def unset_principal(
        self,
        usuario_id: int,
    ) -> None:

        current = self.get_principal(usuario_id)

        if current:
            current.es_principal = False
            self.session.add(current)
            self.session.flush()