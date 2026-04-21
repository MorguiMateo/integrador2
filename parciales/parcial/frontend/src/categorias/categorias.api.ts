import { apiClient } from '../lib/apiClient'
import type { Categoria, CategoriaFormValues } from './categorias.types'

const BASE = '/categorias'

export const categoriasApi = {
  list: () => apiClient.get<Categoria[]>(BASE),
  get: (id: number) => apiClient.get<Categoria>(`${BASE}/${id}`),
  create: (payload: CategoriaFormValues) => apiClient.post<Categoria>(BASE, payload),
  update: (id: number, payload: CategoriaFormValues) =>
    apiClient.put<Categoria>(`${BASE}/${id}`, payload),
  remove: (id: number) => apiClient.delete<void>(`${BASE}/${id}`),
}
