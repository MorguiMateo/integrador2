import { createBrowserRouter, Navigate } from 'react-router-dom'

import App from '../App'
import { CategoriasPage } from '../categorias/CategoriasPage'
import { IngredientesPage } from '../ingredientes/IngredientesPage'
import { ProductosPage } from '../productos/ProductosPage'
import { ProductoDetailPage } from '../productos/ProductoDetailPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Navigate to="/categorias" replace /> },
      { path: 'categorias', element: <CategoriasPage /> },
      { path: 'ingredientes', element: <IngredientesPage /> },
      { path: 'productos', element: <ProductosPage /> },
      //"Acá defino el parámetro id que después leo con useParams()"
      { path: 'productos/:id', element: <ProductoDetailPage /> },
    ],
  },
])
