import os
import sys
import json
import pathlib
import pandas as pd
import plotly.express as px
import streamlit as st

# Configurar encoding utf-8
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from analytics_dashboard.components.leadership_graph import render_leadership_graph
from analytics_dashboard.components.polis_clustering import render_polis_clustering
from analytics_dashboard.components.dama_quality_metrics import render_dama_quality_dashboard

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Cerebro Analítico P2P - Gobernanza Partidaria",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados Premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #F8FAFC;
    }
    .stApp {
        background: linear-gradient(135deg, #0B1120 0%, #17223B 50%, #0F172A 100%);
        color: #E2E8F0;
    }
    .kpi-box {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(96, 165, 250, 0.25);
        border-radius: 16px;
        padding: 22px;
        text-align: center;
        backdrop-filter: blur(14px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.35);
        border-color: rgba(59, 130, 246, 0.6);
    }
    .kpi-val {
        font-family: 'Outfit', sans-serif;
        font-size: 2.3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #60A5FA, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 6px 0;
    }
    .kpi-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #94A3B8;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(15, 23, 42, 0.7);
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94A3B8;
        font-weight: 600;
        padding: 12px 24px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
        color: white !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.45);
    }
</style>
""", unsafe_allow_html=True)

# Rutas de base de datos
DATA_DIR = ROOT_DIR / "data"
LOCAL_P2P_DB = DATA_DIR / "local_p2p_database.json"
SURVEYS_DB = DATA_DIR / "local_intake_surveys.json"

@st.cache_data(ttl=5)
def load_data():
    if not LOCAL_P2P_DB.exists():
        return None, []
    with open(LOCAL_P2P_DB, "r", encoding="utf-8") as f:
        p2p_data = json.load(f)
        
    surveys_data = []
    if SURVEYS_DB.exists():
        with open(SURVEYS_DB, "r", encoding="utf-8") as f:
            surveys_data = json.load(f)
            
    return p2p_data, surveys_data

p2p_data, surveys = load_data()

if not p2p_data:
    st.error("❌ Base de datos P2P no encontrada. Por favor ejecuta `python simulation/generate_p2p_data.py` en tu terminal.")
    st.stop()

# Header Principal y Selector de Eje en Sidebar
st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #60A5FA;">👑 Cerebro P2P</h2>
        <span style="font-size: 0.8rem; color: #94A3B8;">Inteligencia y Gobernanza Partidaria</span>
    </div>
""", unsafe_allow_html=True)

axes_dict = {a["name"]: a["code"] for a in p2p_data["axes"]}
selected_axis_name = st.sidebar.selectbox("🎯 Filtro de Eje Ideológico", ["TODOS LOS EJES"] + list(axes_dict.keys()))
selected_axis_code = "TODOS" if selected_axis_name == "TODOS LOS EJES" else axes_dict[selected_axis_name]

st.sidebar.divider()
st.sidebar.markdown("### 📊 Estado de Ecosistema P2P")
st.sidebar.info(f"**Militantes DAMA MDM:** {len(p2p_data.get('afiliados', []))}\n\n**Delegaciones Líquidas:** {len(p2p_data.get('delegaciones', []))}\n\n**Propuestas en Votación:** {len(p2p_data.get('propuestas', []))}")

# Header del Dashboard
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px;">
        <div>
            <h1 style="margin: 0; font-size: 2.5rem; background: linear-gradient(90deg, #60A5FA, #34D399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🚀 Dashboard Ejecutivo de Gobernanza P2P & Ideario</h1>
            <p style="color: #94A3B8; font-size: 1.08rem; margin-top: 4px;">Participación Ciudadana Activa, Deliberación Polis IA y Gobernanza de Datos en Tiempo Real.</p>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid #10B981; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.82rem;">● LIVE DATA STREAM</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# KPIs Ejecutivos
propuestas = p2p_data.get("propuestas", [])
if selected_axis_code != "TODOS":
    prop_filtered = [p for p in propuestas if p.get("axis_code") == selected_axis_code]
else:
    prop_filtered = propuestas

aprobadas = sum(1 for p in prop_filtered if p.get("consenso_ratio", 0) >= 0.66)
tokens_totales = sum(p.get("total_tokens_votados", 0) for p in prop_filtered)
delegaciones_act = len([d for d in p2p_data.get("delegaciones", []) if selected_axis_code == "TODOS" or d.get("axis_code") == selected_axis_code])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Artículos del Ideario Aprobados</div><div class="kpi-val">{aprobadas} / {len(prop_filtered)}</div><div style="color: #10B981; font-size: 0.8rem;">Consenso Ciudadano (≥66%)</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Tokens de Voto y Apoyo</div><div class="kpi-val">{tokens_totales:,}</div><div style="color: #60A5FA; font-size: 0.8rem;">Motor de Decisión Soberana</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Conexiones y Apoyos Activos</div><div class="kpi-val">{delegaciones_act}</div><div style="color: #A78BFA; font-size: 0.8rem;">Red de Confianza Orgánica</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Consenso Promedio del Ideario</div><div class="kpi-val">{round(sum(p["consenso_ratio"] for p in prop_filtered)/len(prop_filtered)*100, 1) if prop_filtered else 0}%</div><div style="color: #F59E0B; font-size: 0.8rem;">Índice de Acuerdos Polis</div></div>', unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Pestañas Principales
tab_grafo, tab_polis, tab_ideario, tab_dama = st.tabs([
    "🌐 Grafo de Participación y Liderazgo Orgánico", 
    "🎯 Deliberación IA y Consensos (Polis)", 
    "📜 Estado de Aprobación del Ideario", 
    "🛡️ Calidad y Trazabilidad de Datos (DAMA)"
])

# TAB 1: GRAFO DE PARTICIPACIÓN ORGÁNICA
with tab_grafo:
    render_leadership_graph(p2p_data.get("delegaciones", []), p2p_data.get("afiliados", []), selected_axis_code)

# TAB 2: POLIS CLUSTERING
with tab_polis:
    render_polis_clustering(p2p_data.get("polis_clusters", []), p2p_data.get("consensus_bridges", []))

# TAB 3: ESTADO DEL IDEARIO
with tab_ideario:
    st.subheader("📜 Estatus Oficial del Ideario Partidario")
    st.write("Cada artículo es votado en *Sovereign* con tokens directos y delegados. Aquellos que superan el **66% de consenso** quedan formalmente incorporados al Programa de Gobierno del partido.")
    
    for p in prop_filtered:
        consenso = round(p.get("consenso_ratio", 0) * 100, 1)
        bar_color = "#10B981" if consenso >= 66 else ("#3B82F6" if consenso >= 50 else "#F59E0B")
        
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.85); border-left: 5px solid {bar_color}; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.25);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="background: rgba(59, 130, 246, 0.2); color: #60A5FA; padding: 3px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">{p['axis_name']} ({p['axis_code']})</span>
                <span style="font-size: 0.9rem; font-weight: 700; color: {bar_color};">CONSENSO P2P: {consenso}% ({p['status']})</span>
            </div>
            <h3 style="margin: 6px 0 10px 0; font-size: 1.35rem; color: #F8FAFC;">{p['titulo']}</h3>
            <p style="color: #CBD5E1; font-size: 0.98rem; line-height: 1.55;">{p['contenido']}</p>
            
            <!-- Barra de Progreso Visual de Votación -->
            <div style="background: rgba(15, 23, 42, 0.8); border-radius: 9999px; height: 12px; width: 100%; overflow: hidden; margin-top: 15px; display: flex;">
                <div style="background: #10B981; width: {consenso}%; height: 100%; transition: width 0.5s ease;"></div>
                <div style="background: #EF4444; width: {100-consenso}%; height: 100%;"></div>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #94A3B8; margin-top: 8px;">
                <span>👍 Tokens a favor: <b style="color: #10B981;">{p.get('tokens_favor', 0):,}</b> &nbsp;|&nbsp; 👎 Tokens en contra: <b style="color: #EF4444;">{p.get('tokens_contra', 0):,}</b></span>
                <span>Enmiendas tratadas: <b>{p.get('enmiendas_count', 0)}</b> &nbsp;|&nbsp; Autor DID: <code>{p.get('autor_did', '')}</code></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TAB 4: CALIDAD Y LINAJE DAMA-DMBOK
with tab_dama:
    render_dama_quality_dashboard(p2p_data, surveys)
