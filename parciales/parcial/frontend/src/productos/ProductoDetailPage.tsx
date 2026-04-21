import { Link, useParams } from 'react-router-dom'

import { useProducto } from './useProductos'

export function ProductoDetailPage() {
  const { id } = useParams<{ id: string }>()
  const productoId = id ? Number(id) : undefined
  const { data: producto, isLoading, isError, error } = useProducto(productoId)

  return (
    <section className="space-y-4">
      <Link to="/productos" className="text-sm text-slate-500 hover:underline">
        ← Volver a productos
      </Link>

      <h1 className="text-2xl font-semibold">
        {producto ? producto.nombre : `Producto #${id}`}
      </h1>

      {isLoading && (
        <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">
          Cargando…
        </div>
      )}

      {isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Error al cargar producto: {error instanceof Error ? error.message : 'desconocido'}
        </div>
      )}

      {producto && (
        <div className="space-y-4">
          {producto.imagenes_url.length > 0 && (
            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <h2 className="mb-2 text-sm font-semibold text-slate-700">Imágenes</h2>
              <div className="flex flex-wrap gap-3">
                {producto.imagenes_url.map((url, idx) => (
                  <img
                    key={`${url}-${idx}`}
                    src={url}
                    alt={`${producto.nombre} ${idx + 1}`}
                    className="h-32 w-32 rounded-md object-cover border border-slate-200"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-1 rounded-lg border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase text-slate-500">Descripción</p>
              <p className="text-sm text-slate-800">{producto.descripcion ?? '—'}</p>
            </div>
            <div className="grid grid-cols-3 gap-4 rounded-lg border border-slate-200 bg-white p-4">
              <div>
                <p className="text-xs uppercase text-slate-500">Precio</p>
                <p className="text-sm font-medium text-slate-900">${producto.precio_base}</p>
              </div>
              <div>
                <p className="text-xs uppercase text-slate-500">Stock</p>
                <p className="text-sm font-medium text-slate-900">{producto.stock_cantidad}</p>
              </div>
              <div>
                <p className="text-xs uppercase text-slate-500">Estado</p>
                <p className="text-sm font-medium text-slate-900">
                  {producto.disponible ? 'Disponible' : 'No disponible'}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <h2 className="mb-2 text-sm font-semibold text-slate-700">Categorías</h2>
            {producto.categorias.length === 0 ? (
              <p className="text-sm text-slate-500">Sin categorías.</p>
            ) : (
              <ul className="flex flex-wrap gap-2">
                {producto.categorias.map((c) => (
                  <li
                    key={c.categoria.id}
                    className={`rounded-full border px-3 py-1 text-xs ${
                      c.es_principal
                        ? 'border-slate-900 bg-slate-900 text-white'
                        : 'border-slate-300 bg-slate-50 text-slate-700'
                    }`}
                  >
                    {c.categoria.nombre}
                    {c.es_principal && ' • principal'}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <h2 className="mb-2 text-sm font-semibold text-slate-700">Ingredientes</h2>
            {producto.ingredientes.length === 0 ? (
              <p className="text-sm text-slate-500">Sin ingredientes.</p>
            ) : (
              <ul className="divide-y divide-slate-200 text-sm">
                {producto.ingredientes.map((i) => (
                  <li key={i.ingrediente.id} className="flex items-center justify-between py-2">
                    <span className="text-slate-800">{i.ingrediente.nombre}</span>
                    <span className="text-xs text-slate-500">
                      {i.es_removible ? 'removible' : 'obligatorio'}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
