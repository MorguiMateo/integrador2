import type { Categoria } from '../categorias.types'

interface CategoriaTableProps {
  items: Categoria[]
  onEdit: (categoria: Categoria) => void
  onDelete: (categoria: Categoria) => void
}

export function CategoriaTable({ items, onEdit, onDelete }: CategoriaTableProps) {
  if (items.length === 0) {
    return (
      <div className="border border-gray-300 p-8 text-center text-sm text-gray-500">
        No hay categorías cargadas.
      </div>
    )
  }

  return (
    <div className="border border-gray-300">
      <table className="w-full text-left text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 w-20">Imagen</th>
            <th className="px-4 py-2">Nombre</th>
            <th className="px-4 py-2">Descripción</th>
            <th className="px-4 py-2 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {items.map((categoria) => (
            <tr key={categoria.id}>
              <td className="px-4 py-2">
                {categoria.imagen_url ? (
                  <img
                    src={categoria.imagen_url}
                    alt={categoria.nombre}
                    className="h-12 w-12 object-cover border border-gray-300"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                ) : (
                  <div className="h-12 w-12 border border-gray-300 text-[10px] text-gray-400 flex items-center justify-center">
                    sin imagen
                  </div>
                )}
              </td>
              <td className="px-4 py-2 font-medium">{categoria.nombre}</td>
              <td className="px-4 py-2 text-gray-600">{categoria.descripcion ?? '—'}</td>
              <td className="px-4 py-2 text-right">
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(categoria)}
                    className="border border-gray-400 px-3 py-1 text-xs"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(categoria)}
                    className="border border-red-400 px-3 py-1 text-xs text-red-600"
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
