from typing import List, Optional

from pydantic import Field
from sqlmodel import SQLModel

from app.categoria.schema import CategoriaRead
from app.ingrediente.schema import IngredienteRead


class IngredienteEnProductoCreate(SQLModel):
    ingrediente_id: int = Field(gt=0)
    cantidad: float = Field(gt=0)
    unidad: str = Field(min_length=1, max_length=15, default="unidad")


class IngredienteEnProductoRead(SQLModel):
    cantidad: float
    unidad: str
    ingrediente: IngredienteRead


class ProductoBase(SQLModel):
    nombre: str = Field(min_length=2, max_length=80)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    precio: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    activo: bool = True


class ProductoCreate(ProductoBase):
    categoria_ids: List[int] = Field(default_factory=list)
    ingredientes: List[IngredienteEnProductoCreate] = Field(default_factory=list)


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=80)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    precio: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    activo: Optional[bool] = None
    categoria_ids: Optional[List[int]] = None
    ingredientes: Optional[List[IngredienteEnProductoCreate]] = None


class ProductoRead(ProductoBase):
    id: int
    categorias: List[CategoriaRead] = Field(default_factory=list)
    ingredientes: List[IngredienteEnProductoRead] = Field(default_factory=list)
