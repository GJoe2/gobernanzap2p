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
