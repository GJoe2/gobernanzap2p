import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np

def render_polis_clustering(polis_clusters, consensus_bridges):
    """
    Renderiza la visualización tipo Polis (vTaiwan/Audrey Tang) para mostrar
    el clustering PCA de facciones de opinión y las propuestas de consenso puente.
    """
    st.subheader("🎯 Mapeo Deliberativo IA: Facciones Ideológicas vs. Consenso Puente")
    st.write("El algoritmo de *Polis* agrupa a los militantes en función de cómo votan las distintas premisas. En lugar de enfocarse en lo que divide, el sistema resalta automáticamente los **Puentes de Consenso** (propuestas que superan el 70% de aprobación simultánea en clústeres opuestos).")

    if not polis_clusters:
        st.warning("No hay clústeres deliberativos disponibles.")
        return

    # Generar nube de puntos PCA simulada alrededor de los centroides de los clústeres
    np.random.seed(42)
    cluster_points = []
    
    for c in polis_clusters:
        n_points = int(c.get("size_percent", 33) * 2.5)
        cx = c.get("pos_x", 0)
        cy = c.get("pos_y", 0)
        
        xs = np.random.normal(cx, 0.18, n_points)
        ys = np.random.normal(cy, 0.18, n_points)
        
        for x, y in zip(xs, ys):
            cluster_points.append({
                "x": x,
                "y": y,
                "cluster_name": c.get("name"),
                "traits": ", ".join(c.get("key_traits", [])),
                "color": c.get("color", "#3B82F6")
            })

    df_points = pd.DataFrame(cluster_points)

    col_chart, col_bridges = st.columns([1.3, 1])

    with col_chart:
        fig = px.scatter(
            df_points, x="x", y="y", color="cluster_name",
            color_discrete_map={c["name"]: c["color"] for c in polis_clusters},
            title="Mapa PCA 2D del Espacio de Opinión Partidaria",
            labels={"x": "Eje Ideológico 1 (Descentralización / Estado)", "y": "Eje Ideológico 2 (Innovación / Conservación)"},
            hover_data=["traits"]
        )
        
        # Añadir centroides destacados
        for c in polis_clusters:
            fig.add_trace(go.Scatter(
                x=[c["pos_x"]], y=[c["pos_y"]],
                mode="markers+text",
                name=f"Centroide {c['name']}",
                text=[c["name"].replace("Facción ", "")],
                textposition="top center",
                textfont=dict(size=12, color="white", family="Outfit"),
                marker=dict(size=22, symbol="star", color=c["color"], line=dict(width=2, color="white")),
                showlegend=False
            ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15,23,42,0.5)',
            margin=dict(l=10, r=10, t=45, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(color="#CBD5E1")),
            xaxis=dict(showgrid=True, gridcolor='rgba(148,163,184,0.15)', zerolinecolor='rgba(148,163,184,0.4)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(148,163,184,0.15)', zerolinecolor='rgba(148,163,184,0.4)')
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_bridges:
        st.markdown("<h4 style='color: #10B981; font-size: 1.2rem; margin-bottom: 15px;'>🌉 Afirmaciones Puente de Consenso (Bridging Statements)</h4>", unsafe_allow_html=True)
        st.write("Estas propuestas unen a todas las facciones del partido y son candidatas indiscutibles a ser incluidas en el **Ideario Maestro**:")
        
        for idx, bridge in enumerate(consensus_bridges, 1):
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10B981; border-radius: 10px; padding: 15px; margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; color: #34D399; font-size: 0.8rem;">⚡ CONSENSO GLOBAL: {bridge['overall_consensus']}%</span>
                    <span style="background: #10B981; color: #0F172A; padding: 2px 8px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700;">PUENTE VALIDADO</span>
                </div>
                <p style="color: #F8FAFC; font-size: 0.95rem; font-weight: 600; margin: 6px 0;">"{bridge['statement']}"</p>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 8px;">
                    Aprobación por Facción: 
                    <b>C1 ({bridge['approval_cluster_1']}%)</b> • 
                    <b>C2 ({bridge['approval_cluster_2']}%)</b> • 
                    <b>C3 ({bridge['approval_cluster_3']}%)</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
