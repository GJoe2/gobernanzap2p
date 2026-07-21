import re
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
import plotly.express as px
import streamlit as st

# Stopwords en español ampliadas y adaptadas al contexto de encuestas
STOPWORDS_ES = set(STOPWORDS).union({
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para",
    "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "porque",
    "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde",
    "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante",
    "ellos", "e", "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra",
    "él", "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella",
    "estar", "estas", "algunas", "algo", "nosotros", "mi", "mis", "tú", "te", "ti", "tu", "tus",
    "ellas", "nosotras", "vosotros", "vosotras", "os", "mío", "mía", "míos", "mías", "tuyo", "tuya",
    "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas", "nuestro", "nuestra", "nuestros", "nuestras",
    "vuestro", "vuestra", "vuestros", "vuestras", "esos", "esas", "estoy", "estás", "está", "estamos",
    "estáis", "están", "esté", "estés", "estemos", "estéis", "estén", "estaré", "estarás", "estará",
    "estaremos", "estaréis", "estarán", "estaría", "estarías", "estaríamos", "estaríais", "estarían",
    "estaba", "estabas", "estábamos", "estabais", "estaban", "estuve", "estuviste", "estuvo",
    "estuvimos", "estuvisteis", "estuvieron", "estuviera", "estuvieras", "estuviéramos", "estuvierais",
    "estuvieran", "estuviese", "estuvieses", "estuviésemos", "estuvieseis", "estuviesen", "estando",
    "estado", "estada", "estados", "estadas", "estad", "he", "has", "ha", "hemos", "habéis", "han",
    "haya", "hayas", "hayamos", "hayáis", "hayan", "habré", "habrás", "habrá", "habremos", "habréis",
    "habrán", "habría", "habrías", "habríamos", "habríais", "habrían", "había", "habías", "habíamos",
    "habíais", "habían", "hube", "hubiste", "hubo", "hubimos", "hubisteis", "hubieron", "hubiera",
    "hubieras", "hubiéramos", "hubierais", "hubieran", "hubiese", "hubieses", "hubiésemos", "hubieseis",
    "hubiesen", "habiendo", "habido", "habida", "habidos", "habidas", "soy", "eres", "es", "somos",
    "sois", "son", "sea", "seas", "seamos", "seáis", "sean", "seré", "serás", "será", "seremos",
    "seréis", "serán", "sería", "serías", "seríamos", "seríais", "serían", "era", "eras", "éramos",
    "erais", "eran", "fui", "fuiste", "fue", "fuimos", "fuisteis", "fueron", "fuera", "fueras",
    "fuéramos", "fuerais", "fueran", "fuese", "fueses", "fuésemos", "fueseis", "fuesen", "siendo",
    "sido", "tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen", "tenga", "tengas", "tengamos",
    "tengáis", "tengan", "tendré", "tendrás", "tendrá", "tendremos", "tendréis", "tendrán", "tendría",
    "tendrías", "tendríamos", "tendríais", "tendrían", "tenía", "tenías", "teníamos", "teníais",
    "tenían", "tuve", "tuviste", "tuvo", "tuvimos", "tuvisteis", "tuvieron", "tuviera", "tuvieras",
    "tuviéramos", "tuvierais", "tuvieran", "tuviese", "tuvieses", "tuviésemos", "tuvieseis", "tuviesen",
    "teniendo", "tenido", "tenida", "tenidos", "tenidas", "tened",
    # Palabras comunes de encuestas/relleno
    "aquí", "aca", "mire", "joven", "señor", "pues", "hace", "años", "año", "solo", "toda", "vez",
    "cada", "viene", "va", "van", "estar", "ver", "dice", "hacer", "problema", "problemas", "falta",
    "necesitamos", "gente", "ahora", "menos", "bien", "mal", "mas"
})

def get_combined_text_from_surveys(surveys_list):
    """
    Combina los testimonios de voz transcritos y las respuestas declaradas en un solo gran texto limpio.
    """
    text_chunks = []
    for s in surveys_list:
        test = s.get("testimonio_abierto", "")
        p1 = s.get("p1_problema_region", "")
        # Si el testimonio tiene contenido, lo priorizamos y sumamos palabras clave de P1
        if len(test) > 5:
            text_chunks.append(f"{test} {p1}")
        elif len(p1) > 5:
            text_chunks.append(p1)
    return " ".join(text_chunks)

def render_wordcloud(text, title="Nube de Palabras de Voz y Testimonios", colormap="Spectral"):
    """
    Genera y renderiza una Nube de Palabras de alta estética con fondo oscuro.
    """
    if not text or len(text.strip()) < 10:
        st.info("⚠️ No hay suficientes testimonios transcritos o palabras para generar el Word Cloud en esta vista.")
        return

    # Limpieza previa y normalización
    clean_words = []
    for word in re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{3,}\b', text.lower()):
        if word not in STOPWORDS_ES and len(word) > 2:
            clean_words.append(word)

    if not clean_words:
        st.info("⚠️ Las palabras recopiladas son mayormente pronombres o conectores.")
        return

    joined_clean = " ".join(clean_words)

    wc = WordCloud(
        width=850,
        height=420,
        background_color="#0F172A",
        colormap=colormap,
        stopwords=STOPWORDS_ES,
        max_words=100,
        prefer_horizontal=0.85,
        min_font_size=12,
        max_font_size=75,
        random_state=42
    ).generate(joined_clean)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#0F172A")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout(pad=0)
    
    st.markdown(f"<h4 style='color: #F8FAFC; margin-bottom: 8px; font-size: 1.15rem;'>☁️ {title}</h4>", unsafe_allow_html=True)
    st.pyplot(fig)
    plt.close(fig)

def render_top_keywords_treemap(text, title="Top Conceptos y Términos Más Frecuentes"):
    """
    Genera un gráfico interactivo Treemap de Plotly con las palabras y conceptos más repetidos.
    """
    if not text or len(text.strip()) < 10:
        return

    words = []
    for word in re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{4,}\b', text.lower()):
        if word not in STOPWORDS_ES:
            words.append(word)

    if not words:
        return

    counts = Counter(words).most_common(22)
    df_kw = pd.DataFrame(counts, columns=["Palabra / Concepto", "Frecuencia"])
    df_kw["Categoría"] = "Términos Cívicos en Vivo"

    fig = px.treemap(
        df_kw,
        path=["Categoría", "Palabra / Concepto"],
        values="Frecuencia",
        color="Frecuencia",
        color_continuous_scale="Reds",
        title=f"📊 {title}"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#E2E8F0"),
        margin=dict(l=5, r=5, t=35, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

REGION_COORDS = {
    "Amazonas": {"lat": -6.2317, "lon": -77.8690},
    "Áncash": {"lat": -9.5278, "lon": -77.5278},
    "Apurímac": {"lat": -13.6339, "lon": -73.3644},
    "Arequipa": {"lat": -16.4090, "lon": -71.5375},
    "Ayacucho": {"lat": -13.1588, "lon": -74.2239},
    "Cajamarca": {"lat": -7.1638, "lon": -78.5003},
    "Callao (Provincia Constitucional)": {"lat": -12.0566, "lon": -77.1181},
    "Cusco": {"lat": -13.5319, "lon": -71.9675},
    "Huancavelica": {"lat": -12.7864, "lon": -74.9727},
    "Huánuco": {"lat": -9.9306, "lon": -76.2422},
    "Ica": {"lat": -14.0678, "lon": -75.7286},
    "Junín": {"lat": -11.5415, "lon": -74.8839},
    "La Libertad": {"lat": -7.8631, "lon": -78.5003},
    "Lambayeque": {"lat": -6.7714, "lon": -79.8409},
    "Lima Metropolitana": {"lat": -12.0464, "lon": -77.0428},
    "Lima Provincias": {"lat": -11.1925, "lon": -77.6106},
    "Loreto": {"lat": -4.1420, "lon": -74.5828},
    "Madre de Dios": {"lat": -12.5933, "lon": -70.0350},
    "Moquegua": {"lat": -17.1936, "lon": -70.9333},
    "Pasco": {"lat": -10.6675, "lon": -76.2567},
    "Piura": {"lat": -5.1945, "lon": -80.6328},
    "Puno": {"lat": -15.8402, "lon": -70.0219},
    "San Martín": {"lat": -6.4833, "lon": -76.3667},
    "Tacna": {"lat": -18.0066, "lon": -70.2463},
    "Tumbes": {"lat": -3.5669, "lon": -80.4515},
    "Ucayali": {"lat": -8.3791, "lon": -74.5539}
}

def render_semantic_map_peru(df_surveys):
    """
    Genera un mapa georreferenciado del Perú y una tabla de auditoría con el Top 5 de palabras claves más repetidas por cada región.
    """
    if df_surveys.empty:
        st.info("⚠️ No hay encuestas disponibles para calcular el mapa de palabras claves por región.")
        return

    map_data = []
    
    for reg_name, coords in REGION_COORDS.items():
        df_reg = df_surveys[df_surveys["region"] == reg_name]
        voces_cnt = len(df_reg)
        
        if voces_cnt > 0:
            texto_reg = get_combined_text_from_surveys(df_reg.to_dict('records'))
            words = []
            for word in re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{4,}\b', texto_reg.lower()):
                if word not in STOPWORDS_ES:
                    words.append(word)
            
            top5 = Counter(words).most_common(5)
            if top5:
                top1_kw = top5[0][0].capitalize()
                top5_str = " | ".join([f"{idx+1}. {w.capitalize()} ({cnt})" for idx, (w, cnt) in enumerate(top5)])
            else:
                top1_kw = "General"
                top5_str = "Sin palabras clave destacadas"
            
            eje_pred = df_reg["eje_nombre"].mode()[0] if "eje_nombre" in df_reg.columns and not df_reg["eje_nombre"].empty else "Variado"
            
            map_data.append({
                "Región": reg_name,
                "lat": coords["lat"],
                "lon": coords["lon"],
                "Voces Analizadas": voces_cnt,
                "Top 1 Palabra Clave": top1_kw,
                "Top 5 Palabras Claves": top5_str,
                "Eje Predominante": eje_pred
            })

    if not map_data:
        st.info("⚠️ Aún no se han registrado voces suficientes en las regiones continentales del Perú.")
        return

    df_map = pd.DataFrame(map_data)

    st.markdown("#### 🗺️ Mapa Semántico del Perú: Top 5 Palabras Claves por Región")
    st.write("Explora el mapa interactivo posicionando el cursor sobre cada departamento para visualizar las demandas exactas y el ranking de las 5 palabras más repetidas por la ciudadanía en esa localidad:")

    fig = px.scatter_mapbox(
        df_map,
        lat="lat",
        lon="lon",
        hover_name="Región",
        hover_data={
            "lat": False,
            "lon": False,
            "Voces Analizadas": True,
            "Top 1 Palabra Clave": True,
            "Top 5 Palabras Claves": True,
            "Eje Predominante": True
        },
        size="Voces Analizadas",
        color="Top 1 Palabra Clave",
        size_max=22,
        zoom=4.2,
        center=dict(lat=-9.19, lon=-75.01),
        title="📍 Geografía Semántica: ¿Qué pide cada región del Perú?"
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        height=520,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#E2E8F0"),
        margin=dict(l=0, r=0, t=45, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("##### 📋 Tabla Maestro: Ranking Top 5 de Palabras Claves por cada Región del Perú")
    df_tabla = df_map[["Región", "Voces Analizadas", "Top 1 Palabra Clave", "Top 5 Palabras Claves", "Eje Predominante"]].sort_values(by="Voces Analizadas", ascending=False)
    st.dataframe(df_tabla, use_container_width=True)
