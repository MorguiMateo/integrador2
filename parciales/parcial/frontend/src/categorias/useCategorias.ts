import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { categoriasApi } from './categorias.api'
import type { CategoriaFormValues } from './categorias.types'

const LIST_KEY = ['categorias'] as const

export function useCategorias() {
  return useQuery({ queryKey: LIST_KEY, queryFn: categoriasApi.list })
}

export function useCreateCategoria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (values: CategoriaFormValues) => categoriasApi.create(values),
    onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
  })
}

export function useUpdateCategoria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, values }: { id: number; values: CategoriaFormValues }) =>
      categoriasApi.update(id, values),
    onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
  })
}

export function useDeleteCategoria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => categoriasApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
  })
}
