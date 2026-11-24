# Resultado de las pruebas funcionales

- Backend: memoridocx-backend (UP)
- Base de datos: memoridocx
- Documentos semilla: 4
- Proveedores de IA: 3
- Fragmentos del documento 1: 5

## Comparacion de modelos (misma pregunta y documento)

| Modelo | Fragmentos recuperados | Tiempo (ms) |
|---|---:|---:|
| MISTRAL | 3 | 2471 |
| DEEPSEEK | 3 | 48 |
| GLM | 3 | 55 |

## Escenarios

- Exitoso: documento 5 -> AVAILABLE, 1 fragmentos.
- Error controlado: documento 6 -> FAILED, 5 entradas de bitacora con reintentos.
- Sin respuesta: 1 fragmentos recuperados.
