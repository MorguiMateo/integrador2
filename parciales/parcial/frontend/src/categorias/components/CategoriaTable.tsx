import type { Categoria } from '../categorias.types'

interface CategoriaTableProps {
  items: Categoria[]
  onEdit: (categoria: Categoria) => void
  onDelete: (categoria: Categoria) => void
}

export function CategoriaTable({ items, onEdit, onDelete }: CategoriaTableProps) {
  // TODO: renderizar filas con nombre, descripcion y acciones.
  void items
  void onEdit
  void onDelete
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">
      TODO: tabla de categorías.
    </div>
  )
}
