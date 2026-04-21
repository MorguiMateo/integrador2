import { Link, useParams } from 'react-router-dom'

export function ProductoDetailPage() {
  const { id } = useParams<{ id: string }>()
  // TODO: useProducto(Number(id)) y renderizar categorías + ingredientes.
  return (
    <section className="space-y-4">
      <Link to="/productos" className="text-sm text-slate-500 hover:underline">
        ← Volver a productos
      </Link>
      <h1 className="text-2xl font-semibold">Producto #{id}</h1>
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">
        Detalle pendiente — mostrar categorías y ingredientes del producto.
      </div>
    </section>
  )
}
