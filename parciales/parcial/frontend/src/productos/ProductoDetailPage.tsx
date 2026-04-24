import { Link, useParams } from 'react-router-dom'

import { useProducto } from './useProductos'

export function ProductoDetailPage() {

  //   "El id de la ruta llega como string. lo parseo a number."
  const { id } = useParams<{ id: string }>()
  const productoId = id ? Number(id) : undefined
  //llama al hook useProducto(productoid) para traer productos desde la API
  const { data: producto, isLoading, isError, error } = useProducto(productoId)

  return (
    <section className="space-y-4">
      <Link to="/productos" className="text-sm text-slate-500 hover:underline">
        ← Volver a productos
      </Link>

      <h1 className="text-2xl font-semibold">
        {producto ? producto.nombre : `Producto #${id}`}
        {producto?.eliminado && (
          <span className="ml-3 align-middle text-sm font-normal text-gray-600">
            (desactivado)
          </span>
        )}
      </h1>

      {producto?.eliminado && (
        <p className="rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
          Este producto está desactivado (soft delete) y no puede editarse desde el listado.
        </p>
      )}

      {isLoading && (
        <div className="border border-gray-300 p-4 text-sm text-gray-500">
          Cargando…
        </div>
      )}

      {isError && (
        <div className="border border-red-400 p-4 text-sm text-red-700">
          Error al cargar producto: {error instanceof Error ? error.message : 'desconocido'}
        </div>
      )}

      {producto && (
        <div className="space-y-4">
          {producto.imagenes_url.length > 0 && (
            <div className="border border-gray-300 p-4">
              <h2 className="mb-2 text-sm font-semibold">Imágenes</h2>
              <div className="flex flex-wrap gap-3">
                {producto.imagenes_url.map((url, idx) => (
                  <img
                    key={`${url}-${idx}`}
                    src={url}
                    alt={`${producto.nombre} ${idx + 1}`}
                    className="h-32 w-32 object-cover border border-gray-300"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-1 border border-gray-300 p-4">
              <p className="text-xs uppercase text-gray-500">Descripción</p>
              <p className="text-sm">{producto.descripcion ?? '—'}</p>
            </div>
            <div className="grid grid-cols-3 gap-4 border border-gray-300 p-4">
              <div>
                <p className="text-xs uppercase text-gray-500">Precio</p>
                <p className="text-sm font-medium">${producto.precio_base}</p>
              </div>
              <div>
                <p className="text-xs uppercase text-gray-500">Stock</p>
                <p className="text-sm font-medium">{producto.stock_cantidad}</p>
              </div>
              <div>
                <p className="text-xs uppercase text-gray-500">Estado</p>
                <p className="text-sm font-medium">
                  {producto.disponible ? 'Disponible' : 'No disponible'}
                </p>
              </div>
            </div>
          </div>

          <div className="border border-gray-300 p-4">
            <h2 className="mb-2 text-sm font-semibold">Categorías</h2>
            {producto.categorias.length === 0 ? (
              <p className="text-sm text-gray-500">Sin categorías.</p>
            ) : (
              <ul className="flex flex-wrap gap-2">
                {producto.categorias.map((c) => (
                  <li
                    key={c.categoria.id}
                    className={`border px-3 py-1 text-xs ${
                      c.categoria.eliminado
                        ? 'border-gray-400 bg-gray-100 text-gray-500 line-through decoration-gray-500'
                        : c.es_principal
                          ? 'border-blue-700 bg-blue-600 text-white'
                          : 'border-gray-400 text-gray-700'
                    }`}
                  >
                    {c.categoria.nombre}
                    {c.categoria.eliminado && ' (desactivada)'}
                    {c.es_principal && ' • principal'}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="border border-gray-300 p-4">
            <h2 className="mb-2 text-sm font-semibold">Ingredientes</h2>
            {producto.ingredientes.length === 0 ? (
              <p className="text-sm text-gray-500">Sin ingredientes.</p>
            ) : (
              <ul className="divide-y divide-gray-200 text-sm">
                {producto.ingredientes.map((i) => (
                  <li
                    key={i.ingrediente.id}
                    className={`flex items-center justify-between py-2 ${
                      i.ingrediente.eliminado ? 'text-gray-500' : ''
                    }`}
                  >
                    <span>
                      {i.ingrediente.nombre}
                      {i.ingrediente.eliminado && (
                        <span className="ml-1 text-[10px] uppercase text-gray-500">
                          desactivado
                        </span>
                      )}
                    </span>
                    <span className="text-xs text-gray-500">
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
