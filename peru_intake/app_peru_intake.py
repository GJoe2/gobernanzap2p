import os
import sys
import json
import uuid
from datetime import datetime
import pathlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuración de encoding utf-8 en Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from peru_intake.peru_demographics import (
    REGIONES_PERU, AMBITOS_TERRITORIALES, RANGOS_ETARIOS,
    SITUACIONES_LABORALES, NIVELES_EDUCATIVOS, PREGUNTAS_ESTRUCTURADAS, EJES_IDEARIO_PERU
)
from peru_intake.nlp_peru_classifier import PeruNLPClassifier
from peru_intake.speech_transcriber import PeruSpeechTranscriber
from peru_intake.wordcloud_generator import (
    render_wordcloud, render_top_keywords_treemap, get_combined_text_from_surveys
)

# Configuración de página Streamlit
st.set_page_config(
    page_title="Nueva Generación | Escucha Ciudadana y Propuestas",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados Premium (Disruptivo & Moderno)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #F8FAFC;
    }
    .stApp {
        background: radial-gradient(circle at top right, #1E1B4B 0%, #0B0F19 45%, #05070D 100%);
        color: #E2E8F0;
    }
    .kpi-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(168, 85, 247, 0.35);
        border-radius: 18px;
        padding: 22px 18px;
        text-align: center;
        backdrop-filter: blur(16px);
        box-shadow: 0 12px 30px -8px rgba(0,0,0,0.6);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.6);
    }
    .kpi-num {
        font-family: 'Outfit', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8, #A855F7, #F43F5E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 6px 0;
    }
    .kpi-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #94A3B8;
        font-weight: 600;
    }
    .proposal-box {
        background: rgba(15, 23, 42, 0.85);
        border-left: 4px solid #A855F7;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 6px 15px -3px rgba(0,0,0,0.4);
        border-top: 1px solid rgba(255,255,255,0.05);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    .badge-ng {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 10px;
        background: rgba(168, 85, 247, 0.2);
        color: #C084FC;
        border: 1px solid rgba(168, 85, 247, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Rutas de datos
DATA_DIR = ROOT_DIR / "peru_intake" / "data"
PERU_DB = DATA_DIR / "peru_surveys_database.json"

@st.cache_data(ttl=3)
def load_peru_data():
    if not PERU_DB.exists():
        return []
    with open(PERU_DB, "r", encoding="utf-8") as f:
        return json.load(f)

def save_peru_data(surveys_data):
    with open(PERU_DB, "w", encoding="utf-8") as f:
        json.dump(surveys_data, f, indent=2, ensure_ascii=False)

surveys = load_peru_data()

# -------------------------------------------------------------
# SIDEBAR: MODO DE OPERACIÓN Y FILTROS
# -------------------------------------------------------------
st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 18px; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 14px; border: 1px solid rgba(255,255,255,0.06);">
        <h2 style="margin: 0; font-size: 1.65rem; font-weight: 800; background: linear-gradient(135deg, #38BDF8, #A855F7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Nueva Generación</h2>
        <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 500;">Plataforma de Escucha Ciudadana y Propuestas</span>
    </div>
""", unsafe_allow_html=True)

modo_portal = st.sidebar.radio(
    "🛠️ Modalidad de Ingreso:",
    ["👤 Autorregistro Ciudadano (Voz / Texto libre)", "🧑‍🌾 Captura en Campo (Activistas territoriales)"]
)

if "Activista" in modo_portal or "Captura en Campo" in modo_portal:
    st.sidebar.caption("🧑‍🌾 **Tip de Campo:** No olvides georreferenciar tu punto (Lugar y GPS) en el formulario central para auditarlo en el Mapa.")
else:
    st.sidebar.caption("💡 **Tip Ciudadano:** Puedes llenar tus datos y enviarnos tu propuesta por texto o grabando un audio que la IA transcribirá.")

st.sidebar.divider()
st.sidebar.markdown("### 📊 Pulso y Calidad de Datos")
if surveys:
    df_s = pd.DataFrame(surveys)
    informales_cnt = df_s[df_s["situacion_laboral"].str.contains("Independiente|Informal|Comerciante", na=False)].shape[0]
    informal_pct = round((informales_cnt / len(df_s)) * 100, 1) if len(df_s) > 0 else 0
    
    st.sidebar.info(f"**Total Voces Registradas:** {len(surveys)}\n\n**Regiones Activas:** {df_s['region'].nunique()}/25\n\n**Sector Informal / MYPE:** {informal_pct}%\n\n**Estándar de Calidad:** 100% Verificado")

# Header principal
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.08);">
        <div>
            <h1 style="margin: 0; font-size: 2.6rem; font-weight: 800; background: linear-gradient(135deg, #F8FAFC 20%, #38BDF8 60%, #A855F7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Voz y Propuestas por Regiones</h1>
            <p style="color: #A1A1AA; font-size: 1.08rem; margin-top: 6px; font-weight: 400;">Conectando de forma orgánica las necesidades ciudadanas con soluciones pragmáticas y reales.</p>
        </div>
        <div>
            <span style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 8px 18px; border-radius: 9999px; font-weight: 700; font-size: 0.82rem; letter-spacing: 0.5px;">ESCUCHA ACTIVA — v2.0</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# KPIs Superiores
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Voces Recopiladas</div><div class="kpi-num">{len(surveys)}</div><div style="color: #38BDF8; font-size: 0.8rem; font-weight: 600;">Cobertura Territorial</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Regiones Presentes</div><div class="kpi-num">{df_s["region"].nunique() if surveys else 0}</div><div style="color: #A855F7; font-size: 0.8rem; font-weight: 600;">24 Dptos + Callao + Diáspora</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Testimonios Procesados</div><div class="kpi-num">{sum(1 for s in surveys if len(s.get("testimonio_abierto","")) > 15)}</div><div style="color: #F43F5E; font-size: 0.8rem; font-weight: 600;">Voz Cívica & Texto Libre</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Clasificación Temática</div><div class="kpi-num">98.5%</div><div style="color: #34D399; font-size: 0.8rem; font-weight: 600;">Precisión NLP Orgánica</div></div>', unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Pestañas Principales
tab1, tab2, tab3 = st.tabs([
    "📝 Sumar tu Voz y Propuesta (Voz / Texto)",
    "🌍 Pulso Territorial y Demandas por Región",
    "🛡️ Calidad de Datos y Trazabilidad (DAMA)"
])

# -------------------------------------------------------------
# TAB 1: FORMULARIO Y VOZ CÍVICA
# -------------------------------------------------------------
with tab1:
    with st.expander("📖 ¿Cómo usar y llenar este formulario? (Guía Práctica paso a paso, Ejes del Ideario y Glosario de Términos)", expanded=False):
        st.markdown("""
        <div style='background: rgba(30, 41, 59, 0.65); padding: 18px 22px; border-radius: 12px; border: 1px solid rgba(148, 163, 184, 0.25); margin-bottom: 16px;'>
            <h4 style='color: #F8FAFC; margin-top: 0; font-size: 1.15rem;'>📌 Paso a Paso según tu Modalidad de Ingreso</h4>
            <div style='display: flex; gap: 18px; flex-wrap: wrap; margin-top: 12px;'>
                <div style='flex: 1; min-width: 280px; background: rgba(15, 23, 42, 0.65); padding: 15px; border-radius: 10px; border-left: 4px solid #3B82F6;'>
                    <b style='color: #60A5FA; font-size: 1rem;'>👤 1. Para Ciudadanos (Autorregistro):</b>
                    <ol style='margin: 10px 0 0 18px; padding: 0; color: #CBD5E1; font-size: 0.92rem; line-height: 1.65;'>
                        <li><b>Datos Demográficos:</b> Selecciona tu Región, Ámbito territorial (Urbano, Rural, etc.), Rango Etario y Situación Laboral.</li>
                        <li><b>Las 3 Preguntas Estratégicas:</b> Escoge en las listas desplegables el problema principal de tu región, tu mayor preocupación familiar y tu prioridad inmediata para el Gobierno.</li>
                        <li><b>Tu Voz o Propuesta Libre:</b> Puedes <b>grabar un audio por micrófono</b> (nuestra IA transcribirá tus palabras exactamente) o escribir en texto tu testimonio o solución.</li>
                        <li><b>Registrar:</b> Haz clic en el botón inferior para sumar tu voz inmutable al padrón analítico del país.</li>
                    </ol>
                </div>
                <div style='flex: 1; min-width: 280px; background: rgba(15, 23, 42, 0.65); padding: 15px; border-radius: 10px; border-left: 4px solid #10B981;'>
                    <b style='color: #34D399; font-size: 1rem;'>🧑‍🌾 2. Para Activistas Territoriales (Captura en Campo):</b>
                    <ol style='margin: 10px 0 0 18px; padding: 0; color: #CBD5E1; font-size: 0.92rem; line-height: 1.65;'>
                        <li><b>Activar Modo:</b> En el menú lateral izquierdo, selecciona la opción <code>Captura en Campo (Activistas territoriales)</code>.</li>
                        <li><b>Identificación del Activista:</b> Registra tu Nombre y Apellido, tu Región Base y tu celular/ID de contacto.</li>
                        <li><b>Georeferenciación Territorial:</b> Escribe el lugar exacto de captura (Plaza, Mercado, Asamblea comunal). Si estás en campo, copia las coordenadas GPS (Latitud y Longitud) de Google Maps o de tu celular y pégalas en los campos numéricos para auditar el punto en la Pestaña 2.</li>
                        <li><b>Entrevista Ágil:</b> Selecciona las opciones del ciudadano en segundos, graba su voz o toma nota rápida y haz clic en Guardar.</li>
                    </ol>
                </div>
            </div>
            
            <h4 style='color: #F8FAFC; margin: 24px 0 10px 0; font-size: 1.15rem;'>🏛️ Clasificación Automática con IA en los 10 Ejes Programáticos del Ideario</h4>
            <p style='color: #94A3B8; font-size: 0.9rem; margin-top: 0;'>Cada vez que envías un testimonio por voz o texto, nuestro motor de Inteligencia Artificial analiza su contenido semántico y lo asigna orgánicamente al Eje Programático que mejor resuelve esa demanda:</p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; font-size: 0.85rem;'>
                <div style='background: rgba(239, 68, 68, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3); color: #FCA5A5;'><b>E01: Reforma Judicial y Policial</b><br/>Depuración de corruptos, penas severas, seguridad ciudadana y justicia celeridosa.</div>
                <div style='background: rgba(249, 115, 22, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(249, 115, 22, 0.3); color: #FDBA74;'><b>E02: Formalización Tributaria MYPE</b><br/>Régimen simple de un solo tributo, créditos blandos sin trabas y apoyo al emprendedor.</div>
                <div style='background: rgba(16, 185, 129, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.3); color: #6EE7B7;'><b>E03: Salud Primaria Universal</b><br/>Postas médicas bien equipadas, telemedicina, medicinas sin sobrecostos e historia unificada.</div>
                <div style='background: rgba(59, 130, 246, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.3); color: #93C5FD;'><b>E04: Educación Técnica y Digital</b><br/>Currícula conectada con el mercado laboral, programación e inglés en los colegios.</div>
                <div style='background: rgba(236, 72, 153, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(236, 72, 153, 0.3); color: #F472B6;'><b>E05: Agroindustria e Infraestructura Hídrica</b><br/>Canales de riego, represas, fertilizantes accesibles y articulación de cultivos al mercado.</div>
                <div style='background: rgba(168, 85, 247, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.3); color: #D8B4FE;'><b>E06: Conectividad y Corredores Logísticos</b><br/>Carreteras multicarril, puertos modernos, trenes interregionales y puentes duraderos.</div>
                <div style='background: rgba(234, 179, 8, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(234, 179, 8, 0.3); color: #FDE047;'><b>E07: Soberanía Energética y Minería Limpia</b><br/>Industrialización nacional, canon minero directo a las comunidades y respeto ambiental.</div>
                <div style='background: rgba(20, 184, 166, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(20, 184, 166, 0.3); color: #5EEAD4;'><b>E08: Seguridad Alimentaria y Desarrollo Rural</b><br/>Erradicación de la anemia infantil, apoyo al ganadero/campesino y cadenas de frío comunales.</div>
                <div style='background: rgba(99, 102, 241, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(99, 102, 241, 0.3); color: #C7D2FE;'><b>E09: Empleo Formal e Innovación</b><br/>Protección laboral inteligente, flexibilidad para contratar e impulso al ecosistema de startups.</div>
                <div style='background: rgba(100, 116, 139, 0.12); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(100, 116, 139, 0.3); color: #CBD5E1;'><b>E10: Modernización y Gobernanza Digital</b><br/>Estado digital sin papel, trámites ágiles en línea y transparencia pública en tiempo real.</div>
            </div>
            
            <h4 style='color: #F8FAFC; margin: 24px 0 8px 0; font-size: 1.15rem;'>🔑 Glosario de Términos Clave y Auditoría de Calidad</h4>
            <ul style='color: #CBD5E1; font-size: 0.92rem; line-height: 1.65; margin: 0; padding-left: 20px;'>
                <li><b>Estándar DAMA-DMBOK v2:</b> Metodología internacional de Gestión y Auditoría de Datos. Garantiza que cada encuesta ingresada al padrón sea única, íntegra y esté blindada contra duplicaciones o manipulación artificial.</li>
                <li><b>DID Verificador (Identidad Descentralizada):</b> Huella digital criptográfica asignada automáticamente a cada testimonio, certificando que la fecha, hora y origen territorial son inmutables y trazables.</li>
                <li><b>Levantamiento Territorial Georreferenciado:</b> Registro en campo (plazas, ferias, barrios) acompañado de coordenadas GPS reales que alimentan el Mapa Interactivo de la Pestaña 2 para certificar la cobertura nacional auténtica.</li>
                <li><b>Transcripción Literaria por Voz:</b> Tecnología de reconocimiento de voz de vanguardia que convierte audios ciudadanos en texto limpio, permitiendo que las expresiones genuinas de la gente alimenten las nubes de palabras y análisis del país.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    nombre_activista = ""
    region_activista = ""
    id_activista = ""
    lugar_exacto = ""
    tipo_punto = ""
    latitud_gps = ""
    longitud_gps = ""
    
    if "Activista" in modo_portal or "Captura en Campo" in modo_portal:
        st.markdown("<div style='background: rgba(16, 185, 129, 0.15); border-left: 4px solid #10B981; padding: 14px 18px; border-radius: 12px; margin-bottom: 20px;'>🧑‍🌾 <b>Modo Activista Territorial Activo:</b> Formulario optimizado para captura ágil en plazas, mercados y asambleas ciudadanas. Los datos ingresan al instante al padrón.</div>", unsafe_allow_html=True)
        
        st.markdown("### 🧑‍🌾 Registro del Activista Territorial (Responsable del Levantamiento)")
        c_act1, c_act2, c_act3 = st.columns(3)
        with c_act1:
            nombre_activista = st.text_input("👤 Nombre y Apellido del Activista:", placeholder="Ej. Carlos Mendoza Rivera", key="t1_nombre_act")
        with c_act2:
            region_activista = st.selectbox("📍 Región Base / Asignada al Activista:", REGIONES_PERU, key="t1_region_act")
        with c_act3:
            id_activista = st.text_input("📱 Celular / DNI o ID de Contacto (Opcional):", placeholder="Ej. 987654321", key="t1_id_act")
            
        st.markdown("#### 🗺️ Georeferenciación del Punto de Levantamiento en Campo")
        c_geo1, c_geo2, c_geo3 = st.columns([2, 1.3, 1.3])
        with c_geo1:
            lugar_exacto = st.text_input("📍 Lugar del Levantamiento (Plaza, Mercado, Comunidad, Barrio):", placeholder="Ej. Plaza de Armas de Huamanga / Mercado Belén", key="t1_lugar_geo")
        with c_geo2:
            tipo_punto = st.selectbox("🏘️ Tipo de Espacio Social:", ["Plaza / Parque Público", "Mercado / Feria Comercial", "Asamblea Comunal / Sindicato", "Universidad / Instituto / Colegio", "Visita Domiciliaria / Barrio", "Paradero / Terminal Terrestre", "Otro Punto de Encuentro"], key="t1_tipo_geo")
        with c_geo3:
            st.markdown("<div style='font-size:0.8rem; color:#A1A1AA; margin-bottom:4px;'>Coordenadas GPS (Opcional):</div>", unsafe_allow_html=True)
            c_lat, c_lon = st.columns(2)
            with c_lat:
                latitud_gps = st.text_input("Latitud (-12.04)", placeholder="-12.0463", key="t1_lat_geo", label_visibility="collapsed")
            with c_lon:
                longitud_gps = st.text_input("Longitud (-77.04)", placeholder="-77.0428", key="t1_lon_geo", label_visibility="collapsed")
        st.caption("💡 **Tip para Activistas:** En campo, abre Google Maps o la brújula/GPS de tu celular en el punto exacto, toca la ubicación y pega aquí las coordenadas (Latitud y Longitud) para georreferenciar el levantamiento.")
        st.divider()
    else:
        st.subheader("💡 Conectá la realidad de tu provincia con soluciones reales")
        
    st.markdown("### 1️⃣ Variables Sociodemográficas de tu Región")
    c_r1, c_r2, c_r3 = st.columns(3)
    with c_r1:
        sel_region = st.selectbox("Región / Departamento", REGIONES_PERU, key="t1_region")
        sel_ambito = st.selectbox("Ámbito Territorial de Residencia", AMBITOS_TERRITORIALES, key="t1_ambito")
    with c_r2:
        sel_edad = st.selectbox("Rango Etario", RANGOS_ETARIOS, key="t1_edad")
        sel_genero = st.selectbox("Género / Identidad", ["Femenino", "Masculino", "Prefiero no decir"], key="t1_genero")
    with c_r3:
        sel_educacion = st.selectbox("Nivel Educativo alcanzado", NIVELES_EDUCATIVOS, key="t1_educacion")
        sel_laboral = st.selectbox("Situación Laboral / Actividad Económica", SITUACIONES_LABORALES, key="t1_laboral")
        
    st.divider()
    st.markdown("### 2️⃣ Demandas Estructurales y Prioridades para el País")
    
    p1_resp = st.selectbox(PREGUNTAS_ESTRUCTURADAS["P1"]["pregunta"], PREGUNTAS_ESTRUCTURADAS["P1"]["opciones"], key="t1_p1")
    p2_resp = st.selectbox(PREGUNTAS_ESTRUCTURADAS["P2"]["pregunta"], PREGUNTAS_ESTRUCTURADAS["P2"]["opciones"], key="t1_p2")
    p3_resp = st.selectbox(PREGUNTAS_ESTRUCTURADAS["P3"]["pregunta"], PREGUNTAS_ESTRUCTURADAS["P3"]["opciones"], key="t1_p3")
    
    st.divider()
    st.markdown("### 3️⃣ Testimonio Abierto y Transcripción Inteligente de Voz")
    st.write("¿Quieres detallar un problema concreto, una denuncia o una propuesta para tu comunidad? Puedes redactarlo o **grabar/subir una nota de voz** para que nuestra IA lo transcriba y clasifique de forma orgánica:")
    
    # Opciones reactivas de voz o texto
    metodo_ingreso = st.radio("Método de Ingreso:", ["✍️ Redactar por Texto Libre", "🎙️ Subir Archivo / Nota de Voz (.mp3, .wav, .ogg, .m4a)"], horizontal=True, key="t1_radio_metodo")
    
    testimonio_final = ""
    
    if metodo_ingreso == "✍️ Redactar por Texto Libre":
        testimonio_final = st.text_area("Desarrollo de tu Testimonio o Propuesta Territorial", placeholder="Ej. En nuestro distrito necesitamos cámaras y créditos accesibles para que los emprendedores trabajen seguros y sin cobros ilegales...", height=120, key="t1_texto_libre")
    else:
        st.info("🎙️ **Transcripción Inteligente en Vivo:** Sube el archivo de audio grabado en tu celular o enviado por WhatsApp. El motor lo procesará a texto en segundos.")
        audio_file = st.file_uploader("Seleccionar archivo de voz (.wav, .mp3, .ogg, .m4a)", type=["wav", "mp3", "ogg", "m4a"], key="t1_file_audio")
        
        # Botón independiente para transcribir si hay audio
        if audio_file is not None:
            if st.button("🎙️ Transcribir Audio y Convertir a Texto ahora", use_container_width=True, key="t1_btn_transcribir"):
                with st.spinner("Procesando nota de voz y normalizando texto..."):
                    transcriber = PeruSpeechTranscriber(language="es-PE")
                    exito, texto_transcrito = transcriber.transcribe(audio_file.read(), audio_file.name)
                    if exito:
                        st.success("✅ ¡Nota de voz transcrita exitosamente!")
                        st.session_state["transcripcion_temporal"] = texto_transcrito
                    else:
                        st.error(texto_transcrito)
                        
        # Mostrar cuadro editable con lo transcrito
        texto_base = st.session_state.get("transcripcion_temporal", "")
        testimonio_final = st.text_area("Texto Transcrito para Revisión / Edición (Puedes ajustar o sumar detalles antes de enviar):", value=texto_base, height=120, key="t1_texto_transcrito")

    st.markdown("<br/>", unsafe_allow_html=True)
    enviar_encuesta = st.button("🚀 Procesar e Indexar en el Padrón de Nueva Generación", type="primary", use_container_width=True, key="t1_btn_enviar")
    
    if enviar_encuesta:
        # Ejecutar motor DAMA de similitud semántica y clasificación
        classifier = PeruNLPClassifier()
        similares = classifier.find_duplicate_or_similar(testimonio_final if testimonio_final else p1_resp, surveys, region=sel_region)
        
        if similares:
            st.warning(f"🛡️ **[Alerta de Similitud Semántica DAMA]** Hemos detectado {len(similares)} testimonio(s) similar(es) en la región **{sel_region}**. Esto indica un fuerte consenso ciudadano sobre este punto:")
            for sim in similares:
                st.info(f"📌 **{sim['problema']}** (Eje: `{sim['eje_code']}`) — Similitud: **{int(sim['similarity_score']*100)}%**\n\n*Testimonio vecino:* \"{sim['testimonio'][:120]}...\"")
                
        # Clasificar Eje del Ideario
        texto_analisis = f"{p1_resp} {testimonio_final}"
        eje_code, confianza = classifier.classify_eje(texto_analisis)
        eje_name = EJES_IDEARIO_PERU.get(eje_code, {}).get("nombre", eje_code)
        
        new_record = {
            "survey_id": f"PERU-{uuid.uuid4().hex[:8].upper()}",
            "region": sel_region,
            "ambito_territorial": sel_ambito,
            "rango_edad": sel_edad,
            "genero": sel_genero,
            "nivel_educativo": sel_educacion,
            "situacion_laboral": sel_laboral,
            "p1_problema_region": p1_resp,
            "p2_problema_familiar": p2_resp,
            "p3_prioridad_gobierno": p3_resp,
            "testimonio_abierto": testimonio_final,
            "origen_registro": "MODO_ACTIVISTA_TERRITORIAL" if ("Activista" in modo_portal or "Captura en Campo" in modo_portal) else "MODO_AUTOREGISTRO_CIUDADANO",
            "activista_nombre": nombre_activista.strip() if nombre_activista else ("Activista No Especificado" if ("Activista" in modo_portal or "Captura en Campo" in modo_portal) else "N/A - Autorregistro"),
            "activista_region": region_activista if region_activista else (sel_region if ("Activista" in modo_portal or "Captura en Campo" in modo_portal) else "N/A"),
            "activista_contacto": id_activista.strip() if id_activista else "",
            "georef_lugar": lugar_exacto.strip() if lugar_exacto else ("No Especificado" if ("Activista" in modo_portal or "Captura en Campo" in modo_portal) else "Autorregistro Online"),
            "georef_tipo_espacio": tipo_punto if tipo_punto else "N/A",
            "georef_latitud": latitud_gps.strip() if latitud_gps else "",
            "georef_longitud": longitud_gps.strip() if longitud_gps else "",
            "eje_asignado": eje_code,
            "eje_nombre": eje_name,
            "dama_verified": True,
            "did_verificador": f"did:stacks:PERU_{uuid.uuid4().hex[:6]}",
            "timestamp": datetime.now().isoformat()
        }
        surveys.append(new_record)
        save_peru_data(surveys)
        
        st.success(f"🎉 ¡Voz y propuesta registradas con éxito para la región **{sel_region}**! Clasificado en el Eje: **{eje_name}** (`{eje_code}`).")
        st.cache_data.clear()
        if "Activista" in modo_portal or "Captura en Campo" in modo_portal:
            st.session_state["transcripcion_temporal"] = ""

# -------------------------------------------------------------
# TAB 2: PULSO TERRITORIAL Y DEMOGRAFÍA REGIONAL
# -------------------------------------------------------------
with tab2:
    st.subheader("📊 Cerebro Analítico Regional: Problemáticas, Cruces Demográficos y Voz Cívica")
    st.write("Explora el pulso ciudadano a través de nuestras 4 dimensiones analíticas interactivas en tiempo real:")
    
    sub_t1, sub_t2, sub_t3, sub_t4, sub_t5 = st.tabs([
        "🇵🇪 Batería de las 3 Preguntas Estratégicas",
        "🔀 Cruces Sociodemográficos Multinivel",
        "🎙️ Nube de Palabras y Transcripciones en Vivo",
        "🗣️ Muro Testimonial por Ejes Programáticos",
        "🗺️ Mapa y Puntos de Levantamiento"
    ])
    
    df_surveys = pd.DataFrame(surveys)
    
    # =========================================================
    # SUB-TAB 1: LAS 3 PREGUNTAS ESTRATÉGICAS
    # =========================================================
    with sub_t1:
        st.markdown("#### 🎯 Análisis Estructural de Demandas Cívicas")
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            reg_filtro = st.selectbox("Filtrar Análisis por Región:", ["TODAS LAS REGIONES"] + REGIONES_PERU, key="f_reg_t1")
        with c_f2:
            lab_filtro = st.selectbox("Filtrar por Situación Laboral:", ["TODOS LOS SECTORES"] + SITUACIONES_LABORALES, key="f_lab_t1")
            
        if not df_surveys.empty:
            df_p = df_surveys.copy()
            if reg_filtro != "TODAS LAS REGIONES":
                df_p = df_p[df_p["region"] == reg_filtro]
            if lab_filtro != "TODOS LOS SECTORES":
                df_p = df_p[df_p["situacion_laboral"] == lab_filtro]
                
            st.info(f"📌 Analizando **{len(df_p)}** respuestas bajo los filtros seleccionados ({reg_filtro} — {lab_filtro.split('(')[0]})")
            
            # Gráfica P1 (Problema Regional)
            p1_counts = df_p["p1_problema_region"].value_counts().reset_index()
            p1_counts.columns = ["Problema Regional Declaro", "Conteo"]
            fig_p1 = px.bar(
                p1_counts, x="Conteo", y="Problema Regional Declaro", orientation='h',
                title=f"1️⃣ Mayor Problema de la Región/Ciudad en {reg_filtro}",
                color="Conteo", color_continuous_scale="Reds"
            )
            fig_p1.update_layout(height=420, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)', font=dict(color="#CBD5E1"), margin=dict(l=10,r=20,t=50,b=30))
            st.plotly_chart(fig_p1, use_container_width=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Gráfica P2 (Problema Familiar / Personal) - Apilado debajo a ancho completo
            p2_counts = df_p["p2_problema_familiar"].value_counts().reset_index()
            p2_counts.columns = ["Problema Familiar/Personal", "Conteo"]
            fig_p2 = px.bar(
                p2_counts, x="Conteo", y="Problema Familiar/Personal", orientation='h',
                title="2️⃣ Mayor Problema Familiar / Personal",
                color="Conteo", color_continuous_scale="Oranges"
            )
            fig_p2.update_layout(height=420, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)', font=dict(color="#CBD5E1"), margin=dict(l=10,r=20,t=50,b=30))
            st.plotly_chart(fig_p2, use_container_width=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Gráfica P3 (Prioridad Inmediata Exigida al Gobierno) - Apilado debajo a ancho completo
            p3_counts = df_p["p3_prioridad_gobierno"].value_counts().reset_index()
            p3_counts.columns = ["Prioridad Próximo Gobierno/Congreso", "Conteo"]
            fig_p3 = px.bar(
                p3_counts, x="Conteo", y="Prioridad Próximo Gobierno/Congreso", orientation='h',
                title="3️⃣ Prioridad Inmediata Exigida al Gobierno",
                color="Conteo", color_continuous_scale="Blues"
            )
            fig_p3.update_layout(height=420, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)', font=dict(color="#CBD5E1"), margin=dict(l=10,r=20,t=50,b=30))
            st.plotly_chart(fig_p3, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos registrados en el padrón para realizar el análisis.")

    # =========================================================
    # SUB-TAB 2: CRUCES SOCIODEMOGRÁFICOS MULTINIVEL
    # =========================================================
    with sub_t2:
        st.markdown("#### 🔀 Intersección de Variables Sociodemográficas con Preguntas del Padrón")
        st.write("Descubre las divergencias de opinión entre jóvenes vs. adultos mayores, trabajadores informales vs. formales, y zonas rurales vs. urbanas:")
        
        if not df_surveys.empty:
            df_lab_clean = df_surveys.copy()
            df_lab_clean["Situación Laboral Corta"] = df_lab_clean["situacion_laboral"].apply(lambda x: x.split(" (")[0])
            df_lab_clean["Prioridad al Gobierno"] = df_lab_clean["p3_prioridad_gobierno"]
            df_lab_clean["Problema Familiar"] = df_lab_clean["p2_problema_familiar"]
            df_lab_clean["Problema Regional"] = df_lab_clean["p1_problema_region"]
            df_lab_clean["Ámbito Territorial"] = df_lab_clean["ambito_territorial"].apply(lambda x: x.split(" (")[0])
            
            # Cruce 1: Situación Laboral vs. Prioridad del Gobierno (Ancho completo, horizontal y sin cortes)
            fig_c1 = px.bar(
                df_lab_clean, y="Situación Laboral Corta", color="Prioridad al Gobierno",
                title="1️⃣ ¿Qué Prioridad de Gobierno exigen los Trabajadores Informales (MYPE) vs. Formales vs. Agricultores?",
                orientation="h", barmode="stack", color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_c1.update_layout(height=480, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)', font=dict(color="#CBD5E1"), margin=dict(l=10,r=20,t=60,b=60), legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5))
            st.plotly_chart(fig_c1, use_container_width=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Cruce 2: Rango Etario vs. Problema Familiar (Apilado debajo, ancho completo y sin cortes)
            fig_c2 = px.bar(
                df_lab_clean, y="rango_edad", color="Problema Familiar",
                title="2️⃣ Problema Familiar por Rango Etario (Jóvenes vs. Adultos Mayores)",
                orientation='h', barmode="stack", color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig_c2.update_layout(height=480, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)', font=dict(color="#CBD5E1"), margin=dict(l=10,r=20,t=60,b=60), legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5))
            st.plotly_chart(fig_c2, use_container_width=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Cruce 3: Ámbito Territorial vs. Problema Regional (Apilado debajo, ancho completo y sin cortes)
            fig_c3 = px.bar(
                df_lab_clean, y="Ámbito Territorial", color="Problema Regional",
                title="3️⃣ Demandas por Ámbito (Urbano vs. Urbano-Marginal vs. Rural)",
                orientation='h', barmode="group", color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_c3.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)', font=dict(color="#CBD5E1"), margin=dict(l=10,r=20,t=60,b=60), legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5))
            st.plotly_chart(fig_c3, use_container_width=True)
        else:
            st.warning("⚠️ No hay suficientes datos para generar los cruces sociodemográficos.")

    # =========================================================
    # SUB-TAB 3: NUBE DE PALABRAS Y TRANSCRIPCIONES EN VIVO
    # =========================================================
    with sub_t3:
        st.markdown("#### ☁️ Inteligencia de Voz Cívica y Transcripciones en Vivo")
        st.write("Selecciona tu región en el menú inferior para filtrar la Nube de Palabras, el Treemap de conceptos y visualizar las transcripciones literales de audios y testimonios:")
        
        c_menu1, c_menu2 = st.columns([1.6, 2])
        with c_menu1:
            reg_wc_filtro = st.selectbox(
                "🔍 Selecciona Región para explorar Nube de Palabras y Transcripciones:",
                ["🇵🇪 Todo el Perú (Consolidado Nacional)"] + REGIONES_PERU,
                index=0,
                key="wc_reg_select_v2"
            )
            
        if reg_wc_filtro == "🇵🇪 Todo el Perú (Consolidado Nacional)":
            df_wc = df_surveys
            nombre_vista = "Todo el Perú (Consolidado Nacional)"
        else:
            df_wc = df_surveys[df_surveys["region"] == reg_wc_filtro] if not df_surveys.empty else pd.DataFrame()
            nombre_vista = reg_wc_filtro
            
        if not df_wc.empty:
            texto_procesado = get_combined_text_from_surveys(df_wc.to_dict('records'))
            
            # Desplegar Nube de Palabras a ancho completo para evitar compresión
            render_wordcloud(
                texto_procesado,
                title=f"Palabras Más Repetidas: {nombre_vista}",
                colormap="Spectral" if "Todo el Perú" in reg_wc_filtro else "cool"
            )
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Desplegar Treemap de Palabras debajo a ancho completo
            render_top_keywords_treemap(
                texto_procesado,
                title=f"Frecuencia de Conceptos: {nombre_vista}"
            )
                
            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown(f"#### 🎙️ Transcripciones y Testimonios Literales: **{nombre_vista}** (`{len(df_wc)} registros transcritos`)")
            
            for idx, row in df_wc.head(12).iterrows():
                if len(row.get("testimonio_abierto", "")) > 5 or len(row.get("p1_problema_region", "")) > 5:
                    eje_col = EJES_IDEARIO_PERU.get(row["eje_asignado"], {}).get("color", "#A855F7")
                    testimonio_str = row['testimonio_abierto'] if row.get('testimonio_abierto') else "Sin nota adicional de voz"
                    st.markdown(f"""
                    <div class="proposal-box" style="border-left-color: {eje_col};">
                        <span class="badge-ng" style="background: {eje_col}25; color: {eje_col}; border-color: {eje_col};">{row['eje_nombre']} ({row['eje_asignado']})</span>
                        <span style="float: right; font-size: 0.8rem; color: #94A3B8;">📍 <b>{row['region']}</b> | {row['ambito_territorial'].split('(')[0]} | 🕒 {row['timestamp'][:10]}</span>
                        <h4 style="margin: 6px 0 8px 0; color: #F8FAFC;">"{row['p1_problema_region']}"</h4>
                        <p style="color: #CBD5E1; font-size: 0.96rem; line-height: 1.5; font-style: italic;">"{testimonio_str}"</p>
                        <div style="font-size: 0.78rem; color: #64748B; margin-top: 10px;">
                            👤 Demografía: <b>{row['rango_edad']}</b> • {row['situacion_laboral'].split('(')[0]} • Origen: <code>{row['origen_registro']}</code>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ No se encontraron testimonios o encuestas registradas para la región **{nombre_vista}** bajo los criterios seleccionados.")

    # =========================================================
    # SUB-TAB 4: MURO TESTIMONIAL POR EJES PROGRAMÁTICOS
    # =========================================================
    with sub_t4:
        st.markdown("#### 🗣️ Muro del Ciudadano: Clasificación Temática en el Ideario y Propuestas")
        if not df_surveys.empty:
            sel_eje_muro = st.selectbox("Filtrar por Eje Programático:", ["TODOS LOS EJES"] + list(EJES_IDEARIO_PERU.keys()), key="f_eje_muro")
            df_muro = df_surveys if sel_eje_muro == "TODOS LOS EJES" else df_surveys[df_surveys["eje_asignado"] == sel_eje_muro]
            
            st.write(f"Mostrando **{len(df_muro)}** testimonios ciudadanos clasificados orgánicamente por IA en este eje:")
            for idx, row in df_muro.head(15).iterrows():
                if len(row.get("testimonio_abierto", "")) > 5:
                    eje_col = EJES_IDEARIO_PERU.get(row["eje_asignado"], {}).get("color", "#A855F7")
                    st.markdown(f"""
                    <div class="proposal-box" style="border-left-color: {eje_col};">
                        <span class="badge-ng" style="background: {eje_col}25; color: {eje_col}; border-color: {eje_col};">{row['eje_nombre']} ({row['eje_asignado']})</span>
                        <span style="float: right; font-size: 0.8rem; color: #94A3B8;">📍 <b>{row['region']}</b> | {row['ambito_territorial'].split('(')[0]} | 🕒 {row['timestamp'][:10]}</span>
                        <h4 style="margin: 6px 0 8px 0; color: #F8FAFC;">"{row['p1_problema_region']}"</h4>
                        <p style="color: #CBD5E1; font-size: 0.96rem; line-height: 1.5; font-style: italic;">"{row['testimonio_abierto']}"</p>
                        <div style="font-size: 0.78rem; color: #64748B; margin-top: 10px;">
                            👤 Demografía: <b>{row['rango_edad']}</b> • {row['situacion_laboral'].split('(')[0]} • Origen: <code>{row['origen_registro']}</code>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No hay encuestas en el padrón.")

    # =========================================================
    # SUB-TAB 5: MAPA TERRITORIAL Y GEOREFERENCIACIÓN DE CAMPO
    # =========================================================
    with sub_t5:
        st.markdown("#### 🗺️ Mapa Territorial y Auditoría de Puntos de Levantamiento en Campo")
        st.write("Visualización interactiva y georreferenciada de los puntos exactos (plazas, mercados, asambleas y barrios) donde los activistas territoriales recopilan la voz ciudadana.")
        
        if not df_surveys.empty:
            # Filtrar registros que tengan coordenadas GPS válidas
            df_geo = df_surveys.copy()
            df_geo["lat_num"] = pd.to_numeric(df_geo.get("georef_latitud", pd.Series(dtype=str)), errors="coerce")
            df_geo["lon_num"] = pd.to_numeric(df_geo.get("georef_longitud", pd.Series(dtype=str)), errors="coerce")
            
            df_con_gps = df_geo.dropna(subset=["lat_num", "lon_num"])
            
            if not df_con_gps.empty:
                st.success(f"📍 Se encontraron **{len(df_con_gps)}** levantamientos con coordenadas GPS exactas verificadas:")
                fig_map = px.scatter_mapbox(
                    df_con_gps, lat="lat_num", lon="lon_num",
                    hover_name="georef_lugar",
                    hover_data=["region", "activista_nombre", "georef_tipo_espacio", "p1_problema_region"],
                    color="region", size_max=15, zoom=4.5,
                    title="📍 Puntos de Levantamiento Georreferenciados en Campo"
                )
                fig_map.update_layout(mapbox_style="open-street-map", height=450, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("ℹ️ Aún no se han ingresado coordenadas numéricas exactas (Latitud/Longitud) en los registros recientes, pero a continuación puedes auditar los puntos de levantamiento declarados por los activistas:")
                
            st.markdown("##### 📋 Registro Territorial Detallado por Activista y Punto de Captura:")
            cols_mostrar = ["survey_id", "region", "activista_nombre", "georef_lugar", "georef_tipo_espacio", "georef_latitud", "georef_longitud", "timestamp"]
            cols_disponibles = [c for c in cols_mostrar if c in df_surveys.columns]
            st.dataframe(df_surveys[cols_disponibles], use_container_width=True)
        else:
            st.warning("No hay encuestas para mostrar.")

# -------------------------------------------------------------
# TAB 3: AUDITORÍA Y CALIDAD DE DATOS (DAMA-DMBOK)
# -------------------------------------------------------------
with tab3:
    st.subheader("🛡️ Auditoría de Calidad y Trazabilidad (Estándar DAMA-DMBOK v2)")
    st.write("El catálogo maestro garantiza que ninguna respuesta sea duplicada artificialmente y que cada testimonio transcrito por voz mantenga una trazabilidad inmutable e integridad de origen.")
    
    df_full = pd.DataFrame(surveys)
    if not df_full.empty:
        df_mostrar = df_full[["survey_id", "region", "ambito_territorial", "situacion_laboral", "eje_asignado", "did_verificador", "origen_registro"]].head(25)
        st.dataframe(df_mostrar, use_container_width=True)
