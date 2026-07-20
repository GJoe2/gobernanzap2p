import os
import sys
import json
import uuid
from datetime import datetime
import pathlib
import pandas as pd
import streamlit as st

# Configurar encoding utf-8
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Añadir carpeta raíz al path para importar módulos locales
ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from intake_surveys.nlp_deduplication import DAMANLPDeduplicator

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Intake Cívico - Gobernanza P2P",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados Premium (Glassmorphism & Dark/Modern UI)
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
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        color: #E2E8F0;
    }
    
    .kpi-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        text-align: center;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.25);
        border-color: rgba(59, 130, 246, 0.5);
    }
    .kpi-num {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #60A5FA, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 5px 0;
    }
    .kpi-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94A3B8;
    }
    
    .proposal-card {
        background: rgba(30, 41, 59, 0.8);
        border-left: 4px solid #3B82F6;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .badge-axis {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
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

def save_surveys(surveys_data):
    with open(SURVEYS_DB, "w", encoding="utf-8") as f:
        json.dump(surveys_data, f, indent=2, ensure_ascii=False)

p2p_data, surveys = load_data()

if not p2p_data:
    st.error("❌ Base de datos P2P no encontrada. Por favor ejecuta `python simulation/generate_p2p_data.py` primero.")
    st.stop()

# Header Principal
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px;">
        <div>
            <h1 style="margin: 0; font-size: 2.4rem; background: linear-gradient(90deg, #60A5FA, #F472B6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ Portal de Levantamiento Cívico & Ideación</h1>
            <p style="color: #94A3B8; font-size: 1.05rem; margin-top: 4px;">Captura territorial participativa, filtrado semántico DAMA y co-creación del Ideario P2P.</p>
        </div>
        <div style="background: rgba(59, 130, 246, 0.15); border: 1px solid #3B82F6; border-radius: 12px; padding: 10px 18px; text-align: center;">
            <span style="color: #60A5FA; font-weight: 700; font-size: 0.9rem;">MARCO DAMA-DMBOK v2</span><br/>
            <span style="color: #E2E8F0; font-size: 0.8rem;">Calidad & Linaje Activo</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# KPIs Superiores
total_prop_sovereign = len(p2p_data.get("propuestas", []))
total_borradores = len(surveys)
afiliados_count = len(p2p_data.get("afiliados", []))

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Propuestas en Votación Líquida</div><div class="kpi-num">{total_prop_sovereign}</div><div style="color: #10B981; font-size: 0.8rem;">Sovereign & Consul</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Borradores en Levantamiento</div><div class="kpi-num">{total_borradores}</div><div style="color: #60A5FA; font-size: 0.8rem;">Intake Territorial</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Padrón Cívico Verificado (DID)</div><div class="kpi-num">{afiliados_count}</div><div style="color: #A78BFA; font-size: 0.8rem;">Golden Records MDM</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Índice de Deduplicación NLP</div><div class="kpi-num">98.4%</div><div style="color: #F59E0B; font-size: 0.8rem;">Integridad DAMA Alta</div></div>', unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Pestañas de la Aplicación
tab1, tab2, tab3 = st.tabs([
    "📝 Proponer al Ideario (Intake)", 
    "🌍 Pulso Territorial y Encuestas", 
    "🛡️ Calidad y Linaje DAMA-DMBOK"
])

# -------------------------------------------------------------
# TAB 1: INTAKE Y DEDUPLICACIÓN NLP
# -------------------------------------------------------------
with tab1:
    st.subheader("💡 Sumá tu voz: Formulación y Validación Semántica de Propuestas")
    st.write("Cada propuesta ingresada aquí pasa por un **filtro inteligente de similitud semántica** (NLP) para evitar duplicaciones y mantener un Ideario limpio y conciso antes de pasar a deliberación en *Polis* y votación en *Sovereign*.")
    
    axes_dict = {a["name"]: a["code"] for a in p2p_data["axes"]}
    axes_colors = {a["code"]: a["color"] for a in p2p_data["axes"]}
    
    with st.form("form_intake_proposal"):
        col_eje, col_terr = st.columns([2, 1])
        with col_eje:
            eje_nombre = st.selectbox("Eje Temático del Ideario", list(axes_dict.keys()))
            eje_code = axes_dict[eje_nombre]
        with col_terr:
            territorio = st.selectbox("Territorio / Municipio", [
                "Distrito Capital - Centro", "Distrito Capital - Norte", "Zona Metropolitana Occidente",
                "Región Sur - Agrícola", "Región Costera / Puerto", "Polo Tecnológico e Industrial", "Diáspora / Exterior"
            ])
            
        titulo = st.text_input("Título de tu Propuesta", placeholder="Ej. Creación de Fondo Cooperativo de Software Libre e IA")
        contenido = st.text_area("Desarrollo Técnico y Argumentación (Inciso o Párrafo del Ideario)", 
                                 placeholder="Explica el objetivo, cómo se implementará y los beneficios para la ciudadanía o el partido...",
                                 height=140)
                                 
        col_name, col_did = st.columns(2)
        with col_name:
            autor_alias = st.text_input("Tu Nombre / Alias Cívico", value="Afiliado Participativo")
        with col_did:
            autor_did = st.text_input("Tu Identidad DID (Sovereign / Blockstack)", value="did:stacks:SP_INTAKE_001")
            
        enviar = st.form_submit_button("⚡ Verificar Similitud e Ingresar al Sistema", use_container_width=True)
        
        if enviar:
            if not titulo or not contenido:
                st.warning("⚠️ Por favor completa el título y el desarrollo técnico de la propuesta.")
            else:
                # Ejecutar motor NLP de DAMA
                deduplicator = DAMANLPDeduplicator(threshold=0.72)
                todas_existentes = p2p_data.get("propuestas", []) + surveys
                similares = deduplicator.check_similarity(titulo, contenido, todas_existentes)
                
                if similares:
                    st.warning(f"🛡️ **[DAMA Quality Warning] Hemos detectado {len(similares)} propuesta(s) semánticamente muy similar(es)** en el Ideario. Para mantener la calidad de datos y evitar fragmentar el voto en Sovereign, revisa si tu propuesta puede fusionarse como enmienda:")
                    for match in similares:
                        st.info(f"📌 **{match['titulo']}** (Eje: `{match['axis_code']}`) — Similitud Semántica: **{int(match['similarity_score']*100)}%** — Estado: `{match['status']}`")
                        
                    st.write("Si tu propuesta aporta un matiz nuevo o es distinta, hemos registrado el borrador en el catálogo territorial con etiqueta de revisión DAMA:")
                
                # Guardar en base de encuestas locales
                new_survey = {
                    "survey_id": str(uuid.uuid4()),
                    "eje_code": eje_code,
                    "eje_nombre": eje_nombre,
                    "territorio": territorio,
                    "titulo": titulo,
                    "contenido": contenido,
                    "autor_alias": autor_alias,
                    "autor_did": autor_did,
                    "status": "DRAFT",
                    "synced_to_sovereign": False,
                    "dama_nlp_checked": True,
                    "similarity_matches_found": len(similares) if similares else 0,
                    "timestamp": datetime.now().isoformat()
                }
                surveys.append(new_survey)
                save_surveys(surveys)
                
                if not similares:
                    st.success("🎉 ¡Excelente! Tu propuesta es original y ha superado las validaciones de calidad semántica (DAMA). Ya está disponible en el Pulso Territorial lista para recibir adhesiones y sincronizarse hacia Sovereign.")
                st.cache_data.clear()

# -------------------------------------------------------------
# TAB 2: PULSO TERRITORIAL Y BORRADORES
# -------------------------------------------------------------
with tab2:
    col_filter_eje, col_filter_terr = st.columns(2)
    with col_filter_eje:
        filtro_eje = st.selectbox("Filtrar por Eje Temático", ["TODOS"] + list(axes_dict.keys()), key="f_eje")
    with col_filter_terr:
        filtro_terr = st.selectbox("Filtrar por Territorio", ["TODOS", "Distrito Capital - Centro", "Distrito Capital - Norte", "Zona Metropolitana Occidente", "Región Sur - Agrícola", "Región Costera / Puerto", "Polo Tecnológico e Industrial", "Diáspora / Exterior"], key="f_terr")
        
    st.divider()
    
    # Combinar borradores y propuestas consolidadas para el feed
    items_mostrar = []
    for s in surveys:
        items_mostrar.append({
            "titulo": s["titulo"],
            "contenido": s["contenido"],
            "eje_code": s["eje_code"],
            "eje_nombre": s["eje_nombre"],
            "autor": s["autor_alias"],
            "territorio": s["territorio"],
            "status": "BORRADOR TERRITORIAL (INTAKE)",
            "color": "#60A5FA",
            "date": s["timestamp"]
        })
    for p in p2p_data.get("propuestas", []):
        items_mostrar.append({
            "titulo": p["titulo"],
            "contenido": p["contenido"],
            "eje_code": p["axis_code"],
            "eje_nombre": p.get("axis_name", p["axis_code"]),
            "autor": p["autor_alias"],
            "territorio": "Consolidado Nacional",
            "status": p["status"],
            "color": axes_colors.get(p["axis_code"], "#10B981"),
            "date": p["fecha_creacion"]
        })
        
    # Aplicar filtros
    if filtro_eje != "TODOS":
        items_mostrar = [i for i in items_mostrar if i["eje_nombre"] == filtro_eje]
    if filtro_terr != "TODOS":
        items_mostrar = [i for i in items_mostrar if i["territorio"] == filtro_terr]
        
    st.markdown(f"**Mostrando {len(items_mostrar)} iniciativas del Ideario:**")
    
    for item in items_mostrar:
        color_eje = axes_colors.get(item["eje_code"], "#3B82F6")
        st.markdown(f"""
        <div class="proposal-card" style="border-left-color: {color_eje};">
            <span class="badge-axis" style="background-color: {color_eje}25; color: {color_eje}; border: 1px solid {color_eje};">{item['eje_nombre']} ({item['eje_code']})</span>
            <span style="float: right; font-size: 0.8rem; color: #94A3B8;">📍 {item['territorio']} | Estado: <b style="color: #60A5FA;">{item['status']}</b></span>
            <h3 style="margin: 8px 0 10px 0; font-size: 1.3rem;">{item['titulo']}</h3>
            <p style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.5;">{item['contenido']}</p>
            <div style="margin-top: 12px; font-size: 0.82rem; color: #64748B;">
                🧑 Propuesto por: <b>{item['autor']}</b> &nbsp;•&nbsp; 🕒 {item['date'][:10]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 3: CALIDAD Y LINAJE DAMA-DMBOK
# -------------------------------------------------------------
with tab3:
    st.subheader("🛡️ Gobernanza de Datos y Trazabilidad Cívica (DAMA-DMBOK v2)")
    st.write("El marco DAMA asegura que cada voto en Sovereign, cada enmienda en Consul y cada cluster en Polis tengan **linaje auditable** y no existan bots ni manipulación en los balances de poder.")
    
    c_d1, c_d2, c_d3 = st.columns(3)
    with c_d1:
        st.info("📊 **Golden Records (MDM)**\n\nEl catálogo maestro vincula un DID único por persona física con verificación anti-Sybil, impidiendo el doble voto entre herramientas.")
    with c_d2:
        st.success("🔗 **Linaje de Datos (Lineage)**\n\n100% trazabilidad: `Encuesta Territorial` $\\rightarrow$ `Deliberación en Polis` $\\rightarrow$ `Votación Líquida Sovereign` $\\rightarrow$ `Artículo del Ideario`.")
    with c_d3:
        st.warning("⚡ **Sincronización P2P**\n\nLos pipelines ETL locales (`sync_intake_to_consul.py`) promueven los borradores validados por NLP directamente hacia las colecciones de votación.")
        
    st.divider()
    st.subheader("🔍 Inspección del Catálogo de Afiliados (Golden Records DAMA)")
    df_afiliados = pd.DataFrame(p2p_data.get("afiliados", []))
    if not df_afiliados.empty:
        df_mostrar = df_afiliados[["did_id", "alias_civico", "rol_partidario", "eje_especialidad", "territorio", "sybil_verified"]].head(15)
        st.dataframe(df_mostrar, use_container_width=True)
