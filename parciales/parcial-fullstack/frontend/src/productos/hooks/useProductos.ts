import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createProducto,
  deleteProducto,
  getProducto,
  getProductos,
  updateProducto,
} from "@/productos/api";
import type { Producto, ProductoInput } from "@/productos/types";

const LIST_KEY = ["productos"] as const;
const detailKey = (id: number) => ["productos", id] as const;

export function useProductos() {
  return useQuery<Producto[]>({
    queryKey: LIST_KEY,
    queryFn: getProductos,
  });
}

export function useProducto(id: number | undefined) {
  return useQuery<Producto>({
    queryKey: id ? detailKey(id) : ["productos", "none"],
    queryFn: () => getProducto(id as number),
    enabled: typeof id === "number" && !Number.isNaN(id),
  });
}

export function useCreateProducto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProductoInput) => createProducto(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LIST_KEY });
    },
  });
}

export function useUpdateProducto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductoInput }) =>
      updateProducto(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: LIST_KEY });
      queryClient.invalidateQueries({ queryKey: detailKey(variables.id) });
    },
  });
}

export function useDeleteProducto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteProducto(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LIST_KEY });
    },
  });
}
