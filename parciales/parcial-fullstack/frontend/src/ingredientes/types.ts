export interface Ingrediente {
  id: number;
  nombre: string;
  descripcion: string | null;
  es_alergeno: boolean;
  activo: boolean;
}

export interface IngredienteInput {
  nombre: string;
  descripcion: string | null;
  es_alergeno: boolean;
  activo: boolean;
}
