import { Link } from "react-router-dom";

import { Button } from "@/shared/components/Button";

import type { Producto } from "../types";

interface ProductosTableProps {
  productos: Producto[];
  onEdit: (producto: Producto) => void;
  onDelete: (producto: Producto) => void;
}

export function ProductosTable({
  productos,
  onEdit,
  onDelete,
}: ProductosTableProps) {
  if (productos.length === 0) {
    return (
      <p className="text-sm text-gray-500 text-center py-8">
        No hay productos cargados.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto bg-white rounded border border-gray-200">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 text-gray-600">
          <tr>
            <th className="text-left px-3 py-2">Nombre</th>
            <th className="text-left px-3 py-2">Precio</th>
            <th className="text-left px-3 py-2">Stock</th>
            <th className="text-left px-3 py-2">Categorías</th>
            <th className="text-left px-3 py-2">Estado</th>
            <th className="text-right px-3 py-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {productos.map((producto) => (
            <tr key={producto.id} className="border-t border-gray-100">
              <td className="px-3 py-2 font-medium">
                <Link
                  to={`/productos/${producto.id}`}
                  className="text-gray-800 hover:underline"
                >
                  {producto.nombre}
                </Link>
              </td>
              <td className="px-3 py-2">${producto.precio.toFixed(2)}</td>
              <td className="px-3 py-2">{producto.stock}</td>
              <td className="px-3 py-2">
                <div className="flex flex-wrap gap-1">
                  {producto.categorias.length === 0 ? (
                    <span className="text-xs text-gray-400">—</span>
                  ) : (
                    producto.categorias.map((c) => (
                      <span
                        key={c.id}
                        className="text-xs bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded"
                      >
                        {c.codigo}
                      </span>
                    ))
                  )}
                </div>
              </td>
              <td className="px-3 py-2">
                <span
                  className={
                    producto.activo
                      ? "text-green-700 bg-green-100 px-2 py-0.5 rounded text-xs"
                      : "text-gray-600 bg-gray-100 px-2 py-0.5 rounded text-xs"
                  }
                >
                  {producto.activo ? "Activo" : "Inactivo"}
                </span>
              </td>
              <td className="px-3 py-2 text-right">
                <div className="inline-flex gap-2">
                  <Button
                    variant="secondary"
                    onClick={() => onEdit(producto)}
                  >
                    Editar
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => onDelete(producto)}
                  >
                    Eliminar
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
