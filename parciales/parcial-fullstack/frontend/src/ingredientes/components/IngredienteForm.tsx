import { useEffect, useState } from "react";

import { Button } from "@/shared/components/Button";
import { InputField, TextareaField } from "@/shared/components/Input";

import type { Ingrediente, IngredienteInput } from "../types";

interface IngredienteFormProps {
  initial?: Ingrediente;
  onSubmit: (data: IngredienteInput) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
  submitError?: string | null;
}

const defaultValues: IngredienteInput = {
  nombre: "",
  descripcion: "",
  es_alergeno: false,
  activo: true,
};

export function IngredienteForm({
  initial,
  onSubmit,
  onCancel,
  isSubmitting,
  submitError,
}: IngredienteFormProps) {
  const [values, setValues] = useState<IngredienteInput>(defaultValues);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (initial) {
      setValues({
        nombre: initial.nombre,
        descripcion: initial.descripcion ?? "",
        es_alergeno: initial.es_alergeno,
        activo: initial.activo,
      });
    } else {
      setValues(defaultValues);
    }
    setErrors({});
  }, [initial]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const newErrors: Record<string, string> = {};
    if (values.nombre.trim().length < 2) {
      newErrors.nombre = "Mínimo 2 caracteres";
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
        value={values.descripcion ?? ""}
        rows={2}
        onChange={(e) =>
          setValues({ ...values, descripcion: e.target.value })
        }
      />
      <label className="flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          checked={values.es_alergeno}
          onChange={(e) =>
            setValues({ ...values, es_alergeno: e.target.checked })
          }
        />
        Es alérgeno
      </label>
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
