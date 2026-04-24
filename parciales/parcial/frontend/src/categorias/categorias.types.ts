export interface Categoria {
  id: number
  parent_id: number | null
  nombre: string
  descripcion: string | null
  imagen_url: string | null
  created_at: string
  updated_at: string
  deleted_at?: string | null
  eliminado?: boolean
}

export interface CategoriaFormValues {
  nombre: string
  descripcion: string | null
  imagen_url: string | null
  parent_id: number | null
}
