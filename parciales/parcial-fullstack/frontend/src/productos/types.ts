import type { Categoria } from "@/categorias/types";
import type { Ingrediente } from "@/ingredientes/types";

export interface IngredienteEnProducto {
  cantidad: number;
  unidad: string;
  ingrediente: Ingrediente;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio: number;
  stock: number;
  activo: boolean;
  categorias: Categoria[];
  ingredientes: IngredienteEnProducto[];
}

export interface IngredienteInputItem {
  ingrediente_id: number;
  cantidad: number;
  unidad: string;
}

export interface ProductoInput {
  nombre: string;
  descripcion: string | null;
  precio: number;
  stock: number;
  activo: boolean;
  categoria_ids: number[];
  ingredientes: IngredienteInputItem[];
}
