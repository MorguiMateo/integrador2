from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal

class ItemPedidoRequest(BaseModel):
    
    producto_id: int
    cantidad: int  = Field(ge=1)
    personalizacion: list[int] | None = None

class PedidoCreate(BaseModel):

    direccion_id: int | None = None
    forma_pago_codigo: str
    notas: str | None = None
    items: list[ItemPedidoRequest] = Field(min_length=1)



class AvanzarEstadoRequest(BaseModel):
    
    estado_hacia: str
    motivo: str | None = None



class DetallePedidoRead(BaseModel):

    pedido_id: int
    producto_id: int
    cantidad: int
    nombre_snapshot: str
    precio_snapshot: Decimal
    subtotal_snap: Decimal
    personalizacion: list[int]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)




class HistorialRead(BaseModel):

    id: int
    estado_desde: str | None
    estado_hacia: str 
    usuario_id: int | None 
    motivo: str | None
    created_at: datetime 
    model_config = ConfigDict(from_attributes=True)



class PedidoRead(BaseModel):

    id: int 
    usuario_id: int 
    direccion_id: int | None 
    estado_codigo: str 
    forma_pago_codigo: str 
    subtotal: Decimal 
    descuento: Decimal 
    costo_envio: Decimal 
    total: Decimal 
    notas: str | None 
    created_at: datetime 
    updated_at: datetime 
    deleted_at: datetime | None 
    detalles: list[DetallePedidoRead] = []
    historial: list[HistorialRead] = []
    model_config = ConfigDict(from_attributes=True)