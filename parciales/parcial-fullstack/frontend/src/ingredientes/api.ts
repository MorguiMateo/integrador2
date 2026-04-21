import { apiRequest } from "@/lib/apiClient";

import type { Ingrediente, IngredienteInput } from "./types";

export function getIngredientes(): Promise<Ingrediente[]> {
  return apiRequest<Ingrediente[]>("/ingredientes/?limit=100");
}

export function createIngrediente(data: IngredienteInput): Promise<Ingrediente> {
  return apiRequest<Ingrediente>("/ingredientes/", {
    method: "POST",
    body: data,
  });
}

export function updateIngrediente(
  id: number,
  data: IngredienteInput,
): Promise<Ingrediente> {
  return apiRequest<Ingrediente>(`/ingredientes/${id}`, {
    method: "PUT",
    body: data,
  });
}

export function deleteIngrediente(id: number): Promise<void> {
  return apiRequest<void>(`/ingredientes/${id}`, { method: "DELETE" });
}
