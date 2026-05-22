from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.modules.categoria.schema import CategoriaRead
from app.modules.ingrediente.schema import IngredienteRead


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
    cantidad: Decimal = Field(gt=0, max_digits=10, decimal_places=3)
    unidad_medida_id: int = Field(ge=1)


class ProductoIngredienteRead(BaseModel):
    ingrediente: IngredienteRead
    es_removible: bool
    cantidad: Decimal
    unidad_medida_id: int

    model_config = ConfigDict(from_attributes=True)


class ProductoBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: str | None = None
    precio_base: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    imagenes_url: list[str] = Field(default_factory=list)
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = True


class ProductoCreate(ProductoBase):
    categorias: list[ProductoCategoriaCreate] = Field(default_factory=list)
    ingredientes: list[ProductoIngredienteCreate] = Field(default_factory=list)
    unidad_venta_id: int | None = None


class ProductoRead(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    categorias: list[ProductoCategoriaRead] = []
    ingredientes: list[ProductoIngredienteRead] = []
    unidad_venta_id: int | None = None
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def eliminado(self) -> bool:
        return self.deleted_at is not None


class ProductoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    descripcion: str | None = None
    precio_base: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    imagenes_url: list[str] | None = None
    stock_cantidad: int | None = Field(default=None, ge=0)
    disponible: bool | None = None
    categorias: list[ProductoCategoriaCreate] | None = None
    ingredientes: list[ProductoIngredienteCreate] | None = None
    unidad_venta_id: int | None = None


    #meti unidad_venta_id: int | None = None en ProductoCreate, en ProductoUpdate y en ProductoRead
    #y meti cantidad y unidad de medida en ProductoIngredienteCreate y en ProductoIngredienteRead