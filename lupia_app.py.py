
import streamlit as st

# -----------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------

st.set_page_config(
    page_title="LupIA Demo",
    layout="wide",
)

st.title("🔎 LupIA – Demo")

st.write("""
Esta es una versión DEMO muy básica. 
Pronto podrás usar:
- API de OpenAI
- Modelos configurables
- Análisis legal/técnico/económico real
""")

# -----------------------------------------------------------
# CARGA DE ARCHIVOS
# -----------------------------------------------------------

st.subheader("Carga de documentos")

uploaded_pliego = st.file_uploader(
    "Sube el Pliego",
    type=["pdf"],
    accept_multiple_files=False,
    key="pliego"
)

uploaded_oferta = st.file_uploader(
    "Sube la Oferta",
    type=["pdf"],
    accept_multiple_files=False,
    key="oferta"
)

# Mostrar nombres cuando estén cargados
if uploaded_pliego:
    st.success(f"📄 Pliego cargado: {uploaded_pliego.name}")

if uploaded_oferta:
    st.success(f"📄 Oferta cargada: {uploaded_oferta.name}")


# -----------------------------------------------------------
# BOTÓN DE ANÁLISIS
# -----------------------------------------------------------

st.write("---")

if uploaded_pliego and uploaded_oferta:
    if st.button("🔍 Ejecutar análisis"):
        st.success("Analizando documentos…")
        st.write("""
        Aquí irá el resultado del análisis técnico, legal y económico.
        
        - Extracción de requisitos del pliego
        - Extracción de características de la oferta
        - Comparación automática
        - Semáforo de cumplimiento
        - Conclusión
        """)
else:
    st.info("➡️ Carga el pliego y la oferta para iniciar.")

# -----------------------------------------------------------
# PIE DE PÁGINA
# -----------------------------------------------------------

st.write("---")
st.caption("LupIA · Versión demo · Próximamente análisis real con IA")

