import { useMemo, useState } from 'react'

import type { Producto, ProductoFilters, ProductoFormValues } from './productos.types'
import { ProductoCard } from './components/ProductoCard'
import { ProductoModal } from './components/ProductoModal'
import {
  useCreateProducto,
  useDeleteProducto,
  useProductos,
  useUpdateProducto,
} from './useProductos'

export function ProductosPage() {
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Producto | null>(null)
  const [search, setSearch] = useState('')
  const [soloDisponibles, setSoloDisponibles] = useState(false)

  const filters = useMemo<ProductoFilters>(() => {
    const f: ProductoFilters = {}
    if (search.trim()) f.q = search.trim()
    if (soloDisponibles) f.disponible = true
    return f
  }, [search, soloDisponibles])

  const { data, isLoading, isError, error } = useProductos(filters)
  const createMutation = useCreateProducto()
  const updateMutation = useUpdateProducto()
  const deleteMutation = useDeleteProducto()

  const items: Producto[] = data ?? []

  const openNew = () => {
    setEditing(null)
    setModalOpen(true)
  }

  const openEdit = (producto: Producto) => {
    setEditing(producto)
    setModalOpen(true)
  }

  const handleClose = () => setModalOpen(false)

  const handleSubmit = (values: ProductoFormValues) => {
    if (editing) {
      updateMutation.mutate(
        { id: editing.id, values },
        { onSuccess: () => setModalOpen(false) },
      )
    } else {
      createMutation.mutate(values, { onSuccess: () => setModalOpen(false) })
    }
  }

  const handleDelete = (producto: Producto) => {
    if (!confirm(`¿Borrar el producto "${producto.nombre}"?`)) return
    deleteMutation.mutate(producto.id)
  }

  const mutationError =
    createMutation.error ?? updateMutation.error ?? deleteMutation.error

  return (
    <section className="space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Productos</h1>
        <button
          type="button"
          onClick={openNew}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Nuevo producto
        </button>
      </header>

      <div className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white p-3">
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por nombre..."
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
        />
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={soloDisponibles}
            onChange={(e) => setSoloDisponibles(e.target.checked)}
            className="h-4 w-4 rounded border-slate-300"
          />
          Solo disponibles
        </label>
      </div>

      {isLoading && (
        <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">
          Cargando…
        </div>
      )}

      {isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Error al cargar productos: {error instanceof Error ? error.message : 'desconocido'}
        </div>
      )}

      {mutationError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Error al guardar: {mutationError instanceof Error ? mutationError.message : 'desconocido'}
        </div>
      )}

      {!isLoading && !isError && (
        items.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
            No hay productos cargados.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {items.map((producto) => (
              <ProductoCard
                key={producto.id}
                producto={producto}
                onEdit={openEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )
      )}

      <ProductoModal
        open={modalOpen}
        initialValue={editing}
        onClose={handleClose}
        onSubmit={handleSubmit}
      />
    </section>
  )
}
