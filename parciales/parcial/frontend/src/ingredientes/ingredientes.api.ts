import { apiClient } from '../lib/apiClient'
import type { Ingrediente, IngredienteFormValues } from './ingredientes.types'

const BASE = '/ingredientes'

export const ingredientesApi = {
  list: () => apiClient.get<Ingrediente[]>(BASE),
  get: (id: number) => apiClient.get<Ingrediente>(`${BASE}/${id}`),
  create: (payload: IngredienteFormValues) => apiClient.post<Ingrediente>(BASE, payload),
  update: (id: number, payload: IngredienteFormValues) =>
    apiClient.put<Ingrediente>(`${BASE}/${id}`, payload),
  remove: (id: number) => apiClient.delete<void>(`${BASE}/${id}`),
}
