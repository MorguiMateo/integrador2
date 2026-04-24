import { apiClient } from '../lib/apiClient'
import type { Ingrediente, IngredienteFormValues } from './ingredientes.types'

const BASE = '/ingredientes'

function listQuery(opts?: { incluirEliminados?: boolean }): string {
  if (!opts?.incluirEliminados) return BASE
  return `${BASE}?incluir_eliminados=true`
}

export const ingredientesApi = {
  list: (opts?: { incluirEliminados?: boolean }) =>
    apiClient.get<Ingrediente[]>(listQuery(opts)),
  get: (id: number) => apiClient.get<Ingrediente>(`${BASE}/${id}`),
  create: (payload: IngredienteFormValues) => apiClient.post<Ingrediente>(BASE, payload),
  update: (id: number, payload: IngredienteFormValues) =>
    apiClient.put<Ingrediente>(`${BASE}/${id}`, payload),
  remove: (id: number) => apiClient.delete<void>(`${BASE}/${id}`),
}
