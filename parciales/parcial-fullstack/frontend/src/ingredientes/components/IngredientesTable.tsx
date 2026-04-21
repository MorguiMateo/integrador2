import { Button } from "@/shared/components/Button";

import type { Ingrediente } from "../types";

interface IngredientesTableProps {
  ingredientes: Ingrediente[];
  onEdit: (ingrediente: Ingrediente) => void;
  onDelete: (ingrediente: Ingrediente) => void;
}

export function IngredientesTable({
  ingredientes,
  onEdit,
  onDelete,
}: IngredientesTableProps) {
  if (ingredientes.length === 0) {
    return (
      <p className="text-sm text-gray-500 text-center py-8">
        No hay ingredientes cargados.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto bg-white rounded border border-gray-200">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 text-gray-600">
          <tr>
            <th className="text-left px-3 py-2">Nombre</th>
            <th className="text-left px-3 py-2">Descripción</th>
            <th className="text-left px-3 py-2">Alérgeno</th>
            <th className="text-left px-3 py-2">Estado</th>
            <th className="text-right px-3 py-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {ingredientes.map((ingrediente) => (
            <tr key={ingrediente.id} className="border-t border-gray-100">
              <td className="px-3 py-2 font-medium">{ingrediente.nombre}</td>
              <td className="px-3 py-2 text-gray-600">
                {ingrediente.descripcion ?? "—"}
              </td>
              <td className="px-3 py-2">
                {ingrediente.es_alergeno ? (
                  <span className="text-amber-700 bg-amber-100 px-2 py-0.5 rounded text-xs">
                    Sí
                  </span>
                ) : (
                  <span className="text-gray-500 text-xs">No</span>
                )}
              </td>
              <td className="px-3 py-2">
                <span
                  className={
                    ingrediente.activo
                      ? "text-green-700 bg-green-100 px-2 py-0.5 rounded text-xs"
                      : "text-gray-600 bg-gray-100 px-2 py-0.5 rounded text-xs"
                  }
                >
                  {ingrediente.activo ? "Activo" : "Inactivo"}
                </span>
              </td>
              <td className="px-3 py-2 text-right">
                <div className="inline-flex gap-2">
                  <Button
                    variant="secondary"
                    onClick={() => onEdit(ingrediente)}
                  >
                    Editar
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => onDelete(ingrediente)}
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
