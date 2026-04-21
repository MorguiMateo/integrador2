import type { Producto, ProductoFormValues } from '../productos.types'
import { Modal } from '../../shared/components/Modal'

interface ProductoModalProps {
  open: boolean
  initialValue?: Producto | null
  onClose: () => void
  onSubmit: (values: ProductoFormValues) => void
}

export function ProductoModal({ open, initialValue, onClose, onSubmit }: ProductoModalProps) {
  void initialValue
  void onSubmit
  return (
    <Modal
      open={open}
      title={initialValue ? 'Editar producto' : 'Nuevo producto'}
      onClose={onClose}
    >
      <p className="text-sm text-slate-500">
        TODO: formulario con selector múltiple de categorías y filas de
        ingredientes (cantidad + unidad).
      </p>
    </Modal>
  )
}
