# -*- coding: utf-8 -*-
"""
Genera la presentacion oral del proyecto memoriDocx en PowerPoint.
Incluye diseno propio, graficos, capturas, notas del orador y efectos de transicion.

Uso: .\\.venv\\Scripts\\python.exe generar_presentacion.py
"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
CAP = ROOT / "proyecto-codigo" / "evidencias" / "capturas"
SALIDA = ROOT / "Presentacion_memoriDocx.pptx"

# Paleta
NAVY = RGBColor(0x10, 0x2A, 0x43)
TEAL = RGBColor(0x0E, 0x7C, 0x7B)
ORANGE = RGBColor(0xF2, 0xA6, 0x5A)
LIGHT = RGBColor(0xF4, 0xF6, 0xF8)
GRAY = RGBColor(0x5A, 0x6B, 0x7A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x1B, 0x2B, 0x3A)
RED = RGBColor(0xC0, 0x50, 0x4D)
GREEN = RGBColor(0x2E, 0x8B, 0x57)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


# ---------------------------------------------------------------- helpers
def _solid(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def add_text(slide, text, x, y, w, h, size=18, bold=False, color=DARK,
             align=PP_ALIGN.LEFT, font="Calibri", anchor=MSO_ANCHOR.TOP,
             italic=False, spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        p.line_spacing = spacing
        for run in p.runs:
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.name = font
            run.font.color.rgb = color
    return box


def add_bullets(slide, items, x, y, w, h, size=17, color=DARK, marker="•"):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{marker}  {item}"
        p.level = 0
        p.space_after = Pt(10)
        p.line_spacing = 1.1
        for run in p.runs:
            run.font.size = Pt(size)
            run.font.name = "Calibri"
            run.font.color.rgb = color
    return box


def add_card(slide, x, y, w, h, titulo, cuerpo, color=TEAL, size_title=17,
             size_body=14, icon=""):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  Inches(x), Inches(y), Inches(w), Inches(h))
    _solid(card, WHITE)
    card.line.color.rgb = color
    card.line.width = Pt(1.5)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(0.12))
    _solid(bar, color)
    add_text(slide, f"{icon}  {titulo}" if icon else titulo,
             x + 0.18, y + 0.22, w - 0.36, 0.45,
             size=size_title, bold=True, color=color)
    add_text(slide, cuerpo, x + 0.18, y + 0.72, w - 0.36, h - 0.85,
             size=size_body, color=DARK)
    return card


def add_table(slide, data, x, y, w, h, widths=None, header=NAVY, font_size=13):
    rows, cols = len(data), len(data[0])
    shape = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    tabla = shape.table
    if widths:
        total = sum(widths)
        for i, cw in enumerate(widths):
            tabla.columns[i].width = Emu(int(Inches(w) * cw / total))
    for r in range(rows):
        for c in range(cols):
            cell = tabla.cell(r, c)
            cell.text = str(data[r][c])
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = header if r == 0 else (
                LIGHT if r % 2 == 0 else WHITE)
            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT
                for run in p.runs:
                    run.font.size = Pt(font_size)
                    run.font.name = "Calibri"
                    run.font.color.rgb = WHITE if r == 0 else DARK
                    run.font.bold = (r == 0)
    return tabla


def add_image(slide, path, x, y, w):
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w))


def add_notes(slide, texto):
    slide.notes_slide.notes_text_frame.text = texto


def transition(slide, kind="fade"):
    """Efecto de transicion entre diapositivas (se aplica a la diapositiva actual)."""
    sld = slide._element
    for old in sld.findall(qn("p:transition")):
        sld.remove(old)
    trans = OxmlElement("p:transition")
    trans.set("spd", "med")
    trans.append(OxmlElement("p:" + kind))
    timing = sld.find(qn("p:timing"))
    if timing is not None:
        sld.insert(list(sld).index(timing), trans)
    else:
        sld.append(trans)


def slide_base(titulo, numero, subtitulo=None, dark=False):
    slide = prs.slides.add_slide(BLANK)
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = NAVY if dark else WHITE
    if dark:
        add_text(slide, titulo, 0.8, 1.5, 11.7, 1.4, size=36, bold=True, color=WHITE)
        if subtitulo:
            add_text(slide, subtitulo, 0.8, 2.9, 11.7, 0.8, size=20, color=ORANGE)
        add_text(slide, f"{numero:02d}", 11.8, 6.6, 0.9, 0.5, size=14,
                 color=RGBColor(0x8F, 0xA8, 0xBD), align=PP_ALIGN.RIGHT)
    else:
        header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                        Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        _solid(header, NAVY)
        add_text(slide, titulo, 0.65, 0.26, 11.2, 0.65, size=27, bold=True, color=WHITE)
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                        Inches(0), Inches(1.15), Inches(13.333), Inches(0.08))
        _solid(accent, ORANGE)
        add_text(slide, f"{numero:02d}", 12.1, 6.85, 0.7, 0.4, size=12,
                 color=GRAY, align=PP_ALIGN.RIGHT)
    transition(slide, "fade" if numero % 2 else "push")
    return slide


# ---------------------------------------------------------------- 1. PORTADA
s = prs.slides.add_slide(BLANK)
s.background.fill.solid()
s.background.fill.fore_color.rgb = NAVY
banda = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(4.95),
                           Inches(13.333), Inches(2.55))
_solid(banda, TEAL)
add_text(s, "MEMORIDOCX", 0.9, 0.85, 11.5, 0.6, size=20, bold=True, color=ORANGE)
add_text(s, "Plataforma web inteligente para el análisis\n y consulta de documentos PDF",
         0.9, 1.65, 11.5, 1.8, size=34, bold=True, color=WHITE)
add_text(s, "Automatización · RAG · Inteligencia artificial",
         0.9, 3.8, 11.5, 0.6, size=20, color=RGBColor(0xBF, 0xD3, 0xE0))
add_text(s, "Yesid Rangel Orozco", 0.9, 5.35, 6.0, 0.5, size=20, bold=True, color=WHITE)
add_text(s, "Programa de Ingeniería de Software · Universidad Tecnológica del Oriente",
         0.9, 5.85, 11.0, 0.45, size=14, color=WHITE)
add_text(s, "Seminario de Actualización · Prof. Leydi Johana Polo Amador · Noviembre 2026",
         0.9, 6.4, 11.5, 0.45, size=14, color=WHITE)
add_notes(s, "Bienvenida. Presentar el proyecto memoriDocx y el resultado de aprendizaje: evaluar soluciones de automatización considerando impacto técnico, organizacional y ético.")
transition(s, "fade")

# ---------------------------------------------------------------- 2. AGENDA
s = slide_base("Agenda", 2)
items = [
    ("01", "Contexto y problema", "Por qué consultar documentos es una tarea crítica"),
    ("02", "Proceso y justificación", "Entradas, salidas, actores y alcance"),
    ("03", "Marco tecnológico", "RPA, Low-code, RAG y modelos de IA"),
    ("04", "Diseño del prototipo", "Arquitectura y flujo automatizado"),
    ("05", "Demostración", "Carga, consulta y trazabilidad"),
    ("06", "Evaluación crítica", "Eficiencia, riesgos y ética"),
    ("07", "Conclusiones", "Aprendizajes y recomendaciones"),
]
for i, (num, tit, desc) in enumerate(items):
    y = 1.55 + i * 0.75
    circ = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), Inches(y), Inches(0.5), Inches(0.5))
    _solid(circ, TEAL if i % 2 == 0 else ORANGE)
    add_text(s, num, 0.8, y + 0.08, 0.5, 0.35, size=13, bold=True,
             color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, tit, 1.55, y - 0.02, 4.2, 0.4, size=18, bold=True, color=NAVY)
    add_text(s, desc, 5.8, y + 0.02, 6.5, 0.4, size=14, color=GRAY)
add_notes(s, "Recorrer los siete bloques. Indicar que la demostración es en vivo y que la evaluación es comparativa entre modelos.")

# ---------------------------------------------------------------- 3. PROBLEMA
s = slide_base("Contexto y problema", 3)
add_text(s, "El conocimiento documental crece más rápido que nuestra capacidad para usarlo",
         0.75, 1.45, 11.8, 0.6, size=22, bold=True, color=NAVY)
add_card(s, 0.75, 2.25, 3.7, 2.6, "Tiempo", "Entre 12 y 18 minutos por consulta manual de un documento extenso.", ORANGE, icon="⏱")
add_card(s, 4.82, 2.25, 3.7, 2.6, "Error", "Selección de versiones desactualizadas y reinterpretaciones.", RED, icon="⚠")
add_card(s, 8.89, 2.25, 3.7, 2.6, "Dependencia", "Solo ciertas personas conocen dónde está la información.", TEAL, icon="👥")
rect = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(5.2),
                          Inches(11.84), Inches(1.35))
_solid(rect, LIGHT)
add_text(s, "Pregunta de investigación: ¿cómo automatizar la consulta documental sin sustituir el criterio profesional?",
         1.0, 5.5, 11.3, 0.8, size=18, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
add_notes(s, "Énfasis: el problema no es falta de información sino acceso oportuno. Cifras de la línea base simulada. La solución no sustituye al profesional: lo apoya con evidencia.")

# ---------------------------------------------------------------- 4. PROCESO
s = slide_base("Proceso seleccionado", 4)
add_text(s, "Gestión y consulta de documentos PDF", 0.75, 1.4, 11.8, 0.5,
         size=22, bold=True, color=NAVY)
data = [
    ["Elemento", "Descripción", "Ejemplo"],
    ["Entrada", "Archivo PDF recibido o actualizado", "Informe de gestión"],
    ["Entrada", "Pregunta en lenguaje natural", "¿Cuál es el tiempo de respuesta?"],
    ["Actor", "Quien carga y valida el archivo", "Coordinación de calidad"],
    ["Actor", "Quien consulta", "Analista de información"],
    ["Salida", "Respuesta con referencia de página", "Doce horas (pág. 2)"],
    ["Salida", "Registro de la ejecución", "Historial y bitácora"],
]
add_table(s, data, 0.75, 2.05, 11.8, 4.4, widths=[1.4, 5.1, 4.2], font_size=14)
add_notes(s, "Describir el proceso como sistema: entradas, actores y salidas. Destacar que la salida no es solo texto, sino texto con procedencia y un registro auditable.")

# ---------------------------------------------------------------- 5. JUSTIFICACIÓN
s = slide_base("Justificación y alcance", 5)
add_card(s, 0.75, 1.55, 5.7, 2.3, "Problema", "Distancia entre el conocimiento documental y el acceso oportuno a él.", RED, icon="!")
add_card(s, 6.85, 1.55, 5.7, 2.3, "Oportunidad", "Acortar esa distancia sin sustituir el criterio profesional: el sistema localiza, la persona decide.", TEAL, icon="✓")
add_text(s, "Alcance del prototipo", 0.75, 4.15, 11.8, 0.45, size=20, bold=True, color=NAVY)
add_bullets(s, [
    "Incluye: carga de PDF, extracción, fragmentación con página, consulta conversacional, selector de modelos, historial y bitácora.",
    "Excluye: edición de documentos, entrenamiento propio y proveedores personalizados (BYOK queda como evolución futura).",
    "Se apoya en la guía oficial de MinTIC para identificar procesos automatizables.",
], 0.9, 4.7, 11.5, 2.0, size=16)
add_notes(s, "Justificar por qué este proceso y no otro: alta frecuencia, repetitividad y resultado verificable. Aclarar que BYOK se deja fuera por seguridad (SSRF, credenciales).")

# ---------------------------------------------------------------- 6. TECNOLOGÍA
s = slide_base("Marco tecnológico", 6)
tech = [
    ("React", "Interfaz web", TEAL), ("Java + Spring Boot", "API REST y negocio", NAVY),
    ("Node-RED", "Orquestación Low-code", ORANGE), ("Mistral OCR", "Extracción de texto", TEAL),
    ("Mistral / DeepSeek / GLM", "Generación de respuestas", NAVY), ("MariaDB", "Datos estructurales", ORANGE),
    ("Qdrant", "Recuperación vectorial", TEAL), ("Postman", "Pruebas de API", GRAY),
]
for i, (nombre, uso, color) in enumerate(tech):
    x = 0.75 + (i % 4) * 3.05
    y = 1.6 + (i // 4) * 2.05
    c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y),
                           Inches(2.85), Inches(1.75))
    _solid(c, WHITE)
    c.line.color.rgb = color
    c.line.width = Pt(1.5)
    add_text(s, nombre, x + 0.15, y + 0.25, 2.55, 0.55, size=15, bold=True, color=color)
    add_text(s, uso, x + 0.15, y + 0.85, 2.55, 0.7, size=13, color=DARK)
add_text(s, "Capa de abstracción de proveedores: cambiar de modelo no modifica la lógica de la aplicación.",
         0.75, 5.95, 11.8, 0.6, size=16, italic=True, color=GRAY)
add_notes(s, "Destacar la separación de responsabilidades: Node-RED solo orquesta; Java gestiona negocio; Qdrant guarda vectores. La abstracción permite comparar modelos.")

# ---------------------------------------------------------------- 7. ARQUITECTURA
s = slide_base("Arquitectura general", 7)
capas = [
    ("PRESENTACIÓN", "React · carga de PDF · selector de modelo · chat", TEAL),
    ("APLICACIÓN", "Spring Boot · API REST · autenticación · historial", NAVY),
    ("AUTOMATIZACIÓN", "Node-RED · OCR · validación · fragmentación · reintentos", ORANGE),
    ("DATOS", "MariaDB (estructura) · Qdrant (vectores) · proveedores de IA", GRAY),
]
for i, (nombre, desc, color) in enumerate(capas):
    y = 1.55 + i * 1.28
    r = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(y),
                           Inches(11.1), Inches(1.0))
    _solid(r, color)
    add_text(s, nombre, 1.35, y + 0.12, 2.6, 0.7, size=16, bold=True, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, desc, 4.0, y + 0.12, 8.0, 0.7, size=15, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
    if i < 3:
        add_text(s, "▼", 6.25, y + 1.0, 0.8, 0.3, size=16, color=NAVY,
                 align=PP_ALIGN.CENTER)
add_notes(s, "Explicar el flujo sincrónico de consulta frente al asíncrono de procesamiento. La imagen de la interfaz se muestra en la siguiente diapositiva.")

# ---------------------------------------------------------------- 8. FLUJO RAG
s = slide_base("Flujo automatizado y RAG", 8)
pasos = [
    ("1", "Recepción", "Evento de nuevo PDF"),
    ("2", "OCR", "Extracción por página"),
    ("3", "Validación", "Texto suficiente"),
    ("4", "Fragmentación", "900 caracteres + solape"),
    ("5", "Indexación", "Vector + página"),
    ("6", "Consulta", "Recuperar + generar"),
]
for i, (num, tit, desc) in enumerate(pasos):
    x = 0.65 + i * 2.06
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.55), Inches(1.8), Inches(0.65), Inches(0.65))
    _solid(c, TEAL if i < 5 else ORANGE)
    add_text(s, num, x + 0.55, 1.9, 0.65, 0.4, size=16, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER)
    add_text(s, tit, x, 2.65, 1.8, 0.45, size=15, bold=True, color=NAVY,
             align=PP_ALIGN.CENTER)
    add_text(s, desc, x, 3.1, 1.8, 0.9, size=12, color=GRAY, align=PP_ALIGN.CENTER)
    if i < 5:
        add_text(s, "→", x + 1.75, 1.9, 0.4, 0.4, size=20, color=ORANGE,
                 align=PP_ALIGN.CENTER)
rect = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(4.5),
                          Inches(11.8), Inches(1.8))
_solid(rect, LIGHT)
add_text(s, "RAG: la pregunta se convierte en vector, se recuperan los fragmentos más afines y se entregan como contexto al modelo.\nSi ningún fragmento supera el umbral, el sistema responde que la información no está en el documento.",
         1.05, 4.8, 11.2, 1.3, size=17, color=DARK, align=PP_ALIGN.CENTER)
add_notes(s, "El manejo de errores incluye tres reintentos con espera progresiva. El umbral de similitud evita respuestas inventadas: es una decisión de diseño ético.")

# ---------------------------------------------------------------- 9. UI DOCUMENTOS
s = slide_base("Prototipo · Gestión documental", 9)
add_image(s, CAP / "figura_3_panel_documentos.png", 2.75, 1.45, 7.8)
add_text(s, "Carga de PDF, estados de procesamiento, selector de documento y panel de trazabilidad.",
         0.8, 6.65, 11.8, 0.5, size=15, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
add_notes(s, "Mostrar el panel izquierdo: lista de documentos con badges de estado. El documento semilla está AVAILABLE; el de prueba dañada, FAILED.")

# ---------------------------------------------------------------- 10. UI CONSULTA
s = slide_base("Prototipo · Consulta inteligente", 10)
add_image(s, CAP / "figura_3_consulta_exitosa.png", 2.75, 1.45, 7.8)
add_text(s, "Respuesta de Mistral con tres fuentes documentales y referencia a la página 2.",
         0.8, 6.65, 11.8, 0.5, size=15, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
add_notes(s, "Demostrar la pregunta: ¿Cuál es el tiempo de respuesta en nivel 2? Respuesta: doce horas, página 2. Señalar las fuentes clicables.")

# ---------------------------------------------------------------- 11. TRAZABILIDAD Y ERROR
s = slide_base("Evidencias · Trazabilidad y error controlado", 11)
add_image(s, CAP / "figura_3_trazabilidad_exitosa.png", 0.55, 1.6, 5.95)
add_image(s, CAP / "figura_3_error_controlado.png", 6.85, 1.6, 5.95)
add_text(s, "Flujo exitoso: RECEIVED → OCR → VALIDACIÓN → CHUNKING → INDEXING → READY",
         0.6, 5.55, 5.9, 0.75, size=13, color=NAVY, align=PP_ALIGN.CENTER)
add_text(s, "Error controlado: reintentos 1 y 2, fallo definitivo en el intento 3",
         6.9, 5.55, 5.9, 0.75, size=13, color=RED, align=PP_ALIGN.CENTER)
add_notes(s, "Comparar ambas capturas. La bitácora es la prueba de que el proceso está automatizado y auditado, no solo de que el chat responde.")

# ---------------------------------------------------------------- 12. FRAGMENTOS
s = slide_base("Evidencias · Fragmentos indexados", 12)
add_image(s, CAP / "figura_3_fragmentos.png", 3.15, 1.4, 7.0)
add_text(s, "Cada fragmento conserva su número de página, lo que permite trazar cada respuesta hasta su origen.",
         0.8, 6.55, 11.8, 0.5, size=15, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
add_notes(s, "Mostrar los cinco fragmentos del documento semilla. Explicar el solapamiento y por qué el tamaño de fragmento afecta la precisión.")

# ---------------------------------------------------------------- 13. MODELOS
s = slide_base("Comparación de modelos", 13)
cd = CategoryChartData()
cd.categories = ["Mistral", "DeepSeek", "GLM"]
cd.add_series("Respuestas correctas (de 10)", (9, 9, 8))
chart = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.75), Inches(1.5),
                           Inches(6.2), Inches(4.6), cd).chart
chart.has_legend = False
chart.value_axis.minimum_scale = 0
chart.has_title = True
chart.chart_title.text_frame.text = "Exactitud con el mismo corpus"
plot = chart.plots[0]
plot.has_data_labels = True
plot.data_labels.font.size = Pt(13)
data = [
    ["Modelo", "Correctas", "Latencia", "Observación"],
    ["Mistral", "9/10", "Baja", "Buena adherencia al fragmento"],
    ["DeepSeek", "9/10", "Media", "Respuestas extensas"],
    ["GLM", "8/10", "Media", "Una respuesta sin referencia"],
]
add_table(s, data, 7.25, 2.0, 5.3, 3.0, widths=[1.2, 1.1, 1.0, 2.8], font_size=12)
add_text(s, "Mismas preguntas, contexto y parámetros. La diferencia principal está en latencia y costo, no solo en exactitud.",
         0.75, 6.35, 11.8, 0.6, size=15, italic=True, color=GRAY)
add_notes(s, "El aporte más interesante del proyecto: comparación objetiva. No elegir solo por exactitud; combinar precisión, latencia y sostenibilidad económica.")

# ---------------------------------------------------------------- 14. EFICIENCIA
s = slide_base("Eficiencia esperada", 14)
cd = CategoryChartData()
cd.categories = ["Manual", "Automatizado"]
cd.add_series("Minutos por consulta", (15, 0.67))
chart = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.75), Inches(1.5),
                           Inches(6.0), Inches(4.5), cd).chart
chart.has_legend = False
chart.value_axis.minimum_scale = 0
chart.has_title = True
chart.chart_title.text_frame.text = "Tiempo medio por consulta"
chart.plots[0].has_data_labels = True
data = [
    ["Indicador", "Manual", "Automatizado"],
    ["Tiempo medio", "15 min", "40 s"],
    ["Con referencia", "No registrado", "100 % casos exitosos"],
    ["Versión desactualizada", "Frecuente", "Control parcial"],
    ["Registro", "Ausente", "Completo"],
]
add_table(s, data, 7.1, 2.1, 5.45, 3.3, widths=[2.1, 1.5, 1.9], font_size=12)
add_text(s, "Reducción estimada del 95 %: el trabajo humano se desplaza de buscar a verificar.",
         0.75, 6.3, 11.8, 0.6, size=17, bold=True, color=TEAL)
add_notes(s, "Aclarar que la cifra es estimada en escenario simulado. El valor real está en liberar tiempo para interpretación y verificación.")

# ---------------------------------------------------------------- 15. RIESGOS
s = slide_base("Riesgos y mitigación", 15)
data = [
    ["Riesgo", "Impacto", "Mitigación"],
    ["Respuesta inventada", "Alto", "RAG con referencias y umbral de similitud"],
    ["Exposición de datos", "Alto", "Datos simulados, control de acceso y cifrado"],
    ["Dependencia de proveedor", "Medio", "Capa de abstracción y tres modelos"],
    ["Costo de APIs", "Medio", "Registro de consumo y límites"],
    ["Índice desactualizado", "Medio", "Reindexación automática tras cada carga"],
]
add_table(s, data, 0.75, 1.65, 11.8, 4.6, widths=[2.9, 1.4, 6.5], font_size=15)
add_text(s, "Ninguna mitigación elimina la supervisión humana: el sistema apoya, no decide.",
         0.8, 6.45, 11.8, 0.5, size=16, italic=True, color=NAVY)
add_notes(s, "Clasificar por impacto. El riesgo ético más alto es la respuesta incorrecta con apariencia de certeza; por eso la referencia siempre visible.")

# ---------------------------------------------------------------- 16. ÉTICA
s = slide_base("Ética y responsabilidad profesional", 16)
vals = [
    ("Veracidad", "Evidencia visible; respuestas sin fuente se marcan como no disponibles.", TEAL),
    ("Privacidad", "Minimización, consentimiento y eliminación controlada de datos.", NAVY),
    ("Equidad", "Los modelos pueden reproducir sesgos del corpus documental.", ORANGE),
    ("Responsabilidad", "Una persona identificable valida las decisiones importantes.", GREEN),
]
for i, (tit, cuerpo, color) in enumerate(vals):
    x = 0.75 + (i % 2) * 6.05
    y = 1.6 + (i // 2) * 2.35
    add_card(s, x, y, 5.75, 2.1, tit, cuerpo, color, size_title=19, size_body=16)
add_text(s, "La ingeniería construye sistemas que funcionan… y que pueden justificarse.",
         0.75, 6.4, 11.8, 0.5, size=17, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
add_notes(s, "Cuatro preocupaciones éticas. Cerrar con la idea de que evaluar el impacto antes de adoptar es parte del trabajo profesional.")

# ---------------------------------------------------------------- 17. CONCLUSIONES
s = slide_base("Conclusiones y recomendaciones", 17)
add_text(s, "Conclusiones", 0.75, 1.45, 5.6, 0.45, size=21, bold=True, color=TEAL)
add_bullets(s, [
    "El proceso reúne condiciones para automatizarse: repetición, reglas estables y salida verificable.",
    "Node-RED + API REST + base vectorial + IA producen un servicio con referencias y bitácora.",
    "RAG reduce costo y permite reconocer cuándo no hay respuesta en el documento.",
    "La exactitud depende del documento y del umbral; ningún control sustituye la verificación humana.",
], 0.85, 2.0, 5.6, 3.6, size=15)
add_text(s, "Recomendaciones", 6.85, 1.45, 5.6, 0.45, size=21, bold=True, color=ORANGE)
add_bullets(s, [
    "Mantener visible la referencia de página.",
    "Pruebas de regresión al cambiar fragmentos o umbral.",
    "Registrar consumo para estimar costo y fijar límites.",
    "Política de datos antes de cualquier despliegue real.",
], 6.95, 2.0, 5.6, 3.6, size=15)
add_notes(s, "Síntesis final. Recalcar que el proyecto evalúa la automatización desde cinco dimensiones: técnica, organizacional, económica, tecnológica y ética.")

# ---------------------------------------------------------------- 18. CIERRE
s = slide_base("Gracias", 18, dark=True)
add_text(s, "Enlace de la presentación en video", 0.9, 4.25, 11.5, 0.5,
         size=18, bold=True, color=ORANGE)
add_text(s, "[insertar aquí el enlace de YouTube con visualización restringida]",
         0.9, 4.85, 11.5, 0.6, size=17, color=WHITE)
add_text(s, "Preguntas", 0.9, 5.8, 11.5, 0.7, size=30, bold=True, color=WHITE)
add_notes(s, "Cerrar invitando a preguntas. Recordar que el informe contiene el enlace del video y las evidencias.")
transition(s, "fade")

prs.save(str(SALIDA))
print("Presentación generada:", SALIDA.name, "| diapositivas:", len(prs.slides._sldIdLst))
