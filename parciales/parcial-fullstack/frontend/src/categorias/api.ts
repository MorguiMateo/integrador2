import { apiRequest } from "@/lib/apiClient";

import type { Categoria, CategoriaInput } from "./types";

export function getCategorias(): Promise<Categoria[]> {
  return apiRequest<Categoria[]>("/categorias/?limit=100");
}

export function createCategoria(data: CategoriaInput): Promise<Categoria> {
  return apiRequest<Categoria>("/categorias/", { method: "POST", body: data });
}

export function updateCategoria(
  id: number,
  data: CategoriaInput,
): Promise<Categoria> {
  return apiRequest<Categoria>(`/categorias/${id}`, {
    method: "PUT",
    body: data,
  });
}

export function deleteCategoria(id: number): Promise<void> {
  return apiRequest<void>(`/categorias/${id}`, { method: "DELETE" });
}
