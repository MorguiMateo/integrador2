export interface Categoria {
  id: number;
  codigo: string;
  descripcion: string;
  activo: boolean;
}

export interface CategoriaInput {
  codigo: string;
  descripcion: string;
  activo: boolean;
}
