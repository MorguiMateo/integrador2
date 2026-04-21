import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createIngrediente,
  deleteIngrediente,
  getIngredientes,
  updateIngrediente,
} from "@/ingredientes/api";
import type { Ingrediente, IngredienteInput } from "@/ingredientes/types";

const KEY = ["ingredientes"] as const;

export function useIngredientes() {
  return useQuery<Ingrediente[]>({
    queryKey: KEY,
    queryFn: getIngredientes,
  });
}

export function useCreateIngrediente() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: IngredienteInput) => createIngrediente(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: KEY });
    },
  });
}

export function useUpdateIngrediente() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: IngredienteInput }) =>
      updateIngrediente(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: KEY });
    },
  });
}

export function useDeleteIngrediente() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteIngrediente(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: KEY });
      queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}
