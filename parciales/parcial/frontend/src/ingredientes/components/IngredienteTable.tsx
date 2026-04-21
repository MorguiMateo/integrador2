import type { Ingrediente } from '../ingredientes.types'

interface IngredienteTableProps {
  items: Ingrediente[]
  onEdit: (ingrediente: Ingrediente) => void
  onDelete: (ingrediente: Ingrediente) => void
}

export function IngredienteTable({ items, onEdit, onDelete }: IngredienteTableProps) {
  void items
  void onEdit
  void onDelete
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">
      TODO: tabla de ingredientes.
    </div>
  )
}
