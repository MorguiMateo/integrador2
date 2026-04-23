import { useEffect, useState } from 'react'
import type { SyntheticEvent } from 'react'

import type { Categoria, CategoriaFormValues } from '../categorias.types'
import { Modal } from '../../shared/components/Modal'

interface CategoriaModalProps {
  open: boolean
  initialValue?: Categoria | null
  onClose: () => void
  onSubmit: (values: CategoriaFormValues) => void
}

const EMPTY: CategoriaFormValues = {
  nombre: '',
  descripcion: null,
  imagen_url: null,
  parent_id: null,
}

function toFormValues(categoria: Categoria | null | undefined): CategoriaFormValues {
  if (!categoria) return EMPTY
  return {
    nombre: categoria.nombre,
    descripcion: categoria.descripcion,
    imagen_url: categoria.imagen_url,
    parent_id: categoria.parent_id,
  }
}

export function CategoriaModal({ open, initialValue, onClose, onSubmit }: CategoriaModalProps) {
  const [values, setValues] = useState<CategoriaFormValues>(() => toFormValues(initialValue))
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open) {
      setValues(toFormValues(initialValue))
      setError(null)
    }
  }, [open, initialValue])

  const handleSubmit = (event: SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (values.nombre.trim().length < 2) {
      setError('El nombre debe tener al menos 2 caracteres.')
      return
    }
    onSubmit({
      ...values,
      nombre: values.nombre.trim(),
      descripcion: values.descripcion?.trim() || null,
      imagen_url: values.imagen_url?.trim() || null,
    })
  }

  return (
    <Modal
      open={open}
      title={initialValue ? 'Editar categoría' : 'Nueva categoría'}
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="categoria-nombre">
            Nombre
          </label>
          <input
            id="categoria-nombre"
            type="text"
            value={values.nombre}
            onChange={(e) => setValues((prev) => ({ ...prev, nombre: e.target.value }))}
            className="w-full border border-gray-300 px-3 py-2 text-sm"
            autoFocus
          />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="categoria-descripcion">
            Descripción
          </label>
          <textarea
            id="categoria-descripcion"
            value={values.descripcion ?? ''}
            onChange={(e) =>
              setValues((prev) => ({ ...prev, descripcion: e.target.value || null }))
            }
            className="w-full border border-gray-300 px-3 py-2 text-sm"
            rows={3}
          />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="categoria-imagen">
            URL de imagen
          </label>
          <input
            id="categoria-imagen"
            type="url"
            value={values.imagen_url ?? ''}
            onChange={(e) =>
              setValues((prev) => ({ ...prev, imagen_url: e.target.value || null }))
            }
            className="w-full border border-gray-300 px-3 py-2 text-sm"
            placeholder="https://..."
          />
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
