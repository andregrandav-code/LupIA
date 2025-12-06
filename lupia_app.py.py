

import os
import streamlit as st

# =========================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================
st.set_page_config(
    page_title="LupIA",
    page_icon="L",
    layout="wide",
)

# Logo (debe estar en el mismo repositorio que este archivo)
LOGO_PATH = "logo_lupia.jpg"

# =========================================
# ENCABEZADO
# =========================================
col_logo, col_title = st.columns([1, 4])

with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
    else:
        st.write("LupIA")

with col_title:
    st.markdown(
        "<h1 style='margin-bottom:0'>LupIA – Análisis automático de procesos públicos</h1>",
        unsafe_allow_html=True,
    )
    st.write("Sube los documentos del proceso y LupIA realizará el análisis automático (demo).")

st.markdown("---")

# =========================================
# PANEL LATERAL (API KEY FUTURA)
# =========================================
st.sidebar.header("Configuración")

st.sidebar.write(
    "En futuras versiones aquí podrás ingresar la API Key de OpenAI, configurar modelos, etc."
)

# =========================================
# CARGA DE ARCHIVOS
# =========================================
st.subheader("Subir documentos del proceso")

col1, col2 = st.columns(2)

with col1:
    pliego = st.file_uploader("Sube el pliego (PDF)", type=["pdf"])

with col2:
    oferta = st.file_uploader("Sube la oferta (PDF)", type=["pdf"])

st.markdown("---")

# =========================================
# ANÁLISIS BÁSICO (DEMO)
# =========================================
st.subheader("Análisis (versión demo)")

if pliego and oferta:
    st.success("Archivos cargados correctamente.")

    st.write(
        """
        Esta es una versión demo de LupIA en línea.

        En la versión completa, LupIA hará lo siguiente:

        1. Leer el pliego y extraer:
           - especificaciones técnicas,
           - experiencia requerida,
           - condiciones legales y económicas.

        2. Leer la oferta y extraer:
           - características de los equipos/servicios ofertados,
           - experiencia real del oferente,
           - precios y condiciones.

        3. Comparar automáticamente pliego vs. oferta:
           - requisitos cumplidos / no cumplidos,
           - observaciones legales y técnicas,
           - análisis de riesgos y recomendaciones.

        4. Generar un informe en formato:
           - resumen ejecutivo,
           - detalle técnico,
           - conclusiones y puntaje.
        """
    )
else:
    st.info("Sube **ambos** archivos (pliego y oferta) para iniciar el análisis.")
