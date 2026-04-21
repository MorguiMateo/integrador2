import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createCategoria,
  deleteCategoria,
  getCategorias,
  updateCategoria,
} from "@/categorias/api";
import type { Categoria, CategoriaInput } from "@/categorias/types";


const KEY = ["categorias"] as const;

export function useCategorias() {
  return useQuery<Categoria[]>({
    queryKey: KEY,
    queryFn: getCategorias,
  });
}

export function useCreateCategoria() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CategoriaInput) => createCategoria(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: KEY });
    },
  });
}

export function useUpdateCategoria() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CategoriaInput }) =>
      updateCategoria(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: KEY });
    },
  });
}

export function useDeleteCategoria() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteCategoria(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: KEY });
      queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}
