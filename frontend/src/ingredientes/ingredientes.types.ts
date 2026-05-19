export interface Ingrediente {
  id: number
  nombre: string
  descripcion: string | null
  es_alergeno: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
  eliminado?: boolean
}

export interface IngredienteFormValues {
  nombre: string
  descripcion: string | null
  es_alergeno: boolean
}
