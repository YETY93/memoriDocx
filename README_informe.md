# Informe del proyecto — memoriDocx — APA 7ª edición (Colombia)

## Archivos principales

| Archivo | Descripción |
|---|---|
| **`Informe_Proyecto_memoriDocx_APA7.docx`** | **Entregable editable**. Informe en Word con formato APA 7 e índice autogenerado. |
| `Informe_Proyecto_memoriDocx_APA7.pdf` | Vista previa en PDF (17 páginas, con índice actualizado y 5 capturas insertadas). |
| **`Presentacion_memoriDocx.pptx`** | Presentación oral de 18 diapositivas, con gráficos, capturas, notas del orador y transiciones. |
| `Presentacion_memoriDocx.pdf` | Vista previa de la presentación para revisión rápida. |
| `generar_informe_apa.py` | Script que genera el `.docx` desde el entorno virtual `.venv`. |
| `proyecto-codigo/` | Prototipo funcional: backend Java, frontend React, SQL, Node-RED y evidencias. |

## Cómo actualizar el índice

El índice usa los estilos integrados **Título 1 / Título 2 / Título 3** (`Heading 1/2/3`).

1. Abre el documento en Word.
2. `Ctrl + A` para seleccionar todo.
3. `F9` para actualizar los campos (o clic derecho sobre el índice → *Actualizar campo* → *Actualizar tabla completa*).
4. Guarda.

Si agregas un encabezado, aplícale el estilo **Título 1** o **Título 2** y vuelve a actualizar.

## Pendiente por completar antes de entregar

1. **Capturas reales**: ya están insertadas las 5 figuras con capturas del navegador (panel de documentos, trazabilidad, respuesta de Mistral, error controlado y fragmentos). Si quieres cambiarlas, reemplaza los PNG en `proyecto-codigo/evidencias/capturas/` y vuelve a ejecutar el generador.
2. **Enlace del video**: sustituye el marcador `[insertar aquí el enlace de YouTube con visualización restringida]`.
3. **Verificar referencias** con la bibliografía del docente (guía de MinTIC y Ley 1581).
4. El informe tiene **17 páginas en total** (≈14,5 sin contar portada ni referencias), dentro del rango de 10–15 páginas exigido.

## Formato APA 7 aplicado

- Papel carta, márgenes de 1 pulgada, Times New Roman 12, interlineado doble, sangría de 1,27 cm.
- Número de página arriba a la derecha desde la portada; sin *running head* (formato estudiante).
- Portada de estudiante con título, Yesid Rangel Orozco, programa/universidad, curso, profesora y fecha.
- Encabezados APA de niveles 1 y 2 en *sentence case* español; 7 tablas y 3 figuras con numeración y nota.
- Referencias en orden alfabético con sangría francesa.

> APA 7 estricto no incluye tabla de contenido; se conserva por ser requisito de la actividad.

## Presentación oral

- Duración estimada: 10–15 minutos (18 diapositivas, una idea principal por lámina).
- Estructura: portada, agenda, problema, proceso, justificación, tecnología, arquitectura,
  flujo RAG, demostración (4 diapositivas con capturas), comparación de modelos, eficiencia,
  riesgos, ética, conclusiones y cierre con el enlace del video.
- Cada diapositiva tiene **notas del orador** con el guion a desarrollar.
- Efectos: transiciones `fade` / `push` entre diapositivas y énfasis con barras de color,
  tarjetas y gráficos nativos de PowerPoint.

Para regenerar:

```powershell
.\.venv\Scripts\python.exe generar_presentacion.py
```

Luego, si quieres actualizar el PDF de vista previa, abre el `.pptx` en PowerPoint y
guarda como PDF.

## Regenerar

```powershell
.\.venv\Scripts\python.exe generar_informe_apa.py
```

Luego abre Word y pulsa `Ctrl+A` → `F9` para actualizar el índice.
