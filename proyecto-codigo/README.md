# memoriDocx — Prototipo funcional

Plataforma web para el análisis y la consulta inteligente de información en documentos PDF,
con automatización del procesamiento, arquitectura RAG y selector de modelos de IA.

> Proyecto académico del Seminario de Actualización. Nombre anterior descartado: MediSync.

## Estructura

```
proyecto-codigo/
├── backend/     Spring Boot 3.3.5 + Java 17 + MySQL/MariaDB + PDFBox
├── frontend/    React 18 + Vite 6
├── sql/         schema.sql, seed.sql y consultas_evidencia.sql
├── nodered/     flow_memoridocx.json (flujo Low-code importable)
├── scripts/     probar_api.py (pruebas funcionales)
└── evidencias/  respuestas JSON generadas por las pruebas
```

## Requisitos

- Java 17, Maven 3.9, Node 18+ (probado con Node 24).
- MySQL/MariaDB en `localhost:3306`, usuario `root` sin clave (XAMPP).
- Python 3 con `pymupdf` para generar el PDF de prueba.

## 1. Base de datos

No hay que crearla a mano: el backend ejecuta `schema.sql` y `data.sql` al iniciar
(`spring.sql.init.mode=always`). Crea la base `memoridocx` y siembra:

- 1 documento procesado (`Informe_Analisis_Procesos_memoriDocx.pdf`) con 5 fragmentos.
- 1 documento con error controlado (`PDF_danado_prueba.pdf`).
- 3 proveedores de IA (Mistral, DeepSeek, GLM).
- 1 conversación con su respuesta y bitácora de procesamiento.

Si la clave de MySQL no está vacía:

```powershell
$env:DB_PASSWORD="tu_clave"
```

Para capturar evidencias en phpMyAdmin, ejecuta `sql/consultas_evidencia.sql`.

## 2. Backend

```powershell
cd backend
mvn spring-boot:run
# o: java -jar target/memoridocx-backend-1.0.0.jar
```

Base URL: `http://localhost:8080/api`

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/documents` | Listar documentos |
| POST | `/documents/upload` | Cargar PDF (multipart, campo `file`) |
| GET | `/documents/{id}` | Detalle de un documento |
| GET | `/documents/{id}/chunks` | Fragmentos indexados con página |
| DELETE | `/documents/{id}` | Eliminar documento |
| POST | `/chat/query` | Consulta `{question, documentId, model}` |
| GET | `/logs?documentId=` | Bitácora de procesamiento |
| GET | `/conversations` | Historial de conversaciones |
| GET | `/conversations/{id}/messages` | Mensajes de una conversación |
| GET | `/providers` | Proveedores de IA |

### Modo de respuesta

- **Con credencial**: si existe `MISTRAL_API_KEY` (en el entorno o en `proyecto-codigo/.env`),
  el proveedor `MISTRAL` llama a la API oficial de Mistral (`https://api.mistral.ai/v1`) y
  el modelo `mistral-large-latest`. Las evidencias actuales usan esta vía.
- **Sin credencial**: el sistema genera una respuesta fundamentada en los fragmentos
  recuperados (RAG local, sin costo). Es el modo de respaldo para DeepSeek y GLM.

> El `.env` se crea con la clave real de Mistral. Formato: `MISTRAL_API_KEY=mstrl...`.
> El backend lo lee automáticamente al iniciar (no hace falta exportar variables a mano).
> **No subas este archivo a un repositorio público.**

## 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. El proxy de Vite redirige `/api` al puerto 8080.

## 4. Pruebas y evidencias

Con el backend corriendo, desde la raíz de este proyecto:

```powershell
python scripts/probar_api.py
```

Genera en `evidencias/` los JSON de: documentos, fragmentos, consulta con los tres modelos,
pregunta sin respuesta, carga real de PDF, ejecución con error controlado (3 reintentos),
logs e historial, más un `resumen_pruebas.md`.

La carpeta `evidencias/capturas/` contiene las capturas de pantalla tomadas con el navegador:

- `figura_3_panel_documentos.png`
- `figura_3_trazabilidad_exitosa.png`
- `figura_3_consulta_exitosa.png` (respuesta real de Mistral con fuentes)
- `figura_3_error_controlado.png` (bitácora con reintentos)
- `figura_3_fragmentos.png` (fragmentos indexados con página)

## 5. Flujo Low-code

Importa `nodered/flow_memoridocx.json` en Node-RED. Representa recepción → OCR →
validación → fragmentación → indexación → estado disponible, con ruta de reintento.

## Nota de alcance

La base vectorial definitiva del diseño es Qdrant; en este prototipo ejecutable la
recuperación semántica se aproxima con un puntaje de coincidencia de términos sobre los
fragmentos almacenados en MariaDB, de modo que el proyecto corre sin servicios adicionales.
