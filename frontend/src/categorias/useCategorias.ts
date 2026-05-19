import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { categoriasApi } from './categorias.api'
import type { CategoriaFormValues } from './categorias.types'

//"La query key identifica la caché; y uso la misma key para invalidar."
const LIST_ROOT = 'categorias' as const

export function useCategorias(opts?: { incluirEliminados?: boolean }) {
  const incluir = opts?.incluirEliminados ?? false
  return useQuery({
    queryKey: [LIST_ROOT, incluir] as const,
    queryFn: () => categoriasApi.list({ incluirEliminados: incluir }),
  })
}

export function useCreateCategoria() {
  const qc = useQueryClient()
  return useMutation({
    // hHace el POST
    mutationFn: (values: CategoriaFormValues) => categoriasApi.create(values),
    // Al crear con éxito, marcamos la lista como stale y se refetchea sola
    onSuccess: () => qc.invalidateQueries({ queryKey: [LIST_ROOT] }),
  })
}

export function useUpdateCategoria() {
  const qc = useQueryClient()
  return useMutation({
    //  hace el PUT
    mutationFn: ({ id, values }: { id: number; values: CategoriaFormValues }) =>
      categoriasApi.update(id, values),
    // Al actualizar con éxito, marcamos la lista como stale y se refetchea sola
    onSuccess: () => qc.invalidateQueries({ queryKey: [LIST_ROOT] }),
  })
}

export function useDeleteCategoria() {
  const qc = useQueryClient()
  return useMutation({
    //  hace el DELETE
    mutationFn: (id: number) => categoriasApi.remove(id),
    // Al borrar con éxito, marcamos la lista como stale y se refetchea sola
    onSuccess: () => qc.invalidateQueries({ queryKey: [LIST_ROOT] }),
  })
}
