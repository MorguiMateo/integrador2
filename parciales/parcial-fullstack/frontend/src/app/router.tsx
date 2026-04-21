import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppLayout } from "@/app/AppLayout";
import { CategoriasPage } from "@/categorias/CategoriasPage";
import { IngredientesPage } from "@/ingredientes/IngredientesPage";
import { ProductoDetallePage } from "@/productos/ProductoDetallePage";
import { ProductosPage } from "@/productos/ProductosPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/productos" replace /> },
      { path: "categorias", element: <CategoriasPage /> },
      { path: "ingredientes", element: <IngredientesPage /> },
      { path: "productos", element: <ProductosPage /> },
      { path: "productos/:id", element: <ProductoDetallePage /> },
    ],
  },
]);
