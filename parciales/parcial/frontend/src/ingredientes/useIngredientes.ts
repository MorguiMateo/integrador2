import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { ingredientesApi } from './ingredientes.api'
import type { IngredienteFormValues } from './ingredientes.types'

const LIST_ROOT = 'ingredientes' as const

export function useIngredientes(opts?: { incluirEliminados?: boolean }) {
  const incluir = opts?.incluirEliminados ?? false
  return useQuery({
    queryKey: [LIST_ROOT, incluir] as const,
    queryFn: () => ingredientesApi.list({ incluirEliminados: incluir }),
  })
}

export function useCreateIngrediente() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (values: IngredienteFormValues) => ingredientesApi.create(values),
    onSuccess: () => qc.invalidateQueries({ queryKey: [LIST_ROOT] }),
  })
}

export function useUpdateIngrediente() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, values }: { id: number; values: IngredienteFormValues }) =>
      ingredientesApi.update(id, values),
    onSuccess: () => qc.invalidateQueries({ queryKey: [LIST_ROOT] }),
  })
}

export function useDeleteIngrediente() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => ingredientesApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [LIST_ROOT] }),
  })
}
