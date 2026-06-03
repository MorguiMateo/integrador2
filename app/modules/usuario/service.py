from app.core.security import (
    get_password_hash,
    verify_password,
)
from app.modules.usuario.model import Usuario
from app.modules.usuario.repository import UsuarioRepository
from app.modules.usuario.schemas import UserCreate


def create_usuario(
    uow,
    data: UserCreate,
) -> Usuario:

    usuario_repository = UsuarioRepository(uow.session)

    password_hash = get_password_hash(data.password)

    usuario = Usuario(
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        celular=data.celular,
        password_hash=password_hash,
    )

    usuario_repository.save(usuario)

    from app.modules.usuario_rol.model import UsuarioRol

    usuario_rol = UsuarioRol(usuario_id=usuario.id, rol_codigo="CLIENT")
    uow.session.add(usuario_rol)
    uow.session.flush()

    return usuario


def get_usuario(
    uow,
    usuario_id: int,
) -> Usuario | None:

    usuario_repository = UsuarioRepository(uow.session)

    return usuario_repository.get(usuario_id)


def list_usuarios(
    uow,
    skip: int = 0,
    limit: int = 100,
) -> list[Usuario]:

    usuario_repository = UsuarioRepository(uow.session)

    return usuario_repository.get_all(
        skip=skip,
        limit=limit,
    )


def authenticate_user(
    uow,
    email: str,
    password: str,
) -> Usuario | None:

    usuario_repository = UsuarioRepository(uow.session)

    usuario = usuario_repository.get_by_email(email)

    if not usuario:
        return None

    is_valid_password = verify_password(
        password,
        usuario.password_hash,
    )

    if not is_valid_password:
        return None

    return usuario