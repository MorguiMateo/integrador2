import type { ReactNode } from 'react'

interface ModalProps {
  open: boolean
  title: string
  onClose: () => void
  children: ReactNode
}

export function Modal({ open, title, onClose, children }: ModalProps) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="flex w-full max-w-lg flex-col border border-gray-300 bg-white max-h-[90vh]">
        <header className="flex shrink-0 items-center justify-between border-b border-gray-300 px-4 py-3">
          <h2 className="text-base font-semibold">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-gray-500"
            aria-label="Cerrar"
          >
            ×
          </button>
        </header>
        <div className="overflow-y-auto px-4 py-4">{children}</div>
      </div>
    </div>
  )
}
