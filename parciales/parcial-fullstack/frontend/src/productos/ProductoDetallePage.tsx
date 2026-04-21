import { Link, useParams } from "react-router-dom";

import { PageHeader } from "@/shared/components/PageHeader";

import { useProducto } from "./hooks/useProductos";

export function ProductoDetallePage() {
  const { id } = useParams<{ id: string }>();
  const numericId = id ? Number(id) : undefined;
  const { data, isLoading, isError, error } = useProducto(numericId);

  if (!numericId || Number.isNaN(numericId)) {
    return <p className="text-sm text-red-600">ID inválido.</p>;
  }

  if (isLoading) {
    return <p className="text-sm text-gray-500">Cargando...</p>;
  }

  if (isError || !data) {
    return (
      <p className="text-sm text-red-600">
        Error: {error instanceof Error ? error.message : "no encontrado"}
      </p>
    );
  }

  return (
    <div>
      <PageHeader
        title={data.nombre}
        description={data.descripcion ?? "Sin descripción"}
        action={
          <Link to="/productos" className="text-sm text-gray-600 underline">
            Volver
          </Link>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded p-4">
          <p className="text-xs text-gray-500 uppercase">Precio</p>
          <p className="text-lg font-semibold">${data.precio.toFixed(2)}</p>
        </div>
        <div className="bg-white border border-gray-200 rounded p-4">
          <p className="text-xs text-gray-500 uppercase">Stock</p>
          <p className="text-lg font-semibold">{data.stock}</p>
        </div>
        <div className="bg-white border border-gray-200 rounded p-4">
          <p className="text-xs text-gray-500 uppercase">Estado</p>
          <p className="text-lg font-semibold">
            {data.activo ? "Activo" : "Inactivo"}
          </p>
        </div>
      </div>

      <div className="mt-6 bg-white border border-gray-200 rounded p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          Categorías
        </h3>
        {data.categorias.length === 0 ? (
          <p className="text-sm text-gray-500">Sin categorías asignadas.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {data.categorias.map((c) => (
              <span
                key={c.id}
                className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded"
              >
                {c.codigo} — {c.descripcion}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4 bg-white border border-gray-200 rounded p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          Ingredientes
        </h3>
        {data.ingredientes.length === 0 ? (
          <p className="text-sm text-gray-500">Sin ingredientes cargados.</p>
        ) : (
          <ul className="text-sm text-gray-700 flex flex-col gap-1">
            {data.ingredientes.map((item) => (
              <li
                key={item.ingrediente.id}
                className="flex items-center justify-between border-b border-gray-100 py-1"
              >
                <span>
                  {item.ingrediente.nombre}
                  {item.ingrediente.es_alergeno ? (
                    <span className="text-xs text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded ml-2">
                      alérgeno
                    </span>
                  ) : null}
                </span>
                <span className="text-xs text-gray-500">
                  {item.cantidad} {item.unidad}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
