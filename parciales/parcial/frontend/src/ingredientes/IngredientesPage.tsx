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

  const { data, isLoading, isError, error } = useIngredientes()
  const createMutation = useCreateIngrediente()
  const updateMutation = useUpdateIngrediente()
  const deleteMutation = useDeleteIngrediente()

  const items: Ingrediente[] = data ?? []

  const openNew = () => {
    setEditing(null)
    setModalOpen(true)
  }

  const openEdit = (ingrediente: Ingrediente) => {
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
    if (!confirm(`¿Borrar el ingrediente "${ingrediente.nombre}"?`)) return
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
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Nuevo ingrediente
        </button>
      </header>

      {isLoading && (
        <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">
          Cargando…
        </div>
      )}

      {isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Error al cargar ingredientes: {error instanceof Error ? error.message : 'desconocido'}
        </div>
      )}

      {mutationError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
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
