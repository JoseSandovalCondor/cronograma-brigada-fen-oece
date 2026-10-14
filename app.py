import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Cronograma Brigada FEN - OECE",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# COLORES INSTITUCIONALES
# ==========================================
COLORS = {
    'azul_marino': '#1a3a5c',
    'azul_secundario': '#2c5282',
    'blanco': '#ffffff',
    'gris_fondo': '#f7fafc',
    'gris_texto': '#4a5568',
    'amarillo_quemado': '#d69e2e',
    'verde_exito': '#38a169'
}

# ==========================================
# ESTILOS CSS PERSONALIZADOS
# ==========================================
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLORS['gris_fondo']};
    }}
    
    .main-header {{
        background-color: {COLORS['azul_marino']};
        padding: 1.5rem 2rem;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }}
    .header-title {{
        text-align: center;
        flex-grow: 1;
        color: {COLORS['blanco']};
    }}
    .header-title h1 {{
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }}
    .header-title p {{
        margin: 5px 0 0 0;
        font-size: 1.5rem;
        color: {COLORS['amarillo_quemado']};
    }}
    
    .stat-card {{
        background-color: {COLORS['blanco']};
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border-left: 5px solid {COLORS['azul_marino']};
    }}
    .stat-number {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {COLORS['azul_marino']};
        margin: 0;
    }}
    .stat-label {{
        font-size: 1rem;
        color: {COLORS['gris_texto']};
        margin-top: 5px;
    }}
    
    .table-container {{
        background-color: {COLORS['blanco']};
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    .footer {{
        text-align: right;
        color: {COLORS['gris_texto']};
        font-size: 0.85rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #e2e8f0;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIÓN PARA CARGAR DATOS
# ==========================================
@st.cache_data(ttl=60)
def cargar_datos():
    try:
        sheet_id = "1w8KSXhfPdzJho_9k-pjodxdNm3oxZeh4RUQRrGxATjM"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=CRONOGRAMA"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google Sheets: {str(e)}")
        return pd.DataFrame()

# ==========================================
# RUTAS DE LOS LOGOS
# ==========================================
ruta_logo_oece = os.path.join("logos", "logo_oece.png")
if not os.path.exists(ruta_logo_oece):
    ruta_logo_oece = os.path.join("logos", "logo_oece.jpg")

ruta_logo_fen = os.path.join("logos", "logo_fen.jpg")
if not os.path.exists(ruta_logo_fen):
    ruta_logo_fen = os.path.join("logos", "logo_fen.png")

# ==========================================
# ENCABEZADO CON LOGOS (VERSIÓN CORREGIDA)
# ==========================================
def obtener_base64_imagen(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as imagen_file:
            return base64.b64encode(imagen_file.read()).decode()
    return None

# Generar base64 de las imágenes
img_oece_b64 = obtener_base64_imagen(ruta_logo_oece)
img_fen_b64 = obtener_base64_imagen(ruta_logo_fen)

# Crear HTML con tamaños EXPLÍCITOS forzados
if img_oece_b64:
    html_oece = f'<img src="data:image/jpeg;base64,{img_oece_b64}" style="max-width: 215px; height: auto; max-height: 150px;" alt="OECE">'
else:
    html_oece = '<div style="width: 120px;"></div>'

if img_fen_b64:
    html_fen = f'<img src="data:image/jpeg;base64,{img_fen_b64}" style="max-width: 175px; height: auto; max-height: 150px;" alt="Brigada FEN">'
else:
    html_fen = '<div style="width: 100px;"></div>'

# Renderizar encabezado
st.markdown(f"""
    <div class="main-header">
        <div style="flex-shrink: 0;">{html_oece}</div>
        <div class="header-title">
            <h1>CRONOGRAMA DE ACTIVIDADES DE LA BRIGADA FEN - OECE</h1>
            <p>OECE - Organismo Especializado para las Contrataciones Públicas Eficientes</p>
        </div>
        <div style="flex-shrink: 0;">{html_fen}</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# CARGAR Y MOSTRAR DATOS
# ==========================================
df = cargar_datos()

if not df.empty:
    total_actividades = len(df)
    col_estado = next((col for col in df.columns if "estado" in col.lower()), df.columns[-1])
    completados = len(df[df[col_estado].astype(str).str.lower().str.contains("completad|finaliz|cerrad|ejecutad", na=False)])
    en_progreso = total_actividades - completados

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
            <div class="stat-card">
                <p class="stat-number">{total_actividades}</p>
                <p class="stat-label">Total de Actividades</p>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
            <div class="stat-card" style="border-left-color: {COLORS['amarillo_quemado']};">
                <p class="stat-number" style="color: {COLORS['amarillo_quemado']};">{en_progreso}</p>
                <p class="stat-label">En Progreso</p>
            </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
            <div class="stat-card" style="border-left-color: {COLORS['verde_exito']};">
                <p class="stat-number" style="color: {COLORS['verde_exito']};">{completados}</p>
                <p class="stat-label">Completadas</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #1a3a5c; font-weight: 700; font-size: 1.3rem;">📅 Detalle de actividades programadas:</h3>', unsafe_allow_html=True)
    
    st.dataframe(df, use_container_width=True, hide_index=True, height=450)
    st.markdown('</div>', unsafe_allow_html=True)

    ahora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    st.markdown(f"""
        <div class="footer">
            🔄 Última actualización: {ahora}
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Actualizar datos ahora", type="primary"):
        st.cache_data.clear()
        st.rerun()

else:
    st.warning("️ No se pudieron cargar los datos.")
