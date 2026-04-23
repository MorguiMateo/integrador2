import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import type { Producto, ProductoCategoriaInput, ProductoFormValues, ProductoIngredienteInput } from '../productos.types'
import { Modal } from '../../shared/components/Modal'
import { useCategorias } from '../../categorias/useCategorias'
import { useIngredientes } from '../../ingredientes/useIngredientes'

interface ProductoModalProps {
  open: boolean
  initialValue?: Producto | null
  onClose: () => void
  onSubmit: (values: ProductoFormValues) => void
}

const EMPTY: ProductoFormValues = {
  nombre: '',
  descripcion: null,
  precio_base: '0.00',
  imagenes_url: [],
  stock_cantidad: 0,
  disponible: true,
  categorias: [],
  ingredientes: [],
}

function toFormValues(producto: Producto | null | undefined): ProductoFormValues {
  if (!producto) return EMPTY
  return {
    nombre: producto.nombre,
    descripcion: producto.descripcion,
    precio_base: producto.precio_base,
    imagenes_url: producto.imagenes_url,
    stock_cantidad: producto.stock_cantidad,
    disponible: producto.disponible,
    categorias: producto.categorias.map((c) => ({
      categoria_id: c.categoria.id,
      es_principal: c.es_principal,
    })),
    ingredientes: producto.ingredientes.map((i) => ({
      ingrediente_id: i.ingrediente.id,
      es_removible: i.es_removible,
    })),
  }
}

export function ProductoModal({ open, initialValue, onClose, onSubmit }: ProductoModalProps) {
  const [values, setValues] = useState<ProductoFormValues>(() => toFormValues(initialValue))
  const [imagenesText, setImagenesText] = useState<string>(() =>
    toFormValues(initialValue).imagenes_url.join('\n'),
  )
  const [error, setError] = useState<string | null>(null)

  const { data: categorias = [] } = useCategorias()
  const { data: ingredientes = [] } = useIngredientes()

  useEffect(() => {
    if (open) {
      const next = toFormValues(initialValue)
      setValues(next)
      setImagenesText(next.imagenes_url.join('\n'))
      setError(null)
    }
  }, [open, initialValue])

  // ── helpers para la sección de categorías ──────────────────────────────────

  function isCategoriaChecked(id: number) {
    return values.categorias.some((c) => c.categoria_id === id)
  }

  function getCategoriaEntry(id: number): ProductoCategoriaInput | undefined {
    return values.categorias.find((c) => c.categoria_id === id)
  }

  function toggleCategoria(id: number) {
    setValues((prev) => {
      const exists = prev.categorias.some((c) => c.categoria_id === id)
      if (exists) {
        return { ...prev, categorias: prev.categorias.filter((c) => c.categoria_id !== id) }
      }
      return { ...prev, categorias: [...prev.categorias, { categoria_id: id, es_principal: false }] }
    })
  }

  function toggleEsPrincipal(id: number) {
    setValues((prev) => ({
      ...prev,
      categorias: prev.categorias.map((c) =>
        c.categoria_id === id ? { ...c, es_principal: !c.es_principal } : c,
      ),
    }))
  }

  // ── helpers para la sección de ingredientes ────────────────────────────────

  function isIngredienteChecked(id: number) {
    return values.ingredientes.some((i) => i.ingrediente_id === id)
  }

  function getIngredienteEntry(id: number): ProductoIngredienteInput | undefined {
    return values.ingredientes.find((i) => i.ingrediente_id === id)
  }

  function toggleIngrediente(id: number) {
    setValues((prev) => {
      const exists = prev.ingredientes.some((i) => i.ingrediente_id === id)
      if (exists) {
        return { ...prev, ingredientes: prev.ingredientes.filter((i) => i.ingrediente_id !== id) }
      }
      return {
        ...prev,
        ingredientes: [...prev.ingredientes, { ingrediente_id: id, es_removible: false }],
      }
    })
  }

  function toggleEsRemovible(id: number) {
    setValues((prev) => ({
      ...prev,
      ingredientes: prev.ingredientes.map((i) =>
        i.ingrediente_id === id ? { ...i, es_removible: !i.es_removible } : i,
      ),
    }))
  }

  // ── submit ─────────────────────────────────────────────────────────────────

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (values.nombre.trim().length < 2) {
      setError('El nombre debe tener al menos 2 caracteres.')
      return
    }
    const precio = Number(values.precio_base)
    if (Number.isNaN(precio) || precio < 0) {
      setError('El precio debe ser un número no negativo.')
      return
    }
    const imagenes = imagenesText
      .split('\n')
      .map((url) => url.trim())
      .filter(Boolean)

    onSubmit({
      ...values,
      nombre: values.nombre.trim(),
      descripcion: values.descripcion?.trim() || null,
      imagenes_url: imagenes,
    })
  }

  return (
    <Modal
      open={open}
      title={initialValue ? 'Editar producto' : 'Nuevo producto'}
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Nombre */}
        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="producto-nombre">
            Nombre
          </label>
          <input
            id="producto-nombre"
            type="text"
            value={values.nombre}
            onChange={(e) => setValues((prev) => ({ ...prev, nombre: e.target.value }))}
            className="w-full border border-gray-300 px-3 py-2 text-sm"
            autoFocus
          />
        </div>

        {/* Descripción */}
        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="producto-descripcion">
            Descripción
          </label>
          <textarea
            id="producto-descripcion"
            value={values.descripcion ?? ''}
            onChange={(e) =>
              setValues((prev) => ({ ...prev, descripcion: e.target.value || null }))
            }
            className="w-full border border-gray-300 px-3 py-2 text-sm"
            rows={2}
          />
        </div>

        {/* Precio / Stock */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <label className="text-sm font-medium" htmlFor="producto-precio">
              Precio base
            </label>
            <input
              id="producto-precio"
              type="number"
              step="0.01"
              min="0"
              value={values.precio_base}
              onChange={(e) => setValues((prev) => ({ ...prev, precio_base: e.target.value }))}
              className="w-full border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium" htmlFor="producto-stock">
              Stock
            </label>
            <input
              id="producto-stock"
              type="number"
              min="0"
              value={values.stock_cantidad}
              onChange={(e) =>
                setValues((prev) => ({ ...prev, stock_cantidad: Number(e.target.value) || 0 }))
              }
              className="w-full border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
        </div>

        {/* Imágenes */}
        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="producto-imagenes">
            Imágenes (una URL por línea)
          </label>
          <textarea
            id="producto-imagenes"
            value={imagenesText}
            onChange={(e) => setImagenesText(e.target.value)}
            className="w-full border border-gray-300 px-3 py-2 text-sm"
            rows={2}
            placeholder="https://...&#10;https://..."
          />
        </div>

        {/* Disponible */}
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={values.disponible}
            onChange={(e) => setValues((prev) => ({ ...prev, disponible: e.target.checked }))}
          />
          Disponible
        </label>

        {/* ── Categorías ── */}
        <div className="space-y-2">
          <p className="text-sm font-medium">Categorías</p>
          {categorias.length === 0 ? (
            <p className="text-xs text-gray-400">No hay categorías creadas aún.</p>
          ) : (
            <div className="max-h-36 overflow-y-auto border border-gray-300 divide-y divide-gray-200">
              {categorias.map((cat) => {
                const checked = isCategoriaChecked(cat.id)
                const entry = getCategoriaEntry(cat.id)
                return (
                  <div key={cat.id} className="flex items-center justify-between px-3 py-2">
                    <label className="flex items-center gap-2 text-sm cursor-pointer">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleCategoria(cat.id)}
                      />
                      {cat.nombre}
                    </label>
                    {checked && (
                      <label className="flex items-center gap-1 text-xs text-gray-500 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={entry?.es_principal ?? false}
                          onChange={() => toggleEsPrincipal(cat.id)}
                        />
                        principal
                      </label>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* ── Ingredientes ── */}
        <div className="space-y-2">
          <p className="text-sm font-medium">Ingredientes</p>
          {ingredientes.length === 0 ? (
            <p className="text-xs text-gray-400">No hay ingredientes creados aún.</p>
          ) : (
            <div className="max-h-36 overflow-y-auto border border-gray-300 divide-y divide-gray-200">
              {ingredientes.map((ing) => {
                const checked = isIngredienteChecked(ing.id)
                const entry = getIngredienteEntry(ing.id)
                return (
                  <div key={ing.id} className="flex items-center justify-between px-3 py-2">
                    <label className="flex items-center gap-2 text-sm cursor-pointer">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleIngrediente(ing.id)}
                      />
                      <span>
                        {ing.nombre}
                        {ing.es_alergeno && (
                          <span className="ml-1 text-xs text-orange-600">(alérgeno)</span>
                        )}
                      </span>
                    </label>
                    {checked && (
                      <label className="flex items-center gap-1 text-xs text-gray-500 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={entry?.es_removible ?? false}
                          onChange={() => toggleEsRemovible(ing.id)}
                        />
                        removible
                      </label>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="border border-gray-400 px-4 py-2 text-sm"
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="border border-blue-700 bg-blue-600 px-4 py-2 text-sm text-white"
          >
            Guardar
          </button>
        </div>
      </form>
    </Modal>
  )
}
