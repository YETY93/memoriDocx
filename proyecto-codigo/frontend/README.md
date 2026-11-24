# memoriDocx · Frontend

Prototipo de interfaz web (React + Vite) para gestionar documentos PDF, consultar al asistente de preguntas y respuestas y revisar la trazabilidad del procesamiento.

## Requisitos

- Node.js 24 (o superior)
- Backend Spring Boot ejecutándose en `http://localhost:8080`

## Instalación y ejecución

```bash
npm install
npm run dev
```

La aplicación se abre en `http://localhost:5173`. Las peticiones a `/api` se redirigen automáticamente al backend en `http://localhost:8080` gracias al proxy configurado en `vite.config.js`.

## Otros comandos

```bash
npm run build     # genera la versión de producción en dist/
npm run preview   # sirve localmente la versión de producción
```

## Endpoints consumidos

| Método | Ruta | Uso |
| --- | --- | --- |
| GET | `/api/health` | Estado de la conexión con el backend |
| GET | `/api/documents` | Listado de documentos |
| POST | `/api/documents/upload` | Carga de PDF (multipart/form-data, campo `file`) |
| GET | `/api/documents/{id}/chunks` | Fragmentos del documento |
| DELETE | `/api/documents/{id}` | Eliminación de un documento |
| POST | `/api/chat/query` | Consulta al asistente (`question`, `documentId`, `model`) |
| GET | `/api/logs?documentId={id}` | Registros de procesamiento |
| GET | `/api/providers` | Proveedores de IA disponibles |

Códigos de modelo utilizados: `MISTRAL`, `DEEPSEEK`, `GLM`.
