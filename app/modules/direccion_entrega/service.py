from fastapi import HTTPException, status

from app.modules.direccion_entrega.model import DireccionEntrega
from app.modules.direccion_entrega.repository import DireccionEntregaRepository
from app.modules.direccion_entrega.schema import DireccionCreate
from app.modules.usuario.model import Usuario

# -----------------------------------------------------------------------------
# Helpers internos
# -----------------------------------------------------------------------------


def _assert_owner_or_admin(
    current_user: Usuario,
    usuario_id: int,
) -> None:
    """
    Verifica que el usuario autenticado sea el dueño o un ADMIN.

    Args:
        current_user (Usuario):
            Usuario autenticado.

        usuario_id (int):
            ID del propietario del recurso.

    Raises:
        HTTPException 403:
            El usuario no tiene permisos sobre este recurso.
    """

    is_owner = current_user.id == usuario_id
    is_admin = "ADMIN" in current_user.roles

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permisos para acceder a estas direcciones.",
        )


# -----------------------------------------------------------------------------
# Servicios
# -----------------------------------------------------------------------------


def list_direcciones(
    uow,
    usuario_id: int,
    current_user: Usuario,
) -> list[DireccionEntrega]:
    """
    Lista las direcciones activas de un usuario.

    Args:
        uow:
            Unit of Work activo.

        usuario_id (int):
            ID del usuario propietario.

        current_user (Usuario):
            Usuario autenticado que realiza la consulta.

    Returns:
        list[DireccionEntrega]

    Raises:
        HTTPException 403:
            El usuario no es dueño ni ADMIN.
    """

    _assert_owner_or_admin(current_user, usuario_id)

    repository = DireccionEntregaRepository(uow.session)

    return repository.list_by_usuario(usuario_id)


def create_direccion(
    uow,
    usuario_id: int,
    data: DireccionCreate,
    current_user: Usuario,
) -> DireccionEntrega:
    """
    Crea una dirección de entrega para el usuario.

    Si ``es_principal=True``, desmarca la dirección
    principal anterior antes de persistir la nueva.

    Args:
        uow:
            Unit of Work activo.

        usuario_id (int):
            ID del usuario propietario.

        data (DireccionCreate):
            Datos de la nueva dirección.

        current_user (Usuario):
            Usuario autenticado que realiza la operación.

    Returns:
        DireccionEntrega:
            Dirección persistida.

    Raises:
        HTTPException 403:
            El usuario no es dueño ni ADMIN.
    """

    _assert_owner_or_admin(current_user, usuario_id)

    repository = DireccionEntregaRepository(uow.session)

    if data.es_principal:
        repository.unset_principal(usuario_id)

    direccion = DireccionEntrega(
        usuario_id=usuario_id,
        alias=data.alias,
        linea1=data.linea1,
        linea2=data.linea2,
        ciudad=data.ciudad,
        provincia=data.provincia,
        codigo_postal=data.codigo_postal,
        latitud=data.latitud,
        longitud=data.longitud,
        es_principal=data.es_principal,
    )

    return repository.save(direccion)


def delete_direccion(
    uow,
    usuario_id: int,
    direccion_id: int,
    current_user: Usuario,
) -> None:
    """
    Soft-delete de una dirección de entrega.

    Args:
        uow:
            Unit of Work activo.

        usuario_id (int):
            ID del usuario propietario.

        direccion_id (int):
            ID de la dirección a eliminar.

        current_user (Usuario):
            Usuario autenticado que realiza la operación.

    Raises:
        HTTPException 403:
            El usuario no es dueño ni ADMIN.

        HTTPException 404:
            La dirección no existe o ya fue eliminada.
    """

    _assert_owner_or_admin(current_user, usuario_id)

    repository = DireccionEntregaRepository(uow.session)

    deleted = repository.soft_delete(direccion_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirección no encontrada.",
        )
    

def set_principal(
    uow,
    usuario_id: int,
    direccion_id: int,
    current_user: Usuario,
) -> DireccionEntrega:
    _assert_owner_or_admin(current_user, usuario_id)

    repository = DireccionEntregaRepository(uow.session)

    direccion = repository.get(direccion_id)

    if not direccion or direccion.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirección no encontrada.",
        )

    repository.unset_principal(usuario_id)
    direccion.es_principal = True
    uow.session.add(direccion)
    uow.session.flush()

    return direccion
