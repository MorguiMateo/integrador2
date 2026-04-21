export function ProductosPage() {
  // TODO: listado + filtros + modal + link al detalle /productos/:id
  return (
    <section className="space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Productos</h1>
        <button
          type="button"
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Nuevo producto
        </button>
      </header>
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">
        Módulo pendiente — cablear useQuery + filtros + tabla + modal.
      </div>
    </section>
  )
}
