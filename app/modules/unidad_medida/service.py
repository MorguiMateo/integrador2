from app.core.uow import UnitOfWork
from app.modules.unidad_medida.model import UnidadMedida
from app.modules.unidad_medida.schema import UnidadMedidaCreate

def list_unidades(uow: UnitOfWork, *, skip: int = 0, limit: int = 50) -> list[UnidadMedida]:
    return uow.unidades_medida.list(skip=skip, limit=limit)

def get_unidad(uow: UnitOfWork, unidad_id: int) -> UnidadMedida | None:
    return uow.unidades_medida.get(unidad_id)

def create_unidad(uow: UnitOfWork, data: UnidadMedidaCreate) -> UnidadMedida:
    return uow.unidades_medida.save(UnidadMedida(**data.model_dump()))

