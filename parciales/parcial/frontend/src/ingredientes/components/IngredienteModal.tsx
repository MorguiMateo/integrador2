import type { Ingrediente, IngredienteFormValues } from '../ingredientes.types'
import { Modal } from '../../shared/components/Modal'

interface IngredienteModalProps {
  open: boolean
  initialValue?: Ingrediente | null
  onClose: () => void
  onSubmit: (values: IngredienteFormValues) => void
}

export function IngredienteModal({ open, initialValue, onClose, onSubmit }: IngredienteModalProps) {
  void initialValue
  void onSubmit
  return (
    <Modal
      open={open}
      title={initialValue ? 'Editar ingrediente' : 'Nuevo ingrediente'}
      onClose={onClose}
    >
      <p className="text-sm text-slate-500">TODO: formulario de ingrediente.</p>
    </Modal>
  )
}
