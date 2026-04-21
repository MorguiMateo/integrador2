# Lista de Verificación del Proyecto Integrador

## Backend (FastAPI + SQLModel)

- [x] Entorno: `.venv`, `requirements.txt` y FastAPI funcionando en modo dev.
- [x] Modelado: tablas creadas con SQLModel incluyendo relaciones `Relationship` (1:N y N:N).
- [x] Validación: uso de `Annotated`, `Query` y `Path` para reglas de negocio (longitudes, rangos).
- [x] CRUD Persistente: endpoints funcionales para Crear, Leer, Actualizar y Borrar en PostgreSQL.
- [x] Seguridad de Datos: `response_model` configurado para no filtrar datos sensibles/innecesarios.
- [x] Estructura: código organizado por módulos (`router`, `schema`, `service`, `model`, `uow`).

## Frontend (React + TypeScript + Tailwind)

- [x] Setup: proyecto creado con Vite + TS y estructura de carpetas limpia.
- [x] Componentes: componentes funcionales con `Props` tipadas con `interface`.
- [x] Estilos: interfaz construida íntegramente con clases de utilidad de Tailwind CSS 4.
- [x] Navegación: `react-router-dom` con al menos una ruta dinámica (`/productos/:id`).
- [x] Estado Local: `useState` para formularios o UI interactiva.

## Integración y Server State

- [x] Lectura (`useQuery`): listados y detalles consumiendo datos reales de la API.
- [x] Escritura (`useMutation`): formularios que envían datos al backend.
- [x] Sincronización: `invalidateQueries` tras cada mutación.
- [x] Feedback: estados "Cargando..." y "Error" visibles.
    
## Video de Presentación

- [ ] Duración: 15 minutos o menos.
- [ ] Audio/Video: voz clara y resolución que permita leer el código.
- [ ] Demo: flujo completo desde la creación hasta la persistencia en la DB.
