from sqlmodel import Session, select

from app.core.repository import BaseRepository
from app.modules.usuario.model import Usuario


class UsuarioRepository(BaseRepository[Usuario]):
  
    model = Usuario

    def get_by_email(
        self,
        email: str,
    ) -> Usuario | None:
        

        statement = (
            select(Usuario)
            .where(Usuario.email == email)
            .where(Usuario.deleted_at.is_(None))
        )

        return self.session.exec(statement).first()
    
    def get_all(self, *, skip: int = 0, limit: int = 100) -> list[Usuario]:
        stmt = select(Usuario).where(Usuario.deleted_at.is_(None))
        stmt = stmt.offset(skip).limit(limit).order_by(Usuario.id)
        return list(self.session.exec(stmt).all())

    def filter(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        rol: str | None = None,
        q: str | None = None,
    ) -> list[Usuario]:
        from app.modules.usuario_rol.model import UsuarioRol

        stmt = select(Usuario).where(Usuario.deleted_at.is_(None))
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                (Usuario.email.ilike(like))
                | (Usuario.nombre.ilike(like))
                | (Usuario.apellido.ilike(like))
            )
        if rol:
            stmt = stmt.where(
                Usuario.id.in_(
                    select(UsuarioRol.usuario_id).where(UsuarioRol.rol_codigo == rol)
                )
            )
        stmt = stmt.offset(skip).limit(limit).order_by(Usuario.id)
        return list(self.session.exec(stmt).all())