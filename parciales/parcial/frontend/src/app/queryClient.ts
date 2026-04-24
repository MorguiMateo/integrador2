import { QueryClient } from '@tanstack/react-query'
//parametros
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      //staleTime dice que tienen que pasar 30 segs sin que se vuelva a hacer refetch
      staleTime: 30_000,
      refetchOnWindowFocus: false,
      //retry 1 es que re intente 1 sola vez 
      retry: 1,
    },
  },
})
