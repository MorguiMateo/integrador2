import type { Categoria } from '../categorias.types'

interface CategoriaTableProps {
  items: Categoria[]
  onEdit: (categoria: Categoria) => void
  onDelete: (categoria: Categoria) => void
}

export function CategoriaTable({ items, onEdit, onDelete }: CategoriaTableProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
        No hay categorías cargadas.
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-2 w-20">Imagen</th>
            <th className="px-4 py-2">Nombre</th>
            <th className="px-4 py-2">Descripción</th>
            <th className="px-4 py-2 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {items.map((categoria) => (
            <tr key={categoria.id}>
              <td className="px-4 py-2">
                {categoria.imagen_url ? (
                  <img
                    src={categoria.imagen_url}
                    alt={categoria.nombre}
                    className="h-12 w-12 rounded-md object-cover border border-slate-200"
                    // Si la URL falla, reemplazamos por el placeholder para no mostrar el ícono de imagen rota
                    onError={(e) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                ) : (
                  <div className="h-12 w-12 rounded-md border border-dashed border-slate-300 bg-slate-50 text-[10px] text-slate-400 flex items-center justify-center">
                    sin imagen
                  </div>
                )}
              </td>
              <td className="px-4 py-2 font-medium text-slate-900">{categoria.nombre}</td>
              <td className="px-4 py-2 text-slate-600">{categoria.descripcion ?? '—'}</td>
              <td className="px-4 py-2 text-right">
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(categoria)}
                    className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(categoria)}
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
