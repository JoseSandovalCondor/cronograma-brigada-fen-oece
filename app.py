import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import time

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
# COLORES INSTITUCIONALES (Basado en el PDR)
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
    /* Fondo general */
    .stApp {{
        background-color: {COLORS['gris_fondo']};
    }}
    
    /* Encabezado Principal */
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
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    .header-title p {{
        margin: 5px 0 0 0;
        font-size: 1.1rem;
        color: {COLORS['amarillo_quemado']};
        font-weight: 500;
    }}
    
    /* Tarjetas de Estadísticas */
    .stat-card {{
        background-color: {COLORS['blanco']};
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border-left: 5px solid {COLORS['azul_marino']};
        transition: transform 0.2s;
    }}
    .stat-card:hover {{
        transform: translateY(-3px);
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
        font-weight: 500;
    }}
    
    /* Contenedor de Tabla */
    .table-container {{
        background-color: {COLORS['blanco']};
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    /* Footer */
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
# FUNCIÓN PARA CARGAR DATOS DE GOOGLE SHEETS
# ==========================================
@st.cache_data(ttl=60)  # Se actualiza cada 60 segundos
def cargar_datos():
    try:
        # Ruta del archivo de credenciales
        ruta_credenciales = os.path.join("config", "credentials.json")
        
        if not os.path.exists(ruta_credenciales):
            st.error("⚠️ No se encuentra el archivo `credentials.json` en la carpeta `config`.")
            return pd.DataFrame()
        
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(ruta_credenciales, scope)
        client = gspread.authorize(creds)
        
        # Abrir por ID específico y hoja específica
        sheet = client.open_by_key("1w8KSXhfPdzJho_9k-pjodxdNm3oxZeh4RUQRrGxATjM")
        worksheet = sheet.worksheet("CRONOGRAMA")
        
        data = worksheet.get_all_values()
        
        if len(data) > 1:
            headers = data[0]
            df = pd.DataFrame(data[1:], columns=headers)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google Sheets: {str(e)}")
        return pd.DataFrame()

# ==========================================
# ENCABEZADO CON LOGOS
# ==========================================
ruta_logo_oece = os.path.join("logos", "logo_oece.png")
ruta_logo_fen = os.path.join("logos", "logo_fen.png")

# Fallback por si los logos tienen extensión .jpg o no existen
if not os.path.exists(ruta_logo_oece):
    ruta_logo_oece = os.path.join("logos", "logo_oece.jpg")
if not os.path.exists(ruta_logo_fen):
    ruta_logo_fen = os.path.join("logos", "logo_fen.jpg")

st.markdown("""
    <div class="main-header">
        <div class="header-title">
            <h1>CRONOGRAMA BRIGADA FEN</h1>
            <p>Organismo Especializado para las Contrataciones Públicas Eficientes</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Insertar logos usando Streamlit (para asegurar que carguen bien)
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if os.path.exists(ruta_logo_oece):
        st.image(ruta_logo_oece, width=120)
    else:
        st.markdown("<div style='text-align:center; color:#6c757d; font-size:0.8rem;'>[Logo OECE]</div>", unsafe_allow_html=True)
with col2:
    st.empty() # Espacio vacío para equilibrar
with col3:
    if os.path.exists(ruta_logo_fen):
        st.image(ruta_logo_fen, width=120)
    else:
        st.markdown("<div style='text-align:center; color:#6c757d; font-size:0.8rem;'>[Logo FEN]</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# CARGAR Y MOSTRAR DATOS
# ==========================================
df = cargar_datos()

if not df.empty:
    # --- TARJETAS DE ESTADÍSTICAS ---
    total_actividades = len(df)
    
    # Identificar la columna de Estado (busca variaciones comunes como "Estado", "estado", etc.)
    col_estado = next((col for col in df.columns if "estado" in col.lower()), df.columns[-1])
    
    # Conteo de estados (Asumimos que "Completado", "Finalizado" o "Cerrado" son estados de éxito - Verde)
    # El resto se considera En Progreso / Pendiente (Amarillo)
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
                <p class="stat-label">En Progreso / Pendientes</p>
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

    # --- TABLA DE CRONOGRAMA ---
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    st.subheader("📅 Detalle de Actividades Programadas")
    
    # Mostrar la tabla de forma limpia y profesional
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=450
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # --- FOOTER Y ACTUALIZACIÓN ---
    ahora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    st.markdown(f"""
        <div class="footer">
            🔄 Última actualización de datos: {ahora} | Datos en tiempo real desde Google Sheets
        </div>
    """, unsafe_allow_html=True)
    
    # Botón de actualización manual
    if st.button("🔄 Actualizar datos ahora", type="primary"):
        st.cache_data.clear()
        st.rerun()

else:
    st.warning("⚠️ No se pudieron cargar los datos. Verifica que:")
    st.write("1. El archivo `credentials.json` esté en la carpeta `config`.")
    st.write("2. La hoja de cálculo se llame exactamente `CRONOGRAMA` (en mayúsculas).")
    st.write("3. Hayas compartido la hoja con el correo de la cuenta de servicio con permisos de **Lector**.")