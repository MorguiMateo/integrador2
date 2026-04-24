import type { Ingrediente } from '../ingredientes.types'

interface IngredienteTableProps {
  items: Ingrediente[]
  onEdit: (ingrediente: Ingrediente) => void
  onDelete: (ingrediente: Ingrediente) => void
}

export function IngredienteTable({ items, onEdit, onDelete }: IngredienteTableProps) {
  if (items.length === 0) {
    return (
      <div className="border border-gray-300 p-8 text-center text-sm text-gray-500">
        No hay ingredientes cargados.
      </div>
    )
  }

  return (
    <div className="border border-gray-300">
      <table className="w-full text-left text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2">Nombre</th>
            <th className="px-4 py-2">Descripción</th>
            <th className="px-4 py-2">Alérgeno</th>
            <th className="px-4 py-2 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {items.map((ingrediente) => {
            const inactivo = Boolean(ingrediente.eliminado)
            return (
            <tr
              key={ingrediente.id}
              className={inactivo ? 'bg-gray-50 text-gray-500 opacity-80' : ''}
            >
              <td className="px-4 py-2 font-medium">
                {ingrediente.nombre}
                {inactivo && (
                  <span className="ml-2 rounded border border-gray-400 px-1.5 py-0.5 text-[10px] uppercase text-gray-600">
                    Desactivado
                  </span>
                )}
              </td>
              <td className="px-4 py-2 text-gray-600">{ingrediente.descripcion ?? '—'}</td>
              <td className="px-4 py-2 text-gray-600">
                {ingrediente.es_alergeno ? 'Sí' : 'No'}
              </td>
              <td className="px-4 py-2 text-right">
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(ingrediente)}
                    disabled={inactivo}
                    className="border border-gray-400 px-3 py-1 text-xs disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(ingrediente)}
                    disabled={inactivo}
                    className="border border-red-400 px-3 py-1 text-xs text-red-600 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {inactivo ? 'Desactivado' : 'Desactivar'}
                  </button>
                </div>
              </td>
            </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
