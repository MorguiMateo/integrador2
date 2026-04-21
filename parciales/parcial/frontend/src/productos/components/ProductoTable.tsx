import type { Producto } from '../productos.types'

interface ProductoTableProps {
  items: Producto[]
  onEdit: (producto: Producto) => void
  onDelete: (producto: Producto) => void
}

export function ProductoTable({ items, onEdit, onDelete }: ProductoTableProps) {
  void items
  void onEdit
  void onDelete
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">
      TODO: tabla de productos con link al detalle (/productos/:id).
    </div>
  )
}
