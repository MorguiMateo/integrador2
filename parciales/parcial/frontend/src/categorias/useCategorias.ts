import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { categoriasApi } from './categorias.api'
import type { CategoriaFormValues } from './categorias.types'

const LIST_KEY = ['categorias'] as const

export function useCategorias() {
  return useQuery({ queryKey: LIST_KEY, queryFn: categoriasApi.list })
}

export function useCreateCategoria() {
  // Accedemos al QueryClient global para poder invalidar queries luego
  const qc = useQueryClient()
  return useMutation({
    // Función que se dispara al llamar mutation.mutate(values): hace el POST
    mutationFn: (values: CategoriaFormValues) => categoriasApi.create(values),
    // Al crear con éxito, marcamos la lista como stale y se refetchea sola
    onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
  })
}

export function useUpdateCategoria() {
  // Accedemos al QueryClient global para poder invalidar queries luego
  const qc = useQueryClient()
  return useMutation({
    // Recibe un objeto { id, values } porque mutate() solo acepta 1 argumento: hace el PUT
    mutationFn: ({ id, values }: { id: number; values: CategoriaFormValues }) =>
      categoriasApi.update(id, values),
    // Al actualizar con éxito, marcamos la lista como stale y se refetchea sola
    onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
  })
}

export function useDeleteCategoria() {
  // Accedemos al QueryClient global para poder invalidar queries luego
  const qc = useQueryClient()
  return useMutation({
    // Recibe solo el id de la categoría a borrar: hace el DELETE
    mutationFn: (id: number) => categoriasApi.remove(id),
    // Al borrar con éxito, marcamos la lista como stale y se refetchea sola
    onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
  })
}
