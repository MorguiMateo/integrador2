from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.types import MoneyDecimal
from app.modules.categoria.schema import CategoriaRead
from app.modules.ingrediente.schema import IngredienteRead
from app.modules.unidad_medida.schema import UnidadMedidaRead

class ProductoCategoriaCreate(BaseModel):
    categoria_id: int = Field(ge=1)
    es_principal: bool = False

class ProductoCategoriaRead(BaseModel):
    categoria: CategoriaRead
    es_principal: bool

    model_config = ConfigDict(from_attributes=True)


class ProductoIngredienteCreate(BaseModel):
    ingrediente_id: int = Field(ge=1)
    es_removible: bool = False
    cantidad: float = Field(gt=0)
    unidad_medida_id: int = Field(ge=1)


class ProductoIngredienteRead(BaseModel):
    ingrediente: IngredienteRead
    es_removible: bool
    cantidad: float
    unidad_medida_id: int

    model_config = ConfigDict(from_attributes=True)


class ProductoBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: Optional[str] = None
    precio_base: MoneyDecimal = Field(ge=0, max_digits=10, decimal_places=2)
    imagenes_url: list[str] = []
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = True


class ProductoCreate(ProductoBase):
    categorias: list[ProductoCategoriaCreate] = []
    ingredientes: list[ProductoIngredienteCreate] = []
    unidad_venta_id: Optional[int] = None


class ProductoRead(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    categorias: list[ProductoCategoriaRead] = []
    ingredientes: list[ProductoIngredienteRead] = []
    unidad_venta_id: Optional[int] = None
    unidad_venta: Optional[UnidadMedidaRead] = None

    model_config = ConfigDict(from_attributes=True)


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=150)
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    imagenes_url: Optional[list[str]] = None
    stock_cantidad: Optional[int] = Field(default=None, ge=0)
    disponible: Optional[bool] = None
    categorias: Optional[list[ProductoCategoriaCreate]] = None
    ingredientes: Optional[list[ProductoIngredienteCreate]] = None
    unidad_venta_id: Optional[int] = None
