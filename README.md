# memoriDocx

**Plataforma web inteligente para la gestión, procesamiento y consulta de documentos PDF mediante inteligencia artificial y automatización de procesos.**

Proyecto individual del curso *Seminario de Actualización* — Programa de Ingeniería de Software, Universidad Tecnológica del Oriente. Autor: Yesid Rangel Orozco.

---

## ¿Qué hace este proyecto?

memoriDocx resuelve un problema frecuente en cualquier organización: **el conocimiento existe en documentos PDF, pero acceder a él es lento y depende de que una persona conozca el archivo**. La plataforma automatiza ese acceso:

1. El usuario **carga uno o varios PDF**.
2. Un flujo automatizado extrae el texto página por página, valida que haya contenido suficiente, divide el texto en fragmentos y los indexa conservando su número de página.
3. El usuario formula **preguntas en lenguaje natural** y elige un proveedor de IA (Mistral, DeepSeek o GLM).
4. El sistema recupera los fragmentos más afines (arquitectura **RAG**, *retrieval-augmented generation*) y entrega al modelo solo ese contexto.
5. La respuesta se muestra **con referencias a las páginas de origen**, de modo que puede verificarse.
6. Todo queda registrado: documentos, conversaciones, mensajes y una **bitácora de procesamiento** con reintentos ante fallos.

El resultado no es solo un chat: es un servicio **trazable, medible y auditable** que reduce el trabajo manual y permite comparar modelos con las mismas preguntas.

---

## Resultado de aprendizaje

Evalúa soluciones de automatización implementadas, considerando su impacto técnico, organizacional y ético, para sustentar decisiones de mejora y uso responsable de la tecnología en contextos profesionales.

El proyecto cubre las cinco dimensiones de la rúbrica: identificación y análisis del proceso, diseño del prototipo, documentación, presentación oral, innovación y creatividad.

---

## Tecnologías

| Capa | Tecnología | Función |
|---|---|---|
| Interfaz | React + Vite | Carga de PDF, chat, selector de modelos y trazabilidad |
| Backend | Java 17 + Spring Boot 3.3 | API REST, lógica de negocio, historial y autenticación |
| Orquestación | Node-RED (flujo incluido) | Procesamiento asíncrono y reintentos |
| Extracción | Apache PDFBox | Lectura de texto por página |
| Recuperación | RAG + coincidencia de términos | Selección de fragmentos afines |
| Persistencia | MariaDB + Qdrant (diseño) | Datos estructurales y vectores |
| IA | Mistral, DeepSeek, GLM | Generación de respuestas con capa de abstracción |
| Pruebas | Postman / `probar_api.py` | Validación de endpoints y escenarios |

> En el prototipo ejecutable, la recuperación semántica se aproxima con un puntaje de coincidencia sobre fragmentos en MariaDB, para que el sistema corra sin servicios adicionales. El diseño prevé Qdrant como base vectorial definitiva.

---

## Estructura del repositorio

```
.
├── proyecto-codigo/
│   ├── backend/              API REST en Spring Boot
│   ├── frontend/             interfaz React
│   ├── sql/                  esquema, datos semilla y consultas de evidencia
│   ├── nodered/              flujo Low-code importable
│   ├── scripts/              pruebas funcionales y verificación
│   ├── evidencias/           respuestas JSON y capturas de pantalla
│   └── README.md             guía detallada de ejecución
├── .env.example              plantilla de credenciales (sin valores reales)
└── README.md                 este archivo
```

---

## Puesta en marcha

### 1. Base de datos

Requiere MySQL/MariaDB en `localhost:3306` (usuario `root`, clave vacía por defecto en XAMPP). El backend crea la base `memoridocx` y ejecuta automáticamente `schema.sql` y `data.sql` al iniciar.

### 2. Configuración

Copia la plantilla y coloca tu propia clave de Mistral:

```powershell
Copy-Item .env.example proyecto-codigo\.env
# edita proyecto-codigo\.env y reemplaza tu_clave_de_mistral_aqui
```

Si no hay clave, el sistema funciona en **modo demo** con respuestas fundamentadas en los fragmentos recuperados (sin costo).

### 3. Backend

```powershell
cd proyecto-codigo\backend
mvn spring-boot:run
```

API en `http://localhost:8080/api`.

### 4. Frontend

```powershell
cd proyecto-codigo\frontend
npm install
npm run dev
```

Interfaz en `http://localhost:5173`.

### 5. Pruebas

```powershell
python proyecto-codigo\scripts\probar_api.py
```

Genera evidencias de: consulta exitosa con tres modelos, pregunta sin respuesta, carga real de PDF, error controlado con tres reintentos e historial de conversaciones.

---

## Seguridad

- Las credenciales **no están versionadas**. Solo se incluye `.env.example` con valores ficticios.
- `.env`, `node_modules/`, `target/`, `dist/` y `uploads/` están excluidos mediante `.gitignore`.
- Para un despliegue real se requieren cifrado de credenciales, control de acceso, consentimiento y política de retención de datos, además de protección contra SSRF si se habilitan proveedores personalizados.

---

## Entregables académicos

El informe (APA 7ª edición) y la presentación se producen localmente a partir del código y
las evidencias generadas por las pruebas. **Ni los documentos ni sus scripts generadores
se versionan en este repositorio.**

---

**Yesid Rangel Orozco** · Seminario de Actualización · Noviembre 2026
