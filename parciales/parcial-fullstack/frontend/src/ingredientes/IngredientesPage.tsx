import { useState } from "react";

import { ApiError } from "@/lib/apiClient";
import { Button } from "@/shared/components/Button";
import { Modal } from "@/shared/components/Modal";
import { PageHeader } from "@/shared/components/PageHeader";

import { IngredienteForm } from "./components/IngredienteForm";
import { IngredientesTable } from "./components/IngredientesTable";
import {
  useCreateIngrediente,
  useDeleteIngrediente,
  useIngredientes,
  useUpdateIngrediente,
} from "./hooks/useIngredientes";
import type { Ingrediente, IngredienteInput } from "./types";

export function IngredientesPage() {
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<Ingrediente | undefined>();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { data, isLoading, isError, error } = useIngredientes();
  const createMutation = useCreateIngrediente();
  const updateMutation = useUpdateIngrediente();
  const deleteMutation = useDeleteIngrediente();

  function openCreate() {
    setEditing(undefined);
    setSubmitError(null);
    setIsOpen(true);
  }

  function openEdit(ingrediente: Ingrediente) {
    setEditing(ingrediente);
    setSubmitError(null);
    setIsOpen(true);
  }

  function handleSubmit(values: IngredienteInput) {
    setSubmitError(null);
    const onError = (err: unknown) => {
      if (err instanceof ApiError) setSubmitError(err.message);
      else setSubmitError("Error al guardar");
    };
    if (editing) {
      updateMutation.mutate(
        { id: editing.id, data: values },
        { onSuccess: () => setIsOpen(false), onError },
      );
    } else {
      createMutation.mutate(values, {
        onSuccess: () => setIsOpen(false),
        onError,
      });
    }
  }

  function handleDelete(ingrediente: Ingrediente) {
    if (!confirm(`¿Eliminar el ingrediente "${ingrediente.nombre}"?`)) return;
    deleteMutation.mutate(ingrediente.id);
  }

  return (
    <div>
      <PageHeader
        title="Ingredientes"
        description="Listado de ingredientes disponibles para las recetas."
        action={<Button onClick={openCreate}>Nuevo ingrediente</Button>}
      />

      {isLoading ? (
        <p className="text-sm text-gray-500">Cargando...</p>
      ) : isError ? (
        <p className="text-sm text-red-600">
          Error: {error instanceof Error ? error.message : "desconocido"}
        </p>
      ) : (
        <IngredientesTable
          ingredientes={data ?? []}
          onEdit={openEdit}
          onDelete={handleDelete}
        />
      )}

      <Modal
        open={isOpen}
        title={editing ? "Editar ingrediente" : "Nuevo ingrediente"}
        onClose={() => setIsOpen(false)}
      >
        <IngredienteForm
          initial={editing}
          onSubmit={handleSubmit}
          onCancel={() => setIsOpen(false)}
          isSubmitting={
            createMutation.isPending || updateMutation.isPending
          }
          submitError={submitError}
        />
      </Modal>
    </div>
  );
}
