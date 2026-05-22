from sqlmodel import Session, select

from app.core.repository import BaseRepository
from app.modules.direccion_entrega.model import DireccionEntrega


class DireccionEntregaRepository(BaseRepository[DireccionEntrega]):
    """
    Repository especializado para DireccionEntrega.
    """

    def __init__(self, session: Session):
        super().__init__(DireccionEntrega, session)

    def list_by_usuario(
        self,
        usuario_id: int,
    ) -> list[DireccionEntrega]:
        """
        Lista las direcciones activas de un usuario.

        Args:
            usuario_id (int):
                ID del usuario propietario.

        Returns:
            list[DireccionEntrega]
        """

        statement = (
            self.base_stmt()
            .where(DireccionEntrega.usuario_id == usuario_id)
        )

        return self.session.exec(statement).all()

    def get_principal(
        self,
        usuario_id: int,
    ) -> DireccionEntrega | None:
        """
        Devuelve la dirección principal activa del usuario.

        Args:
            usuario_id (int):
                ID del usuario.

        Returns:
            DireccionEntrega | None
        """

        statement = (
            self.base_stmt()
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.es_principal == True)  # noqa: E712
        )

        return self.session.exec(statement).first()

    def unset_principal(
        self,
        usuario_id: int,
    ) -> None:
        """
        Desmarca la dirección principal actual del usuario.

        Se llama antes de marcar una nueva como principal
        para garantizar que solo exista una por usuario.

        Args:
            usuario_id (int):
                ID del usuario.
        """

        current = self.get_principal(usuario_id)

        if current:
            current.es_principal = False
            self.session.add(current)
            self.session.flush()