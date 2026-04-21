import { useState } from "react";

import { ApiError } from "@/lib/apiClient";
import { Button } from "@/shared/components/Button";
import { Modal } from "@/shared/components/Modal";
import { PageHeader } from "@/shared/components/PageHeader";

import { ProductoForm } from "./components/ProductoForm";
import { ProductosTable } from "./components/ProductosTable";
import {
  useCreateProducto,
  useDeleteProducto,
  useProductos,
  useUpdateProducto,
} from "./hooks/useProductos";
import type { Producto, ProductoInput } from "./types";

export function ProductosPage() {
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<Producto | undefined>();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { data, isLoading, isError, error } = useProductos();
  const createMutation = useCreateProducto();
  const updateMutation = useUpdateProducto();
  const deleteMutation = useDeleteProducto();

  function openCreate() {
    setEditing(undefined);
    setSubmitError(null);
    setIsOpen(true);
  }

  function openEdit(producto: Producto) {
    setEditing(producto);
    setSubmitError(null);
    setIsOpen(true);
  }

  function handleSubmit(values: ProductoInput) {
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

  function handleDelete(producto: Producto) {
    if (!confirm(`¿Eliminar el producto "${producto.nombre}"?`)) return;
    deleteMutation.mutate(producto.id);
  }

  return (
    <div>
      <PageHeader
        title="Productos"
        description="Productos con sus categorías e ingredientes."
        action={<Button onClick={openCreate}>Nuevo producto</Button>}
      />

      {isLoading ? (
        <p className="text-sm text-gray-500">Cargando...</p>
      ) : isError ? (
        <p className="text-sm text-red-600">
          Error: {error instanceof Error ? error.message : "desconocido"}
        </p>
      ) : (
        <ProductosTable
          productos={data ?? []}
          onEdit={openEdit}
          onDelete={handleDelete}
        />
      )}

      <Modal
        open={isOpen}
        title={editing ? "Editar producto" : "Nuevo producto"}
        onClose={() => setIsOpen(false)}
      >
        <ProductoForm
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
