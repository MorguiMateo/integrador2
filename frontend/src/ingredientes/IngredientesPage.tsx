import { useState } from 'react'

import type { Ingrediente, IngredienteFormValues } from './ingredientes.types'
import { IngredienteModal } from './components/IngredienteModal'
import { IngredienteTable } from './components/IngredienteTable'
import {
  useCreateIngrediente,
  useDeleteIngrediente,
  useIngredientes,
  useUpdateIngrediente,
} from './useIngredientes'

export function IngredientesPage() {
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Ingrediente | null>(null)

  const { data, isLoading, isError, error } = useIngredientes({ incluirEliminados: true })
  const createMutation = useCreateIngrediente()
  const updateMutation = useUpdateIngrediente()
  const deleteMutation = useDeleteIngrediente()

  const items: Ingrediente[] = data ?? []

  const openNew = () => {
    setEditing(null)
    setModalOpen(true)
  }

  const openEdit = (ingrediente: Ingrediente) => {
    if (ingrediente.eliminado) return
    setEditing(ingrediente)
    setModalOpen(true)
  }

  const handleClose = () => setModalOpen(false)

  const handleSubmit = (values: IngredienteFormValues) => {
    if (editing) {
      updateMutation.mutate(
        { id: editing.id, values },
        { onSuccess: () => setModalOpen(false) },
      )
    } else {
      createMutation.mutate(values, { onSuccess: () => setModalOpen(false) })
    }
  }

  const handleDelete = (ingrediente: Ingrediente) => {
    if (ingrediente.eliminado) return
    if (!confirm(`¿Desactivar el ingrediente "${ingrediente.nombre}"? (soft delete)`)) return
    deleteMutation.mutate(ingrediente.id)
  }

  const mutationError =
    createMutation.error ?? updateMutation.error ?? deleteMutation.error

  return (
    <section className="space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Ingredientes</h1>
        <button
          type="button"
          onClick={openNew}
          className="border border-blue-700 bg-blue-600 px-4 py-2 text-sm text-white"
        >
          Nuevo ingrediente
        </button>
      </header>

      {isLoading && (
        <div className="border border-gray-300 p-4 text-sm text-gray-500">
          Cargando…
        </div>
      )}

      {isError && (
        <div className="border border-red-400 p-4 text-sm text-red-700">
          Error al cargar ingredientes: {error instanceof Error ? error.message : 'desconocido'}
        </div>
      )}

      {mutationError && (
        <div className="border border-red-400 p-4 text-sm text-red-700">
          Error al guardar: {mutationError instanceof Error ? mutationError.message : 'desconocido'}
        </div>
      )}

      {!isLoading && !isError && (
        <IngredienteTable items={items} onEdit={openEdit} onDelete={handleDelete} />
      )}

      <IngredienteModal
        open={modalOpen}
        initialValue={editing}
        onClose={handleClose}
        onSubmit={handleSubmit}
      />
    </section>
  )
}
