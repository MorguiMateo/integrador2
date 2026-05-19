import { apiClient } from '../lib/apiClient'
import type { Categoria, CategoriaFormValues } from './categorias.types'

const BASE = '/categorias'

function listQuery(opts?: { incluirEliminados?: boolean }): string {
  if (!opts?.incluirEliminados) return BASE
  return `${BASE}?incluir_eliminados=true`
}

export const categoriasApi = {
  list: (opts?: { incluirEliminados?: boolean }) =>
    apiClient.get<Categoria[]>(listQuery(opts)),
  get: (id: number) => apiClient.get<Categoria>(`${BASE}/${id}`),
  create: (payload: CategoriaFormValues) => apiClient.post<Categoria>(BASE, payload),
  update: (id: number, payload: CategoriaFormValues) =>
    apiClient.put<Categoria>(`${BASE}/${id}`, payload),
  remove: (id: number) => apiClient.delete<void>(`${BASE}/${id}`),
}
