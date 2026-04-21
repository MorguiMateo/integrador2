import type { Ingrediente } from '../ingredientes.types'

interface IngredienteTableProps {
  items: Ingrediente[]
  onEdit: (ingrediente: Ingrediente) => void
  onDelete: (ingrediente: Ingrediente) => void
}

export function IngredienteTable({ items, onEdit, onDelete }: IngredienteTableProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
        No hay ingredientes cargados.
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-2">Nombre</th>
            <th className="px-4 py-2">Descripción</th>
            <th className="px-4 py-2">Alérgeno</th>
            <th className="px-4 py-2 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {items.map((ingrediente) => (
            <tr key={ingrediente.id}>
              <td className="px-4 py-2 font-medium text-slate-900">{ingrediente.nombre}</td>
              <td className="px-4 py-2 text-slate-600">{ingrediente.descripcion ?? '—'}</td>
              <td className="px-4 py-2 text-slate-600">
                {ingrediente.es_alergeno ? 'Sí' : 'No'}
              </td>
              <td className="px-4 py-2 text-right">
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(ingrediente)}
                    className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(ingrediente)}
                    className="rounded-md border border-red-200 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
                  >
                    Borrar
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
