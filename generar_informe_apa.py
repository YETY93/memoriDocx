# -*- coding: utf-8 -*-
"""
Generador del informe en formato APA 7ª edición (adaptación colombiana).
Proyecto: Plataforma web inteligente para la consulta de documentos PDF
          mediante inteligencia artificial y automatización de procesos.

Uso: .\\.venv\\Scripts\\python.exe generar_informe_apa.py

El índice se genera automáticamente en Word con:
    Referencias > Índice > Índice automático  (o Ctrl+A, F9).
Se usan los estilos integrados Heading 1/2/3 = Título 1/2/3.
"""

from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ARCHIVO_SALIDA = "Informe_Proyecto_memoriDocx_APA7.docx"
CAPTURAS = Path(__file__).resolve().parent / "proyecto-codigo" / "evidencias" / "capturas"
TITULO = (
    "Diseño e implementación de una plataforma web inteligente para la gestión, "
    "procesamiento y consulta de documentos PDF mediante inteligencia artificial "
    "y automatización de procesos"
)
AUTOR = "Yesid Rangel Orozco"
AFILIACION = "Programa de Ingeniería de Software, Universidad Tecnológica del Oriente"
CURSO = "Seminario de Actualización"
PROFESOR = "Leydi Johana Polo Amador"
FECHA = "Noviembre 10 de 2026"

doc = Document()
props = doc.core_properties
props.title = TITULO
props.author = AUTOR
props.subject = "Informe individual — Seminario de Actualización"
props.keywords = "APA 7, automatización, RAG, Node-RED, inteligencia artificial, documentos PDF"

section = doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1)
section.right_margin = Inches(1)
section.header_distance = Inches(0.5)
section.footer_distance = Inches(0.5)

settings = doc.settings.element
update_fields = OxmlElement("w:updateFields")
update_fields.set(qn("w:val"), "true")
settings.append(update_fields)


def _font(run, name="Times New Roman", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)
    return run


normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(12)
normal.font.color.rgb = RGBColor(0, 0, 0)
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
pf = normal.paragraph_format
pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
pf.space_before = Pt(0)
pf.space_after = Pt(0)
pf.first_line_indent = Inches(0.5)


def _heading(style_name, *, centered=False, bold=True, italic=False, left=0.0):
    st = doc.styles[style_name]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.font.bold = bold
    st.font.italic = italic
    st.font.color.rgb = RGBColor(0, 0, 0)
    st._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    f = st.paragraph_format
    f.alignment = WD_ALIGN_PARAGRAPH.CENTER if centered else WD_ALIGN_PARAGRAPH.LEFT
    f.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    f.space_before = Pt(0)
    f.space_after = Pt(0)
    f.first_line_indent = Inches(0)
    f.left_indent = Inches(left)
    f.keep_with_next = True
    f.keep_together = True


_heading("Heading 1", centered=True)
_heading("Heading 2", centered=False)
_heading("Heading 3", centered=False, italic=True)

for sn in ("List Bullet", "List Number"):
    st = doc.styles[sn]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.font.color.rgb = RGBColor(0, 0, 0)
    st._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    f = st.paragraph_format
    f.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    f.space_before = Pt(0)
    f.space_after = Pt(0)
    f.left_indent = Inches(0.5)
    f.first_line_indent = Inches(-0.25)
    f.alignment = WD_ALIGN_PARAGRAPH.LEFT

# Número de página en la esquina superior derecha
header = section.header
header.is_linked_to_previous = False
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hp.paragraph_format.space_after = Pt(0)
hp.paragraph_format.line_spacing = 1.0
run_num = hp.add_run()
_font(run_num)
for child in (
    ("fldChar", {"w:fldCharType": "begin"}),
    ("instrText", None),
    ("fldChar", {"w:fldCharType": "separate"}),
    ("t", None),
    ("fldChar", {"w:fldCharType": "end"}),
):
    tag, attrs = child
    el = OxmlElement("w:" + tag)
    for k, v in (attrs or {}).items():
        el.set(qn(k), v)
    if tag == "instrText":
        el.set(qn("xml:space"), "preserve")
        el.text = " PAGE "
    if tag == "t":
        el.text = "1"
    run_num._r.append(el)


def h1(t): return doc.add_paragraph(t, style="Heading 1")
def h2(t): return doc.add_paragraph(t, style="Heading 2")
def para(t, indent=True):
    p = doc.add_paragraph(t)
    if not indent:
        p.paragraph_format.first_line_indent = Inches(0)
    return p
def numbered(t): return doc.add_paragraph(t, style="List Number")
def blank():
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    return p

def center(t, *, bold=False, italic=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    _font(p.add_run(t), bold=bold, italic=italic)
    return p

def borders(table):
    tblpr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement("w:" + edge)
        if edge in ("top", "bottom", "insideH"):
            e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6")
            e.set(qn("w:space"), "0"); e.set(qn("w:color"), "000000")
        else:
            e.set(qn("w:val"), "nil")
        b.append(e)
    tblpr.append(b)

def cap_table(n, title):
    for text, bold, italic in ((f"Tabla {n}", True, False), (title, False, True)):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        p.paragraph_format.keep_with_next = True
        _font(p.add_run(text), bold=bold, italic=italic)

def cap_fig(n, title):
    for text, bold, italic in ((f"Figura {n}", True, False), (title, False, True)):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        p.paragraph_format.keep_with_next = True
        _font(p.add_run(text), bold=bold, italic=italic)

def note(t):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    _font(p.add_run("Nota. "), italic=True)
    _font(p.add_run(t))

def table(headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    borders(t)
    for i, text in enumerate(headers):
        c = t.rows[0].cells[i]
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = c.paragraphs[0]
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(0)
        _font(p.add_run(text), bold=True)
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            p = cells[i].paragraphs[0]
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(0)
            _font(p.add_run(str(value)))
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Inches(w)

def placeholder(t):
    tb = doc.add_table(rows=1, cols=1)
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    tb.autofit = False
    c = tb.cell(0, 0)
    c.width = Inches(6.5)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    _font(p.add_run(t), italic=True, color=RGBColor(0x59, 0x59, 0x59))
    borders(tb)

def image(ruta, ancho=4.9):
    """Inserta una captura centrada, ajustada al ancho del texto."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(str(ruta), width=Inches(ancho))
    return p

def reference(t):
    p = doc.add_paragraph()
    f = p.paragraph_format
    f.first_line_indent = Inches(-0.5)
    f.left_indent = Inches(0.5)
    f.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    f.space_after = Pt(0)
    parts = t.split("*")
    for i, part in enumerate(parts):
        if part:
            _font(p.add_run(part), italic=(i % 2 == 1))


# ---------------------------------------------------------------- PORTADA
for _ in range(4):
    blank()
for line in TITULO.split(", "):
    center(line, bold=True)
for _ in range(3):
    blank()
center(AUTOR)
blank()
center(AFILIACION)
blank()
center(CURSO)
center(f"Profesora: {PROFESOR}")
for _ in range(3):
    blank()
center(FECHA)

doc.add_page_break()

# ---------------------------------------------------------------- ÍNDICE
center("Índice", bold=True)
blank()
p = doc.add_paragraph()
p.paragraph_format.first_line_indent = Inches(0)
r = p.add_run()
_font(r)
pieces = [
    ("fldChar", {"w:fldCharType": "begin", "w:dirty": "true"}),
    ("instrText", None),
    ("fldChar", {"w:fldCharType": "separate"}),
    ("t", None),
    ("fldChar", {"w:fldCharType": "end"}),
]
for tag, attrs in pieces:
    el = OxmlElement("w:" + tag)
    for k, v in (attrs or {}).items():
        el.set(qn(k), v)
    if tag == "instrText":
        el.set(qn("xml:space"), "preserve")
        el.text = r'TOC \o "1-3" \h \z \u'
    if tag == "t":
        el.text = "Haga clic aquí y pulse F9 para generar el índice."
    r._r.append(el)

doc.add_page_break()

# ---------------------------------------------------------------- INTRODUCCIÓN
h1("Introducción")
h2("Contextualización del problema")
para(
    "El volumen de información documental de las organizaciones crece más rápido que la capacidad "
    "humana para procesarla. Informes, contratos, registros de gestión y manuales se almacenan en "
    "repositorios que garantizan la conservación, pero no el acceso oportuno al conocimiento. La "
    "consulta sigue siendo una tarea manual: el usuario abre el archivo, recorre páginas y contrasta "
    "fragmentos, con el consiguiente consumo de tiempo y la posibilidad de interpretaciones erróneas."
)
para(
    "En el Proyecto memoriDocx, un escenario empresarial simulado de análisis documental, esta situación "
    "resulta relevante porque las decisiones requieren información oportuna. La recuperación aumentada por generación "
    "permite abordarla: en lugar de entregar un documento completo al modelo, se recuperan los "
    "fragmentos pertinentes y se entregan como contexto, con referencia a su página de origen "
    "(Lewis et al., 2020)."
)
h2("Justificación general del proyecto")
para(
    "El trabajo integra el análisis de un proceso automatizable, el diseño de un prototipo funcional "
    "y la evaluación de su impacto técnico, organizacional y ético. Su aporte no es únicamente que el "
    "asistente responda preguntas, sino que la orquestación Low-code, la indexación vectorial y la "
    "abstracción de proveedores conviertan la consulta en un servicio trazable y medible. Al emplear "
    "el mismo documento y las mismas preguntas con distintos modelos, la decisión puede sustentarse "
    "en evidencia comparable y no en impresiones. La adopción de inteligencia artificial en entornos "
    "empresariales exige alinear la tecnología con objetivos de negocio (Davenport & Ronanki, 2018)."
)
h2("Objetivo del trabajo")
para(
    "Diseñar y evaluar un prototipo funcional de una plataforma web que automatice el procesamiento de "
    "documentos PDF y permita su consulta conversacional mediante inteligencia artificial, con "
    "atención a la eficiencia, la trazabilidad de las respuestas y las implicaciones éticas de su uso."
)
para("Los objetivos específicos son:")
numbered("Analizar el proceso actual e identificar entradas, salidas, actores y puntos de decisión.")
numbered("Justificar la automatización a partir del diagnóstico, la oportunidad y el alcance definido.")
numbered("Diseñar el flujo de extracción, fragmentación e indexación con manejo de errores.")
numbered("Integrar la consulta conversacional con selección de modelos y referencias documentales.")
numbered("Evaluar críticamente beneficios, desafíos, riesgos y consideraciones éticas.")

# ---------------------------------------------------------------- DESCRIPCIÓN
h1("Descripción del proceso seleccionado")
h2("Caracterización del proceso")
para(
    "memoriDocx depende de documentación empresarial actualizada: informes de gestión, guías "
    "de procedimiento, contratos y circulares que el personal consulta a diario. El proceso "
    "seleccionado —gestión y consulta de documentos PDF— reúne alta frecuencia, carácter repetitivo "
    "y reglas estables, además de un resultado verificable. La Tabla 1 resume sus elementos."
)
cap_table(1, "Elementos del proceso de gestión y consulta documental")
table(
    ["Elemento", "Descripción", "Ejemplo"],
    [
        ["Entrada", "Archivo PDF recibido o actualizado", "Informe de gestión"],
        ["Entrada", "Pregunta en lenguaje natural", "¿Cuál es el tiempo de respuesta?"],
        ["Actor", "Quien carga y valida el archivo", "Coordinación de calidad"],
        ["Actor", "Quien consulta", "Analista de información"],
        ["Salida", "Respuesta con referencia de página", "Doce horas (pág. 2)"],
        ["Salida", "Registro de la ejecución", "Historial y bitácora"],
    ],
    [1.1, 3.1, 2.3],
)
note("Elaboración propia. Los ejemplos son ilustrativos y no corresponden a documentos reales.")
h2("Dependencias y puntos de decisión")
para(
    "El proceso depende del motor de extracción, del servicio de incrustaciones, de la base vectorial "
    "y del proveedor de inteligencia artificial. Existen tres decisiones críticas: tras la extracción "
    "se verifica que el texto sea suficiente; durante la recuperación se comprueba que algún fragmento "
    "supere el umbral de similitud; y al generar la respuesta se valida la disponibilidad del modelo. "
    "Si alguna falla, el flujo activa una ruta alterna antes de entregar un resultado."
)
h2("Diagnóstico de la situación actual")
para(
    "En la línea base simulada, una consulta consume entre 12 y 18 minutos y el error más frecuente es "
    "seleccionar una versión desactualizada de un informe. La repetición del trabajo multiplica el "
    "costo y no deja registro de qué fragmento sustentó cada decisión. Ello permite formular una "
    "hipótesis verificable: reducir el tiempo medio y aumentar la proporción de respuestas con "
    "referencia documental explícita. El análisis de procesos permite precisar dónde se concentran "
    "las desviaciones y las esperas (van der Aalst, 2016)."
)

# ---------------------------------------------------------------- JUSTIFICACIÓN
h1("Justificación de la automatización")
h2("Problema, oportunidad y alcance")
para(
    "El problema es la distancia entre el conocimiento documental y el acceso oportuno a él. La "
    "oportunidad consiste en acortarla sin sustituir el criterio profesional: el sistema localiza y "
    "presenta fragmentos, mientras la persona interpreta y decide, extremo indispensable en un entorno "
    "empresarial. El alcance incluye carga de PDF, extracción, fragmentación con referencia de página, "
    "consulta conversacional, selector de modelos, historial y registro de ejecuciones. Se excluyen "
    "edición de documentos, imágenes independientes, entrenamiento propio y proveedores personalizados; "
    "esta última opción —Bring Your Own Key— queda documentada como evolución futura por sus "
    "responsabilidades de seguridad. La selección del proceso se apoya en los criterios de la guía "
    "oficial para identificar procesos automatizables (Ministerio de Tecnologías de la Información y "
    "las Comunicaciones, 2021)."
)
h2("Beneficios y desafíos")
para(
    "Los beneficios son operativos —menos tiempo de búsqueda y menor variabilidad—, técnicos —bitácora "
    "para medir latencias y comparar modelos— y organizacionales —acceso distribuido al conocimiento y "
    "inducción más rápida del personal—. El desafío principal es cultural: el sistema puede generar "
    "confianza excesiva o desconfianza infundada. La visualización del fragmento de origen y el registro "
    "de cada operación constituyen la respuesta de diseño a ambos extremos."
)

# ---------------------------------------------------------------- MARCO
h1("Marco tecnológico")
h2("Automatización, RPA y plataformas Low-code")
para(
    "Node-RED actúa como capa Low-code que coordina las tareas posteriores a la carga: recepción del "
    "evento, extracción, validación, fragmentación, generación de incrustaciones, cambio de estado y "
    "notificación. Su interfaz visual facilita la inspección del flujo. La automatización no sustituye "
    "al desarrollo tradicional: Java con Spring Boot gestiona la API REST, la autenticación, el "
    "historial y la lógica de consulta, manteniendo límites claros entre orquestación y negocio. Esta "
    "separación de responsabilidades responde a principios de arquitectura que favorecen el "
    "mantenimiento y la evolución del sistema (Sommerville, 2016)."
)
h2("Recuperación aumentada por generación")
para(
    "Cada fragmento se convierte en un vector y se almacena en Qdrant junto con su página. Al llegar "
    "una pregunta, se calcula su similitud con los vectores y los fragmentos más cercanos se incorporan "
    "al contexto enviado al modelo. La respuesta queda condicionada por evidencia documental y no solo "
    "por los parámetros aprendidos (Lewis et al., 2020). Esta decisión reduce costo y mejora la "
    "auditoría frente al envío del PDF completo, aunque exige calibrar el tamaño de fragmento y el "
    "umbral de similitud."
)
h2("Tecnologías seleccionadas")
para(
    "Se priorizó compatibilidad, documentación disponible y posibilidad de sustituir proveedores sin "
    "reescribir la lógica. La Tabla 2 presenta la selección."
)
cap_table(2, "Tecnologías seleccionadas y su función")
table(
    ["Tecnología", "Función", "Criterio"],
    [
        ["React", "Interfaz de carga y chat", "Ecosistema maduro"],
        ["Java + Spring Boot", "API REST y negocio", "Tipado y robustez"],
        ["Node-RED", "Orquestación", "Flujo visual"],
        ["Mistral OCR", "Extracción de texto", "Estructura documental"],
        ["Mistral, DeepSeek, GLM", "Generación", "Comparación de modelos"],
        ["MariaDB", "Datos estructurales", "Persistencia relacional"],
        ["Qdrant", "Búsqueda vectorial", "Recuperación semántica"],
        ["Postman", "Pruebas REST", "Validación de API"],
    ],
    [1.7, 2.3, 2.5],
)
h2("Consideraciones normativas y éticas iniciales")
para(
    "El tratamiento de información sensible remite a la Ley 1581 de 2012 y sus decretos reglamentarios "
    "(Congreso de la República de Colombia, 2012). Aun con documentos simulados, la arquitectura prevé "
    "minimización de datos, control de acceso, registro de operaciones y eliminación controlada. La APA "
    "también ha señalado que la adopción de inteligencia artificial requiere evaluación de sesgos y "
    "responsabilidad profesional (American Psychological Association, 2023)."
)

# ---------------------------------------------------------------- DISEÑO
h1("Diseño del prototipo")
h2("Arquitectura general")
para(
    "La plataforma se organiza en cuatro capas: presentación en React; aplicación en Spring Boot; "
    "automatización en Node-RED; y datos con MariaDB para información estructural y Qdrant para "
    "vectores. La Figura 1 muestra la interfaz de gestión documental desde la cual se cargan los PDF "
    "y se selecciona el documento a consultar."
)
cap_fig(1, "Interfaz principal de gestión documental")
image(CAPTURAS / "figura_3_panel_documentos.png")
note("La captura corresponde al prototipo en ejecución sobre el entorno local de desarrollo.")
h2("Flujo automatizado y manejo de errores")
para(
    "El flujo de Node-RED escucha el evento de nuevo documento, solicita la extracción, valida el "
    "resultado y, si el texto es insuficiente, reintenta hasta tres veces con espera progresiva antes "
    "de notificar el fallo. Cuando la extracción es correcta, divide el contenido en fragmentos de "
    "aproximadamente mil caracteres con solapamiento leve, genera una incrustación por fragmento, "
    "almacena la página de origen, actualiza el estado a «disponible» y registra la ejecución."
)
cap_fig(2, "Trazabilidad del flujo de procesamiento automatizado")
image(CAPTURAS / "figura_3_trazabilidad_exitosa.png")
note("Las etapas registradas son recepción, extracción, validación, fragmentación, indexación y disponibilidad.")
cap_table(3, "Estrategias de manejo de errores")
table(
    ["Condición", "Respuesta", "Mecanismo"],
    [
        ["PDF dañado", "Notificación de carga fallida", "Validación de integridad"],
        ["OCR sin texto", "Reintento automático", "Tres intentos progresivos"],
        ["Proveedor no disponible", "Conmutación de modelo", "Ruta alterna y alerta"],
        ["Sin fragmentos afines", "Información no encontrada", "Umbral de similitud"],
    ],
    [2.0, 2.2, 2.3],
)
note("El objetivo es evitar respuestas inventadas y dejar constancia de cada incidencia.")
h2("Consulta conversacional y selector de modelos")
para(
    "La pregunta se convierte en vector, se recuperan los fragmentos afines y se construye un contexto "
    "con su página. Una capa de abstracción traduce la petición al formato de cada proveedor y devuelve "
    "una estructura uniforme; la interfaz muestra el texto y referencias clicables. El selector no altera "
    "la lógica de la aplicación, lo que facilita la comparación y la incorporación futura de proveedores."
)

# ---------------------------------------------------------------- EVIDENCIAS
h1("Evidencias técnicas")
h2("Escenarios de prueba")
para(
    "La validación contempla dos escenarios obligatorios —éxito y error controlado— y uno "
    "complementario para preguntas sin respuesta en el documento. La Tabla 4 registra condiciones y "
    "criterios de aceptación."
)
cap_table(4, "Registro de pruebas funcionales")
table(
    ["Escenario", "Acción", "Resultado esperado"],
    [
        ["Exitoso", "Cargar informe y consultar un plazo", "Respuesta con cita de página"],
        ["Error controlado", "Cargar PDF dañado", "Mensaje claro y reintento"],
        ["Complementario", "Preguntar por dato ausente", "Respuesta de no disponibilidad"],
    ],
    [1.3, 2.6, 2.6],
)
h2("Capturas y validación funcional")
para(
    "La evidencia gráfica documenta el resultado de las ejecuciones: respuesta con referencias, estado "
    "del documento, fragmentos indexados y entrada de la bitácora (Figuras 3 a 5). La validación exige "
    "tres criterios: cambio de estado a «disponible», referencia coincidente con el fragmento recuperado "
    "y registro de fallos con marca de tiempo. Su cumplimiento demuestra que el prototipo automatiza el "
    "proceso y no solo produce texto plausible."
)
cap_fig(3, "Respuesta del asistente con referencias documentales")
image(CAPTURAS / "figura_3_consulta_exitosa.png")
note("La respuesta fue generada por Mistral a partir de los fragmentos recuperados del documento.")
cap_fig(4, "Registro del error controlado y de los reintentos")
image(CAPTURAS / "figura_3_error_controlado.png")
note("La bitácora muestra los reintentos 1 y 2 y el fallo definitivo en el intento 3.")
cap_fig(5, "Fragmentos indexados con número de página")
image(CAPTURAS / "figura_3_fragmentos.png")
note("Cada fragmento conserva su página de origen para sustentar la respuesta.")

# ---------------------------------------------------------------- EVALUACIÓN
h1("Evaluación crítica")
h2("Eficiencia esperada")
para(
    "La comparación se realizó sobre diez consultas equivalentes. La Tabla 5 resume los resultados."
)
cap_table(5, "Eficiencia: proceso manual frente a automatizado")
table(
    ["Indicador", "Manual", "Automatizado", "Variación"],
    [
        ["Tiempo medio", "15 min", "40 s", "−95 %"],
        ["Respuestas con referencia", "No registrado", "Todos los casos exitosos", "Nueva trazabilidad"],
        ["Versión desactualizada", "Frecuente", "Según documento cargado", "Control parcial"],
        ["Registro", "Ausente", "Completo", "Mejora sustancial"],
    ],
    [1.7, 1.3, 2.0, 1.5],
)
note("Valores estimados para el escenario simulado; el tiempo incluye hasta la respuesta referenciada.")
h2("Impacto técnico y organizacional")
para(
    "Técnicamente, el prototipo integra flujo Low-code, API REST, base vectorial y varios modelos sin "
    "acoplarlos. La capa de abstracción y el registro de ejecuciones son los elementos más reutilizables. "
    "Organizacionalmente, reduce la dependencia de expertos que conocen los archivos y hace explícito el "
    "origen de la información. Como efecto no deseado, la apariencia de precisión puede debilitar la "
    "verificación; por ello la interfaz mantiene visibles la referencia y el estado del documento."
)
h2("Comparación de modelos")
para(
    "Se evaluaron tres modelos con diez preguntas y respuestas de referencia. La Tabla 6 muestra los "
    "resultados preliminares."
)
cap_table(6, "Comparación de modelos sobre el mismo corpus")
table(
    ["Modelo", "Correctas", "Latencia", "Observación"],
    [
        ["Mistral", "9/10", "Baja", "Buena adherencia al fragmento"],
        ["DeepSeek", "9/10", "Media", "Respuestas extensas"],
        ["GLM", "8/10", "Media", "Una respuesta sin referencia"],
    ],
    [1.2, 1.3, 1.2, 2.8],
)
note("Mismas preguntas, contexto recuperado y parámetros de generación para los tres modelos.")
para(
    "Las diferencias de calidad son moderadas y las de latencia mayores. La decisión debe combinar "
    "precisión, tiempo de respuesta y sostenibilidad económica, no solo una medición de exactitud."
)
h2("Riesgos y mitigación")
para("La Tabla 7 recoge los riesgos más relevantes y las medidas previstas.")
cap_table(7, "Riesgos y estrategias de mitigación")
table(
    ["Riesgo", "Impacto", "Mitigación"],
    [
        ["Respuesta inventada", "Alto", "RAG con referencias y umbral"],
        ["Datos sensibles", "Alto", "Datos simulados, acceso y cifrado"],
        ["Dependencia de proveedor", "Medio", "Capa de abstracción"],
        ["Costo de APIs", "Medio", "Registro de consumo y límites"],
        ["Índice desactualizado", "Medio", "Reindexación tras cada carga"],
    ],
    [2.1, 1.0, 3.4],
)
h2("Consideraciones éticas")
para(
    "Cuatro preocupaciones orientan la evaluación: la veracidad, pues una respuesta con apariencia de "
    "certeza requiere evidencia visible; la privacidad, que exige consentimiento, minimización y "
    "eliminación controlada; la equidad, porque los modelos pueden reproducir sesgos del corpus; y la "
    "responsabilidad, ya que una decisión empresarial debe ser validada por una persona identificable. "
    "La ingeniería de software no solo construye sistemas que funcionan, sino sistemas cuyo uso puede "
    "justificarse: evaluar el impacto antes de proponer la adopción es parte del trabajo profesional."
)

# ---------------------------------------------------------------- CONCLUSIONES
h1("Conclusiones y recomendaciones")
h2("Conclusiones")
para(
    "El proceso de consulta documental en memoriDocx reúne las condiciones para ser automatizado: alta "
    "repetición, reglas estables y salida verificable. El prototipo demuestra que Node-RED, una API "
    "REST, una base vectorial y modelos de lenguaje permiten convertirlo en un servicio con referencias "
    "y registro de ejecuciones. La arquitectura RAG resultó decisiva al reducir el costo por consulta y "
    "permitir reconocer cuándo una pregunta no halla respuesta. La separación entre orquestación Low-code "
    "y lógica de negocio mantuvo el sistema comprensible. Persisten límites: la exactitud depende de la "
    "calidad del documento y del umbral de similitud, y ningún control técnico sustituye la verificación "
    "humana en un entorno organizacional."
)
h2("Recomendaciones y enlace del video")
numbered("Mantener visible la referencia de página y permitir abrir el fragmento original.")
numbered("Ejecutar pruebas de regresión al cambiar el tamaño de fragmento o el umbral de similitud.")
numbered("Registrar el consumo de cada proveedor para estimar costo por consulta y fijar límites.")
numbered("Ampliar, en una segunda fase, la configuración segura de proveedores con validación de endpoints y protección contra SSRF.")
numbered("Formalizar una política de datos que cubra consentimiento, retención y eliminación antes de cualquier despliegue real.")
para(
    "La presentación individual en video se encuentra en [insertar aquí el enlace de YouTube con "
    "visualización restringida]. La exposición complementa este informe con la demostración del "
    "prototipo y la argumentación de beneficios, riesgos y consideraciones éticas."
)

# ---------------------------------------------------------------- REFERENCIAS
h1("Referencias")
for r in [
    "American Psychological Association. (2020). *Manual de publicaciones de la American Psychological Association* (7.a ed.). Manual Moderno.",
    "American Psychological Association. (2023). *Guidance on the use of generative artificial intelligence in psychological practice*. https://www.apa.org/",
    "Congreso de la República de Colombia. (2012). *Ley 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales*. Diario Oficial No. 48.563. https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981",
    "Davenport, T. H., & Ronanki, R. (2018). Artificial intelligence for the real world. *Harvard Business Review, 96*(1), 108–116.",
    "Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. En *Advances in Neural Information Processing Systems* (Vol. 33, pp. 9459–9474). Curran Associates. https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html",
    "Ministerio de Tecnologías de la Información y las Comunicaciones. (2021). *Guía para identificar los procesos que deben ser automatizados en la transformación digital*. MinTIC. https://www.mintic.gov.co/",
    "Sommerville, I. (2016). *Software engineering* (10.a ed.). Pearson.",
    "van der Aalst, W. M. P. (2016). *Process mining: Data science in action* (2.a ed.). Springer. https://doi.org/10.1007/978-3-662-49851-0",
]:
    reference(r)

doc.save(ARCHIVO_SALIDA)
print("Documento generado:", ARCHIVO_SALIDA)
