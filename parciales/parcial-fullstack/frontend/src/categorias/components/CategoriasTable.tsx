import { Button } from "@/shared/components/Button";

import type { Categoria } from "../types";

interface CategoriasTableProps {
  categorias: Categoria[];
  onEdit: (categoria: Categoria) => void;
  onDelete: (categoria: Categoria) => void;
}

export function CategoriasTable({
  categorias,
  onEdit,
  onDelete,
}: CategoriasTableProps) {
  if (categorias.length === 0) {
    return (
      <p className="text-sm text-gray-500 text-center py-8">
        No hay categorías cargadas.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto bg-white rounded border border-gray-200">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 text-gray-600">
          <tr>
            <th className="text-left px-3 py-2">Código</th>
            <th className="text-left px-3 py-2">Descripción</th>
            <th className="text-left px-3 py-2">Estado</th>
            <th className="text-right px-3 py-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {categorias.map((categoria) => (
            <tr key={categoria.id} className="border-t border-gray-100">
              <td className="px-3 py-2 font-mono text-xs text-gray-700">
                {categoria.codigo}
              </td>
              <td className="px-3 py-2">{categoria.descripcion}</td>
              <td className="px-3 py-2">
                <span
                  className={
                    categoria.activo
                      ? "text-green-700 bg-green-100 px-2 py-0.5 rounded text-xs"
                      : "text-gray-600 bg-gray-100 px-2 py-0.5 rounded text-xs"
                  }
                >
                  {categoria.activo ? "Activo" : "Inactivo"}
                </span>
              </td>
              <td className="px-3 py-2 text-right">
                <div className="inline-flex gap-2">
                  <Button
                    variant="secondary"
                    onClick={() => onEdit(categoria)}
                  >
                    Editar
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => onDelete(categoria)}
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
