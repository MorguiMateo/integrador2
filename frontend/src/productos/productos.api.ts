import { apiClient } from '../lib/apiClient'
import type {
  Producto,
  ProductoFilters,
  ProductoFormValues,
} from './productos.types'

const BASE = '/productos'

function toQueryString(filters?: ProductoFilters): string {
  if (!filters) return ''
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value === undefined || value === null || value === '') continue
    if (key === 'incluir_eliminados' && value === false) continue
    params.append(key, String(value))
  }
  const qs = params.toString()
  return qs ? `?${qs}` : ''
}

export const productosApi = {
  list: (filters?: ProductoFilters) =>
    apiClient.get<Producto[]>(`${BASE}${toQueryString(filters)}`),
  get: (id: number) => apiClient.get<Producto>(`${BASE}/${id}`),
  create: (payload: ProductoFormValues) => apiClient.post<Producto>(BASE, payload),
  update: (id: number, payload: ProductoFormValues) =>
    apiClient.put<Producto>(`${BASE}/${id}`, payload),
  remove: (id: number) => apiClient.delete<void>(`${BASE}/${id}`),
}
