import type { Categoria } from '../categorias/categorias.types'
import type { Ingrediente } from '../ingredientes/ingredientes.types'

export interface ProductoCategoria {
  categoria: Categoria
  es_principal: boolean
}

export interface ProductoIngrediente {
  ingrediente: Ingrediente
  es_removible: boolean
}

export interface Producto {
  id: number
  nombre: string
  descripcion: string | null
  precio_base: string
  imagenes_url: string[]
  stock_cantidad: number
  disponible: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
  eliminado?: boolean
  categorias: ProductoCategoria[]
  ingredientes: ProductoIngrediente[]
}

export interface ProductoCategoriaInput {
  categoria_id: number
  es_principal: boolean
}

export interface ProductoIngredienteInput {
  ingrediente_id: number
  es_removible: boolean
}

export interface ProductoFormValues {
  nombre: string
  descripcion: string | null
  precio_base: string
  imagenes_url: string[]
  stock_cantidad: number
  disponible: boolean
  categorias: ProductoCategoriaInput[]
  ingredientes: ProductoIngredienteInput[]
}

export interface ProductoFilters {
  q?: string
  disponible?: boolean
  precio_min?: number
  precio_max?: number
  skip?: number
  limit?: number
  incluir_eliminados?: boolean
}
