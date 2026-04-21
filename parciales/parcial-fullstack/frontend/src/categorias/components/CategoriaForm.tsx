import { useEffect, useState } from "react";

import { Button } from "@/shared/components/Button";
import { InputField } from "@/shared/components/Input";

import type { Categoria, CategoriaInput } from "../types";

interface CategoriaFormProps {
  initial?: Categoria;
  onSubmit: (data: CategoriaInput) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
  submitError?: string | null;
}

const defaultValues: CategoriaInput = {
  codigo: "",
  descripcion: "",
  activo: true,
};

export function CategoriaForm({
  initial,
  onSubmit,
  onCancel,
  isSubmitting,
  submitError,
}: CategoriaFormProps) {
  const [values, setValues] = useState<CategoriaInput>(defaultValues);
  const [errors, setErrors] = useState<Partial<Record<keyof CategoriaInput, string>>>(
    {},
  );

  useEffect(() => {
    if (initial) {
      setValues({
        codigo: initial.codigo,
        descripcion: initial.descripcion,
        activo: initial.activo,
      });
    } else {
      setValues(defaultValues);
    }
    setErrors({});
  }, [initial]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const newErrors: Partial<Record<keyof CategoriaInput, string>> = {};
    if (values.codigo.trim().length < 2) {
      newErrors.codigo = "Mínimo 2 caracteres";
    }
    if (values.descripcion.trim().length < 3) {
      newErrors.descripcion = "Mínimo 3 caracteres";
    }
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;
    onSubmit(values);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <InputField
        id="codigo"
        label="Código"
        value={values.codigo}
        onChange={(e) => setValues({ ...values, codigo: e.target.value })}
        error={errors.codigo}
      />
      <InputField
        id="descripcion"
        label="Descripción"
        value={values.descripcion}
        onChange={(e) =>
          setValues({ ...values, descripcion: e.target.value })
        }
        error={errors.descripcion}
      />
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
