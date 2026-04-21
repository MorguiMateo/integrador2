import { useState } from 'react'
import { Link } from 'react-router-dom'

import type { Producto } from '../productos.types'

interface ProductoCardProps {
  producto: Producto
  onEdit: (producto: Producto) => void
  onDelete: (producto: Producto) => void
}

export function ProductoCard({ producto, onEdit, onDelete }: ProductoCardProps) {
  // Índice actual del carrusel: apunta a la imagen visible dentro de imagenes_url
  const [imageIndex, setImageIndex] = useState(0)
  const imagenes = producto.imagenes_url
  const total = imagenes.length

  const prev = () => setImageIndex((i) => (i - 1 + total) % total)
  const next = () => setImageIndex((i) => (i + 1) % total)

  return (
    <article className="flex flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="relative aspect-square w-full bg-slate-100">
        {total > 0 ? (
          <>
            <img
              src={imagenes[imageIndex]}
              alt={`${producto.nombre} ${imageIndex + 1}`}
              className="h-full w-full object-cover"
              // Si una URL rompe, no dejamos el ícono roto: saltamos a la siguiente si hay más
              onError={(e) => {
                if (total > 1) {
                  next()
                } else {
                  e.currentTarget.style.display = 'none'
                }
              }}
            />
            {total > 1 && (
              <>
                <button
                  type="button"
                  onClick={prev}
                  aria-label="Imagen anterior"
                  className="absolute left-2 top-1/2 -translate-y-1/2 rounded-full bg-white/80 px-2 py-1 text-slate-700 shadow hover:bg-white"
                >
                  ‹
                </button>
                <button
                  type="button"
                  onClick={next}
                  aria-label="Imagen siguiente"
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-white/80 px-2 py-1 text-slate-700 shadow hover:bg-white"
                >
                  ›
                </button>
                <span className="absolute bottom-2 right-2 rounded-full bg-black/60 px-2 py-0.5 text-xs font-medium text-white">
                  {imageIndex + 1} / {total}
                </span>
              </>
            )}
          </>
        ) : (
          <div className="flex h-full w-full items-center justify-center text-xs text-slate-400">
            sin imagen
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-start justify-between gap-2">
          <Link
            to={`/productos/${producto.id}`}
            className="text-base font-semibold text-slate-900 hover:underline"
          >
            {producto.nombre}
          </Link>
          <span
            className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
              producto.disponible
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-slate-200 text-slate-600'
            }`}
          >
            {producto.disponible ? 'Disponible' : 'No disponible'}
          </span>
        </div>

        {producto.descripcion && (
          <p className="line-clamp-2 text-sm text-slate-600">{producto.descripcion}</p>
        )}

        <div className="mt-auto flex items-center justify-between pt-2 text-sm">
          <span className="font-semibold text-slate-900">${producto.precio_base}</span>
          <span className="text-xs text-slate-500">Stock: {producto.stock_cantidad}</span>
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={() => onEdit(producto)}
            className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
          >
            Editar
          </button>
          <button
            type="button"
            onClick={() => onDelete(producto)}
            className="rounded-md border border-red-200 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
          >
            Borrar
          </button>
        </div>
      </div>
    </article>
  )
}
