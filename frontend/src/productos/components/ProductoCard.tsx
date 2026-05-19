import { useState } from 'react'
import { Link } from 'react-router-dom'

import type { Producto } from '../productos.types'

interface ProductoCardProps {
  producto: Producto
  onEdit: (producto: Producto) => void
  onDelete: (producto: Producto) => void
}

export function ProductoCard({ producto, onEdit, onDelete }: ProductoCardProps) {
  const inactivo = Boolean(producto.eliminado)
  // Índice actual del carrusel: apunta a la imagen visible dentro de imagenes_url
  const [imageIndex, setImageIndex] = useState(0)
  const imagenes = producto.imagenes_url
  const total = imagenes.length

  const prev = () => setImageIndex((i) => (i - 1 + total) % total)
  const next = () => setImageIndex((i) => (i + 1) % total)

  return (
    <article
      className={`flex flex-col border border-gray-300 ${inactivo ? 'bg-gray-50 opacity-85' : ''}`}
    >
      <div className="relative w-full bg-gray-100" style={{ aspectRatio: '1' }}>
        {total > 0 ? (
          <>
            <img
              src={imagenes[imageIndex]}
              alt={`${producto.nombre} ${imageIndex + 1}`}
              className="h-full w-full object-cover"
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
                  className="absolute left-1 top-1/2 -translate-y-1/2 border border-gray-400 bg-white px-2 py-0.5 text-sm"
                >
                  ‹
                </button>
                <button
                  type="button"
                  onClick={next}
                  aria-label="Imagen siguiente"
                  className="absolute right-1 top-1/2 -translate-y-1/2 border border-gray-400 bg-white px-2 py-0.5 text-sm"
                >
                  ›
                </button>
                <span className="absolute bottom-1 right-1 bg-white border border-gray-300 px-1.5 text-xs">
                  {imageIndex + 1} / {total}
                </span>
              </>
            )}
          </>
        ) : (
          <div className="flex h-full w-full items-center justify-center text-xs text-gray-400">
            sin imagen
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-2 p-3">
        <div className="flex items-start justify-between gap-2">
          <Link
            to={`/productos/${producto.id}`}
            className={`text-base font-semibold underline ${inactivo ? 'text-gray-600' : ''}`}
          >
            {producto.nombre}
          </Link>
          <span className="shrink-0 text-xs text-gray-600">
            {inactivo
              ? 'Desactivado'
              : producto.disponible
                ? 'Disponible'
                : 'No disponible'}
          </span>
        </div>

        {producto.descripcion && (
          <p className="text-sm text-gray-600">{producto.descripcion}</p>
        )}

        <div className="mt-auto flex items-center justify-between pt-2 text-sm">
          <span className="font-semibold">${producto.precio_base}</span>
          <span className="text-xs text-gray-500">Stock: {producto.stock_cantidad}</span>
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={() => onEdit(producto)}
            disabled={inactivo}
            className="border border-gray-400 px-3 py-1 text-xs disabled:cursor-not-allowed disabled:opacity-50"
          >
            Editar
          </button>
          <button
            type="button"
            onClick={() => onDelete(producto)}
            disabled={inactivo}
            className="border border-red-400 px-3 py-1 text-xs text-red-600 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {inactivo ? 'Desactivado' : 'Desactivar'}
          </button>
        </div>
      </div>
    </article>
  )
}
