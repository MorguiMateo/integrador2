import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { ingredientesApi } from './ingredientes.api'
import type { IngredienteFormValues } from './ingredientes.types'

const LIST_KEY = ['ingredientes'] as const

export function useIngredientes() {
  return useQuery({ queryKey: LIST_KEY, queryFn: ingredientesApi.list })
}

export function useCreateIngrediente() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (values: IngredienteFormValues) => ingredientesApi.create(values),
    onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
  })
}

export function useUpdateIngrediente() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, values }: { id: number; values: IngredienteFormValues }) =>
      ingredientesApi.update(id, values),
    onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
  })
}

export function useDeleteIngrediente() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => ingredientesApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
  })
}
