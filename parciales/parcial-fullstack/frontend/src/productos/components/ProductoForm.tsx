import { useEffect, useState } from "react";

import { useCategorias } from "@/categorias/hooks/useCategorias";
import { useIngredientes } from "@/ingredientes/hooks/useIngredientes";
import { Button } from "@/shared/components/Button";
import { InputField, TextareaField } from "@/shared/components/Input";

import type {
  IngredienteInputItem,
  Producto,
  ProductoInput,
} from "../types";

interface ProductoFormProps {
  initial?: Producto;
  onSubmit: (data: ProductoInput) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
  submitError?: string | null;
}

const defaultValues: ProductoInput = {
  nombre: "",
  descripcion: "",
  precio: 0,
  stock: 0,
  activo: true,
  categoria_ids: [],
  ingredientes: [],
};

export function ProductoForm({
  initial,
  onSubmit,
  onCancel,
  isSubmitting,
  submitError,
}: ProductoFormProps) {
  const [values, setValues] = useState<ProductoInput>(defaultValues);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const categoriasQuery = useCategorias();
  const ingredientesQuery = useIngredientes();

  useEffect(() => {
    if (initial) {
      setValues({
        nombre: initial.nombre,
        descripcion: initial.descripcion ?? "",
        precio: initial.precio,
        stock: initial.stock,
        activo: initial.activo,
        categoria_ids: initial.categorias.map((c) => c.id),
        ingredientes: initial.ingredientes.map((i) => ({
          ingrediente_id: i.ingrediente.id,
          cantidad: i.cantidad,
          unidad: i.unidad,
        })),
      });
    } else {
      setValues(defaultValues);
    }
    setErrors({});
  }, [initial]);

  function toggleCategoria(id: number) {
    setValues((v) => ({
      ...v,
      categoria_ids: v.categoria_ids.includes(id)
        ? v.categoria_ids.filter((x) => x !== id)
        : [...v.categoria_ids, id],
    }));
  }

  function addIngrediente() {
    setValues((v) => ({
      ...v,
      ingredientes: [
        ...v.ingredientes,
        { ingrediente_id: 0, cantidad: 1, unidad: "unidad" },
      ],
    }));
  }

  function updateIngrediente(
    index: number,
    patch: Partial<IngredienteInputItem>,
  ) {
    setValues((v) => ({
      ...v,
      ingredientes: v.ingredientes.map((it, i) =>
        i === index ? { ...it, ...patch } : it,
      ),
    }));
  }

  function removeIngrediente(index: number) {
    setValues((v) => ({
      ...v,
      ingredientes: v.ingredientes.filter((_, i) => i !== index),
    }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const newErrors: Record<string, string> = {};
    if (values.nombre.trim().length < 2) {
      newErrors.nombre = "Mínimo 2 caracteres";
    }
    if (values.precio <= 0) {
      newErrors.precio = "Debe ser mayor a 0";
    }
    if (values.stock < 0) {
      newErrors.stock = "No puede ser negativo";
    }
    if (
      values.ingredientes.some(
        (i) => i.ingrediente_id <= 0 || i.cantidad <= 0,
      )
    ) {
      newErrors.ingredientes = "Completá todos los ingredientes";
    }
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    onSubmit({
      ...values,
      descripcion: values.descripcion?.trim() ? values.descripcion : null,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <InputField
        id="nombre"
        label="Nombre"
        value={values.nombre}
        onChange={(e) => setValues({ ...values, nombre: e.target.value })}
        error={errors.nombre}
      />
      <TextareaField
        id="descripcion"
        label="Descripción"
        rows={2}
        value={values.descripcion ?? ""}
        onChange={(e) =>
          setValues({ ...values, descripcion: e.target.value })
        }
      />
      <div className="grid grid-cols-2 gap-3">
        <InputField
          id="precio"
          label="Precio"
          type="number"
          step="0.01"
          min={0}
          value={values.precio}
          onChange={(e) =>
            setValues({ ...values, precio: Number(e.target.value) })
          }
          error={errors.precio}
        />
        <InputField
          id="stock"
          label="Stock"
          type="number"
          min={0}
          value={values.stock}
          onChange={(e) =>
            setValues({ ...values, stock: Number(e.target.value) })
          }
          error={errors.stock}
        />
      </div>

      <div>
        <p className="text-xs font-medium text-gray-600 mb-1">Categorías</p>
        {categoriasQuery.isLoading ? (
          <p className="text-xs text-gray-500">Cargando categorías...</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {(categoriasQuery.data ?? []).map((c) => {
              const selected = values.categoria_ids.includes(c.id);
              return (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => toggleCategoria(c.id)}
                  className={[
                    "text-xs px-2 py-1 rounded border transition-colors duration-200",
                    selected
                      ? "bg-gray-900 text-white border-gray-900"
                      : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50",
                  ].join(" ")}
                >
                  {c.codigo}
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div>
        <div className="flex items-center justify-between mb-1">
          <p className="text-xs font-medium text-gray-600">Ingredientes</p>
          <Button
            type="button"
            variant="ghost"
            onClick={addIngrediente}
            disabled={ingredientesQuery.isLoading}
          >
            + Agregar
          </Button>
        </div>
        {values.ingredientes.length === 0 ? (
          <p className="text-xs text-gray-500">Sin ingredientes.</p>
        ) : (
          <div className="flex flex-col gap-2">
            {values.ingredientes.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 border border-gray-200 rounded p-2"
              >
                <select
                  value={item.ingrediente_id}
                  onChange={(e) =>
                    updateIngrediente(idx, {
                      ingrediente_id: Number(e.target.value),
                    })
                  }
                  className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
                >
                  <option value={0}>Seleccionar...</option>
                  {(ingredientesQuery.data ?? []).map((ing) => (
                    <option key={ing.id} value={ing.id}>
                      {ing.nombre}
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  step="0.01"
                  min={0}
                  value={item.cantidad}
                  onChange={(e) =>
                    updateIngrediente(idx, {
                      cantidad: Number(e.target.value),
                    })
                  }
                  className="w-20 border border-gray-300 rounded px-2 py-1 text-sm"
                  placeholder="Cant."
                />
                <input
                  type="text"
                  value={item.unidad}
                  onChange={(e) =>
                    updateIngrediente(idx, { unidad: e.target.value })
                  }
                  className="w-24 border border-gray-300 rounded px-2 py-1 text-sm"
                  placeholder="Unidad"
                />
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => removeIngrediente(idx)}
                >
                  ✕
                </Button>
              </div>
            ))}
          </div>
        )}
        {errors.ingredientes ? (
          <p className="text-xs text-red-600 mt-1">{errors.ingredientes}</p>
        ) : null}
      </div>

      <label className="flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          checked={values.activo}
          onChange={(e) => setValues({ ...values, activo: e.target.checked })}
        />
        Activo
      </label>

      {submitError ? (
        <p className="text-xs text-red-600">{submitError}</p>
      ) : null}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Guardando..." : "Guardar"}
        </Button>
      </div>
    </form>
  );
}
