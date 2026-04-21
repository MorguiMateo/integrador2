import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { productosApi } from './productos.api'
import type { ProductoFilters, ProductoFormValues } from './productos.types'

const LIST_KEY = 'productos'

export function useProductos(filters?: ProductoFilters) {
  return useQuery({
    queryKey: [LIST_KEY, filters ?? {}],
    queryFn: () => productosApi.list(filters),
  })
}

export function useProducto(id: number | undefined) {
  return useQuery({
    queryKey: [LIST_KEY, 'detail', id],
    queryFn: () => productosApi.get(id!),
    enabled: id !== undefined,
  })
}

export function useCreateProducto() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (values: ProductoFormValues) => productosApi.create(values),
    onSuccess: () => qc.invalidateQueries({ queryKey: [LIST_KEY] }),
  })
}

export function useUpdateProducto() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, values }: { id: number; values: ProductoFormValues }) =>
      productosApi.update(id, values),
    onSuccess: () => qc.invalidateQueries({ queryKey: [LIST_KEY] }),
  })
}

export function useDeleteProducto() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => productosApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [LIST_KEY] }),
  })
}
