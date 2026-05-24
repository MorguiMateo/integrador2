from fastapi import HTTPException, status

from app.modules.direccion_entrega.model import DireccionEntrega
from app.modules.direccion_entrega.repository import DireccionEntregaRepository
from app.modules.direccion_entrega.schema import DireccionCreate, DireccionUpdate


def list_direcciones(uow, usuario_id: int) -> list[DireccionEntrega]:
    repository = DireccionEntregaRepository(uow.session)
    return repository.list_by_usuario(usuario_id)


def create_direccion(
    uow,
    usuario_id: int,
    data: DireccionCreate,
) -> DireccionEntrega:
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


def _get_owned(repository: DireccionEntregaRepository, direccion_id: int, usuario_id: int) -> DireccionEntrega:
    direccion = repository.get(direccion_id)
    if not direccion or direccion.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirección no encontrada.",
        )
    return direccion


def update_direccion(
    uow,
    usuario_id: int,
    direccion_id: int,
    data: DireccionUpdate,
) -> DireccionEntrega:
    repository = DireccionEntregaRepository(uow.session)
    direccion = _get_owned(repository, direccion_id, usuario_id)

    payload = data.model_dump(exclude_unset=True)

    if payload.get("es_principal") is True:
        repository.unset_principal(usuario_id)

    for field, value in payload.items():
        setattr(direccion, field, value)

    return repository.save(direccion)


def delete_direccion(
    uow,
    usuario_id: int,
    direccion_id: int,
) -> None:
    repository = DireccionEntregaRepository(uow.session)
    _get_owned(repository, direccion_id, usuario_id)
    repository.soft_delete(direccion_id)


def set_principal(
    uow,
    usuario_id: int,
    direccion_id: int,
) -> DireccionEntrega:
    repository = DireccionEntregaRepository(uow.session)
    direccion = _get_owned(repository, direccion_id, usuario_id)

    repository.unset_principal(usuario_id)
    direccion.es_principal = True
    uow.session.add(direccion)
    uow.session.flush()

    return direccion
