import type { Categoria, CategoriaFormValues } from '../categorias.types'
import { Modal } from '../../shared/components/Modal'

interface CategoriaModalProps {
  open: boolean
  initialValue?: Categoria | null
  onClose: () => void
  onSubmit: (values: CategoriaFormValues) => void
}

export function CategoriaModal({ open, initialValue, onClose, onSubmit }: CategoriaModalProps) {
  // TODO: formulario controlado con useState + validación.
  void initialValue
  void onSubmit
  return (
    <Modal
      open={open}
      title={initialValue ? 'Editar categoría' : 'Nueva categoría'}
      onClose={onClose}
    >
      <p className="text-sm text-slate-500">TODO: formulario de categoría.</p>
    </Modal>
  )
}
