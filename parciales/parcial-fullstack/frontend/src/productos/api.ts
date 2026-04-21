import { apiRequest } from "@/lib/apiClient";

import type { Producto, ProductoInput } from "./types";

export function getProductos(): Promise<Producto[]> {
  return apiRequest<Producto[]>("/productos/?limit=100");
}

export function getProducto(id: number): Promise<Producto> {
  return apiRequest<Producto>(`/productos/${id}`);
}

export function createProducto(data: ProductoInput): Promise<Producto> {
  return apiRequest<Producto>("/productos/", { method: "POST", body: data });
}

export function updateProducto(
  id: number,
  data: ProductoInput,
): Promise<Producto> {
  return apiRequest<Producto>(`/productos/${id}`, {
    method: "PUT",
    body: data,
  });
}

export function deleteProducto(id: number): Promise<void> {
  return apiRequest<void>(`/productos/${id}`, { method: "DELETE" });
}
