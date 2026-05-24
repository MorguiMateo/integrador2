from fastapi import HTTPException, status
from sqlmodel import select

from app.modules.admin.schema import RolesUpdate, UsuarioAdminUpdate
from app.modules.usuario.model import Usuario
from app.modules.usuario.repository import UsuarioRepository
from app.modules.usuario_rol.model import UsuarioRol


def list_usuarios(
    uow,
    *,
    skip: int,
    limit: int,
    rol: str | None,
    q: str | None,
) -> list[Usuario]:
    repository = UsuarioRepository(uow.session)
    return repository.filter(skip=skip, limit=limit, rol=rol, q=q)


def get_usuario(uow, usuario_id: int) -> Usuario:
    repository = UsuarioRepository(uow.session)
    usuario = repository.get(usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )
    return usuario


def update_usuario(uow, usuario_id: int, data: UsuarioAdminUpdate) -> Usuario:
    usuario = get_usuario(uow, usuario_id)
    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(usuario, field, value)
    uow.session.add(usuario)
    uow.session.flush()
    return usuario


def delete_usuario(uow, usuario_id: int, *, current_user_id: int) -> None:
    if usuario_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No podés eliminar tu propio usuario.",
        )
    repository = UsuarioRepository(uow.session)
    deleted = repository.soft_delete(usuario_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )


def set_roles(
    uow,
    usuario_id: int,
    data: RolesUpdate,
    *,
    current_user_id: int,
) -> Usuario:
    usuario = get_usuario(uow, usuario_id)

    nuevos = set(data.roles)

    if usuario_id == current_user_id and "ADMIN" not in nuevos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No podés removerte el rol ADMIN a vos mismo.",
        )

    existentes_stmt = select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
    existentes = list(uow.session.exec(existentes_stmt).all())
    actuales = {ur.rol_codigo for ur in existentes}

    a_quitar = actuales - nuevos
    a_agregar = nuevos - actuales

    for link in existentes:
        if link.rol_codigo in a_quitar:
            uow.session.delete(link)

    for codigo in a_agregar:
        uow.session.add(
            UsuarioRol(
                usuario_id=usuario_id,
                rol_codigo=codigo,
                asignado_por_id=current_user_id,
            )
        )

    uow.session.flush()
    uow.session.refresh(usuario)
    return usuario
