import os
import streamlit as st
import unicodedata
import textwrap
from pypdf import PdfReader
from fpdf import FPDF
from crewai import Agent, Task, Crew, Process, LLM

# =========================================
# CONFIGURACION DE LA PAGINA
# =========================================
st.set_page_config(
    page_title="LupIA",
    page_icon="L",
    layout="wide",
)

LOGO_PATH = "logo_lupia.jpg"


# =========================================
# FUNCIÓN AUXILIAR PARA LIMPIAR Y ENVOLVER TEXTO (FIX FPDF)
# =========================================
def limpiar_texto_pdf(texto):
    """
    1. Normaliza unicode y elimina caracteres incompatibles.
    2. Rompe líneas extremadamente largas (>100 caracteres) para evitar 
       el error 'Not enough horizontal space' de FPDF.
    """
    if not texto:
        return ""
        
    # Paso 1: Normalizar y limpiar unicode/caracteres especiales
    # Esto elimina emojis y caracteres complejos que FPDF no soporta bien.
    texto_limpio = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    
    # Paso 2: Romper líneas demasiado largas (Word Wrap para FPDF)
    lineas = texto_limpio.split('\n')
    texto_envuelto = []
    
    for line in lineas:
        # textwrap fuerza saltos de línea si la cadena es muy larga (Ej: una matriz sin formato).
        # Esto previene el error 'Not enough horizontal space'.
        wrapped_line = textwrap.fill(line, width=100, subsequent_indent='    ')
        texto_envuelto.append(wrapped_line)
        
    return '\n'.join(texto_envuelto)


# =========================================
# FUNCION PARA LEER PDF
# =========================================
def extract_text_from_pdf(uploaded_file):
    try:
        # Usamos pypdf (la librería moderna)
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error al leer el PDF: {e}")
        return ""


# =========================================
# FUNCION PARA GENERAR PDF
# =========================================
def generar_pdf(informe_tec1: str, informe_tec2: str, informe_consenso: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    def agregar_seccion(titulo, contenido, subtitulo):
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.multi_cell(0, 8, limpiar_texto_pdf(titulo))
        pdf.ln(2)
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 6, limpiar_texto_pdf(subtitulo))
        pdf.ln(5)
        pdf.set_font("Arial", "", 10)
        
        # Limpiamos y envolvemos el contenido ANTES de pasarlo a multi_cell
        contenido_limpio = limpiar_texto_pdf(str(contenido))
        
        # Usamos un solo multi_cell para el bloque de texto completo
        # FPDF lo dividirá automáticamente según los saltos de línea insertados por limpiar_texto_pdf
        pdf.multi_cell(0, 5, contenido_limpio)

    # Portada
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "LupIA - Informe de Analisis", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    intro = ("Este informe ha sido generado automáticamente por LupIA utilizando múltiples agentes "
             "de IA para analizar el pliego y la oferta proporcionados.")
    pdf.multi_cell(0, 8, limpiar_texto_pdf(intro), align='C')

    # Secciones
    agregar_seccion(
        "Asistente Técnico 1",
        informe_tec1,
        "Análisis de Especificaciones Técnicas y Cumplimiento de Ficha."
    )
    agregar_seccion(
        "Asistente Técnico 2",
        informe_tec2,
        "Revisión Documental, Requisitos Habilitantes y Riesgos Administrativos."
    )
    agregar_seccion(
        "Informe de Consenso de LupIA",
        informe_consenso,
        "Integración de resultados, detección de discrepancias y recomendación final."
    )

    # Retornar bytes
    try:
        # Codificación para FPDF
        return pdf.output(dest="S").encode("latin-1", errors="ignore")
    except AttributeError:
        # Fallback si el encoding falla
        return bytes(pdf.output())


# =========================================
# SIDEBAR – API KEY
# =========================================
st.sidebar.header("⚙️ Configuración")

# CRÍTICO: La API Key se pide en el sidebar (NUNCA hardcodeada)
api_key = st.sidebar.text_input(
    "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",
    type="password",
    help="(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)."
)

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key


# =========================================
# ENCABEZADO
# =========================================
col_logo, col_title = st.columns([1, 4])

with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
    else:
        st.write("🔎 **LupIA**")

with col_title:
    st.markdown("<h1 style='margin-bottom:0'>LupIA - Análisis de Procesos Públicos</h1>", unsafe_allow_html=True)
    st.write("Sube el pliego (solicitud mínima) y la oferta. Multiples agentes IA (CrewAI) analizarán los documentos y generarán un informe de consenso.")

st.markdown("---")


# =========================================
# CARGA DE ARCHIVOS
# =========================================
st.subheader("Subir documentos del proceso")

col1, col2 = st.columns(2)

with col1:
    pliego = st.file_uploader("Sube el Pliego / Solicitud Mínima (PDF)", type=["pdf"])

with col2:
    oferta = st.file_uploader("Sube la Oferta del Proveedor (PDF)", type=["pdf"])

st.markdown("---")


# =========================================
# ANALISIS CON CREWAI (MULTIPLES AGENTES)
# =========================================

if st.button("🚀 Ejecutar análisis con multiples agentes (CrewAI)"):
    if not api_key:
        st.error("⚠ Ingresa tu API Key de OpenAI en el panel izquierdo para poder ejecutar el análisis.")
        st.stop()
    if not (pliego and oferta):
        st.warning("Sube ambos archivos (pliego y oferta) para habilitar el análisis.")
        st.stop()

    # Si todo está OK, inicia el proceso
    with st.spinner("⏳ Analizando documentos con agentes IA..."):
        
        # Extraer texto de los PDFs
        pliego_text_completo = extract_text_from_pdf(pliego)
        oferta_text_completa = extract_text_from_pdf(oferta)

        # Limitar a 20000 caracteres para gestionar tokens y tiempo de respuesta
        pliego_text = pliego_text_completo[:20000]
        oferta_text = oferta_text_completa[:20000]
        
        if not pliego_text or not oferta_text:
             st.error("Error al extraer texto de uno o ambos PDFs. Asegúrate de que no están vacíos o corruptos.")
             st.stop()


        # Configurar LLM para CrewAI (OpenAI)
        # Importante: Pasamos la api_key directamente para asegurar la autenticación
        llm_lupia = LLM(
            model="gpt-4o-mini", # Modelo corregido
            api_key=api_key,
            temperature=0.1,
        )

        # ==============================
        # DEFINICION DE AGENTES (memory=False es crucial en Streamlit)
        # ==============================
        asistente_tecnico_1 = Agent(
            role="Asistente Tecnico 1",
            goal=("Evaluar el cumplimiento TECNICO de la oferta frente al pliego, "
                  "identificando claramente que cumple, que no cumple y que no es verificable."),
            backstory=("Eres un ingeniero especialista en licitaciones publicas en Ecuador, "
                       "con foco en especificaciones tecnicas, fichas, catalogos y hojas de datos."),
            llm=llm_lupia,
            verbose=True,
            allow_delegation=False,
            memory=False
        )

        asistente_tecnico_2 = Agent(
            role="Asistente Tecnico 2",
            goal=("Revisar la OFERTA desde la optica de requisitos documentales del pliego "
                  "(habilitantes, experiencia, capacidad financiera, formularios, etc.), "
                  "tratandolo como un analisis tecnico-documental."),
            backstory=("Actuas como segundo par de ojos tecnico-documental, enfocado en contrastar lo que "
                       "el pliego exige versus lo que se adjunta efectivamente en la oferta."),
            llm=llm_lupia,
            verbose=True,
            allow_delegation=False,
            memory=False
        )

        coordinador = Agent(
            role="Coordinador de LupIA",
            goal=("Integrar los analisis de los dos asistentes tecnicos, "
                  "identificando fortalezas, debilidades, discrepancias y generando un informe "
                  "de consenso claro y accionable."),
            backstory=("Tienes experiencia combinando analisis tecnicos en informes de "
                       "recomendacion para entidades contratantes y oferentes."),
            llm=llm_lupia,
            verbose=True,
            allow_delegation=False,
            memory=False
        )

        # ==============================
        # TAREA ASISTENTE TECNICO 1
        # ==============================
        tarea_tec1 = Task(
            description=(
                "Analiza el CUMPLIMIENTO TECNICO de la oferta frente al pliego.\n\n"
                "Contexto de documentos (limitado a 5000 chars por eficiencia):\n"
                "PLIEGO:\n{pliego}\n\n"
                "OFERTA:\n{oferta}\n\n"
                "LIMITE: Maximo 1200 palabras y maximo 20 filas en la matriz. Responde sin repetir el contexto.\n\n"
                "Estructura de salida:\n"
                "1. Lista de requisitos tecnicos principales (vinetas).\n"
                "2. MATRIZ DE CUMPLIMIENTO (Markdown) con columnas: ID, Tipo, Requisito, Evidencia OFERTA, Cumple (Sí/No/No verificable), Comentario.\n"
                "3. Conclusion tecnica (% cumplimiento, riesgos, recomendacion tecnica)."
            ),
            expected_output="Un informe técnico detallado pero conciso con una matriz de cumplimiento en Markdown.",
            agent=asistente_tecnico_1,
            max_retries=1,
            timeout=180,
        )

        crew_tec1 = Crew(
            agents=[asistente_tecnico_1],
            tasks=[tarea_tec1],
            process=Process.sequential,
            memory=False
        )

        # Ejecución Tarea 1
        res_tec1 = crew_tec1.kickoff(inputs={"pliego": pliego_text, "oferta": oferta_text})
        informe_tec1_str = str(res_tec1.raw) if hasattr(res_tec1, 'raw') else str(res_tec1)


        # ==============================
        # TAREA ASISTENTE TECNICO 2
        # ==============================
        tarea_tec2 = Task(
            description=(
                "Analiza el CUMPLIMIENTO DOCUMENTAL de la oferta frente al pliego.\n\n"
                "Contexto de documentos (limitado a 5000 chars por eficiencia):\n"
                "PLIEGO:\n{pliego}\n\n"
                "OFERTA:\n{oferta}\n\n"
                "LIMITE: Maximo 1200 palabras y maximo 20 filas en la matriz. Responde sin repetir el contexto.\n\n"
                "Estructura de salida:\n"
                "1. Requisitos documentales principales (vinetas).\n"
                "2. MATRIZ DE CUMPLIMIENTO (Markdown) con columnas: ID, Tipo, Requisito, Evidencia OFERTA, Cumple (Sí/No/No verificable), Comentario.\n"
                "3. Conclusion tecnico-documental (riesgos, posibles observaciones, recomendacion)."
            ),
            expected_output="Un informe técnico-documental con matriz de cumplimiento en Markdown y conclusión clara.",
            agent=asistente_tecnico_2,
            max_retries=1,
            timeout=180,
        )

        crew_tec2 = Crew(
            agents=[asistente_tecnico_2],
            tasks=[tarea_tec2],
            process=Process.sequential,
            memory=False
        )

        # Ejecución Tarea 2
        res_tec2 = crew_tec2.kickoff(inputs={"pliego": pliego_text, "oferta": oferta_text})
        informe_tec2_str = str(res_tec2.raw) if hasattr(res_tec2, 'raw') else str(res_tec2)


        # ==============================
        # TAREA DE CONSENSO (CROSS-CHECK)
        # ==============================
        tarea_consenso = Task(
            description=(
                "Eres el COORDINADOR de LupIA. Has recibido dos informes. Tu objetivo es hacer un CROSS-CHECK real entre ambos analisis, "
                "detectar contradicciones y generar un CONSENSO.\n\n"
                "=== INFORME ASISTENTE TECNICO 1 ===\n"
                "{informe_tec1}\n\n"
                "=== INFORME ASISTENTE TECNICO 2 ===\n"
                "{informe_tec2}\n\n"
                "Trabaja de forma muy concreta, limitando el informe a un maximo de 1500 palabras.\n\n"
                "Estructura de salida:\n"
                "1. Resumen ejecutivo (max. 10 lineas).\n"
                "2. MATRIZ DE CONSENSO (Markdown) con columnas: ID, Tipo (Tecnico/Documental), Requisito, AT1, AT2, Consenso (Cumple/No cumple/Subsanable), Comentario final.\n"
                "3. Conclusion general: fortalezas, debilidades, y recomendacion final de LupIA (adjudicar / pedir subsanacion / descalificar)."
            ),
            expected_output="Un informe de consenso en lenguaje tecnico, con matriz de consenso y recomendación final clara de LupIA.",
            agent=coordinador,
            max_retries=1,
            timeout=180,
        )

        crew_consenso = Crew(
            agents=[coordinador],
            tasks=[tarea_consenso],
            process=Process.sequential,
            memory=False
        )

        # Ejecución Tarea 3
        res_consenso = crew_consenso.kickoff(
            inputs={
                "informe_tec1": informe_tec1_str,
                "informe_tec2": informe_tec2_str,
            }
        )
        informe_consenso_str = str(res_consenso.raw) if hasattr(res_consenso, 'raw') else str(res_consenso)

        # Generar PDF
        pdf_bytes = generar_pdf(
            informe_tec1_str,
            informe_tec2_str,
            informe_consenso_str,
        )

    # Mostrar resultados y boton de descarga
    tab1, tab2, tab3 = st.tabs(
        [
            "Asistente Tecnico 1",
            "Asistente Tecnico 2",
            "Informe de Consenso",
        ]
    )

    with tab1:
        st.markdown("### Informe del Asistente Tecnico 1 - Especificaciones")
        st.markdown(informe_tec1_str) # Usamos markdown para renderizar la matriz

    with tab2:
        st.markdown("### Informe del Asistente Tecnico 2 - Documental / Pliego")
        st.markdown(informe_tec2_str) # Usamos markdown para renderizar la matriz

    with tab3:
        st.markdown("### Informe de Consenso de LupIA")
        st.markdown(informe_consenso_str) # Usamos markdown para renderizar la matriz
        st.markdown("---")
        st.download_button(
            "Descargar informe completo en PDF",
            data=pdf_bytes,
            file_name="informe_LupIA.pdf",
            mime="application/pdf",
        )