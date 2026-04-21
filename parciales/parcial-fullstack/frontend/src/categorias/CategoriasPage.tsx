import { useState } from "react";

import { ApiError } from "@/lib/apiClient";
import { Button } from "@/shared/components/Button";
import { Modal } from "@/shared/components/Modal";
import { PageHeader } from "@/shared/components/PageHeader";

import { CategoriaForm } from "./components/CategoriaForm";
import { CategoriasTable } from "./components/CategoriasTable";
import {
  useCategorias,
  useCreateCategoria,
  useDeleteCategoria,
  useUpdateCategoria,
} from "./hooks/useCategorias";
import type { Categoria, CategoriaInput } from "./types";

export function CategoriasPage() {
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<Categoria | undefined>();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { data, isLoading, isError, error } = useCategorias();
  const createMutation = useCreateCategoria();
  const updateMutation = useUpdateCategoria();
  const deleteMutation = useDeleteCategoria();

  function openCreate() {
    setEditing(undefined);
    setSubmitError(null);
    setIsOpen(true);
  }

  function openEdit(categoria: Categoria) {
    setEditing(categoria);
    setSubmitError(null);
    setIsOpen(true);
  }

  function handleSubmit(values: CategoriaInput) {
    setSubmitError(null);
    const onError = (err: unknown) => {
      if (err instanceof ApiError) setSubmitError(err.message);
      else setSubmitError("Error al guardar");
    };
    if (editing) {
      updateMutation.mutate(
        { id: editing.id, data: values },
        {
          onSuccess: () => setIsOpen(false),
          onError,
        },
      );
    } else {
      createMutation.mutate(values, {
        onSuccess: () => setIsOpen(false),
        onError,
      });
    }
  }

  function handleDelete(categoria: Categoria) {
    if (!confirm(`¿Eliminar la categoría "${categoria.codigo}"?`)) return;
    deleteMutation.mutate(categoria.id);
  }

  return (
    <div>
      <PageHeader
        title="Categorías"
        description="Gestión del catálogo de categorías."
        action={<Button onClick={openCreate}>Nueva categoría</Button>}
      />

      {isLoading ? (
        <p className="text-sm text-gray-500">Cargando...</p>
      ) : isError ? (
        <p className="text-sm text-red-600">
          Error: {error instanceof Error ? error.message : "desconocido"}
        </p>
      ) : (
        <CategoriasTable
          categorias={data ?? []}
          onEdit={openEdit}
          onDelete={handleDelete}
        />
      )}

      <Modal
        open={isOpen}
        title={editing ? "Editar categoría" : "Nueva categoría"}
        onClose={() => setIsOpen(false)}
      >
        <CategoriaForm
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
