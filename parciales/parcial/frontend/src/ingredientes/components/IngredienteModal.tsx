import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import type { Ingrediente, IngredienteFormValues } from '../ingredientes.types'
import { Modal } from '../../shared/components/Modal'

interface IngredienteModalProps {
  open: boolean
  initialValue?: Ingrediente | null
  onClose: () => void
  onSubmit: (values: IngredienteFormValues) => void
}

const EMPTY: IngredienteFormValues = {
  nombre: '',
  descripcion: null,
  es_alergeno: false,
}

function toFormValues(ingrediente: Ingrediente | null | undefined): IngredienteFormValues {
  if (!ingrediente) return EMPTY
  return {
    nombre: ingrediente.nombre,
    descripcion: ingrediente.descripcion,
    es_alergeno: ingrediente.es_alergeno,
  }
}

export function IngredienteModal({
  open,
  initialValue,
  onClose,
  onSubmit,
}: IngredienteModalProps) {
  const [values, setValues] = useState<IngredienteFormValues>(() => toFormValues(initialValue))
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open) {
      setValues(toFormValues(initialValue))
      setError(null)
    }
  }, [open, initialValue])

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (values.nombre.trim().length < 2) {
      setError('El nombre debe tener al menos 2 caracteres.')
      return
    }
    onSubmit({
      ...values,
      nombre: values.nombre.trim(),
      descripcion: values.descripcion?.trim() || null,
    })
  }

  return (
    <Modal
      open={open}
      title={initialValue ? 'Editar ingrediente' : 'Nuevo ingrediente'}
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="ingrediente-nombre">
            Nombre
          </label>
          <input
            id="ingrediente-nombre"
            type="text"
            value={values.nombre}
            onChange={(e) => setValues((prev) => ({ ...prev, nombre: e.target.value }))}
            className="w-full border border-gray-300 px-3 py-2 text-sm"
            autoFocus
          />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="ingrediente-descripcion">
            Descripción
          </label>
          <textarea
            id="ingrediente-descripcion"
            value={values.descripcion ?? ''}
            onChange={(e) =>
              setValues((prev) => ({ ...prev, descripcion: e.target.value || null }))
            }
            className="w-full border border-gray-300 px-3 py-2 text-sm"
            rows={3}
          />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={values.es_alergeno}
            onChange={(e) => setValues((prev) => ({ ...prev, es_alergeno: e.target.checked }))}
          />
          Es alérgeno
        </label>
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
