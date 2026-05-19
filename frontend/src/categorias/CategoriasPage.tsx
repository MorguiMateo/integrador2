import { useState } from 'react'

import type { Categoria, CategoriaFormValues } from './categorias.types'
import { CategoriaModal } from './components/CategoriaModal'
import { CategoriaTable } from './components/CategoriaTable'
import {
  useCategorias,
  useCreateCategoria,
  useDeleteCategoria,
  useUpdateCategoria,
} from './useCategorias'

export function CategoriasPage() {
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Categoria | null>(null)

  const { data, isLoading, isError, error } = useCategorias({ incluirEliminados: true })
  const createMutation = useCreateCategoria()
  const updateMutation = useUpdateCategoria()
  const deleteMutation = useDeleteCategoria()

  const items: Categoria[] = data ?? []

  const openNew = () => {
    setEditing(null)
    setModalOpen(true)
  }

  const openEdit = (categoria: Categoria) => {
    if (categoria.eliminado) return
    setEditing(categoria)
    setModalOpen(true)
  }

  const handleClose = () => setModalOpen(false)

  const handleSubmit = (values: CategoriaFormValues) => {
    if (editing) {
      updateMutation.mutate(
        { id: editing.id, values },
        { onSuccess: () => setModalOpen(false) },
      )
    } else {
      createMutation.mutate(values, { onSuccess: () => setModalOpen(false) })
    }
  }

  const handleDelete = (categoria: Categoria) => {
    if (categoria.eliminado) return
    if (!confirm(`¿Desactivar la categoría "${categoria.nombre}"? (soft delete)`)) return
    deleteMutation.mutate(categoria.id)
  }

  const mutationError =
    createMutation.error ?? updateMutation.error ?? deleteMutation.error

  return (
    <section className="space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Categorías</h1>
        <button
          type="button"
          onClick={openNew}
          className="border border-gray-400 bg-blue-600 px-4 py-2 text-sm text-white"
        >
          Nueva categoría
        </button>
      </header>

      {isLoading && (
        <div className="border border-gray-300 p-4 text-sm text-gray-500">
          Cargando…
        </div>
      )}

      {isError && (
        <div className="border border-red-400 p-4 text-sm text-red-700">
          Error al cargar categorías: {error instanceof Error ? error.message : 'desconocido'}
        </div>
      )}

      {mutationError && (
        <div className="border border-red-400 p-4 text-sm text-red-700">
          Error al guardar: {mutationError instanceof Error ? mutationError.message : 'desconocido'}
        </div>
      )}

      {!isLoading && !isError && (
        <CategoriaTable items={items} onEdit={openEdit} onDelete={handleDelete} />
      )}

      {/* Modal controlado: su visibilidad y datos dependen del estado de la página */}
      <CategoriaModal
        // Booleano que muestra/oculta el modal (controlado por setModalOpen)
        open={modalOpen}
        // Si hay categoría en edición, el form se precarga; si es null, es creación
        initialValue={editing}
        // Callback al cerrar (cancelar o clic afuera): setModalOpen(false)
        onClose={handleClose}
        // Al enviar el form decide si llama a updateMutation o createMutation
        onSubmit={handleSubmit}
      />
    </section>
  )
}
