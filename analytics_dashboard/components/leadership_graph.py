import networkx as nx
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def render_leadership_graph(delegations, afiliados, selected_axis="ECO-01"):
    """
    Construye y renderiza el grafo de democracia líquida P2P usando NetworkX y Plotly.
    Calcula métricas de centralidad de PageRank y In-Degree para identificar a los líderes orgánicos
    del partido en el eje seleccionado.
    """
    if not delegations or not afiliados:
        st.warning("No hay suficientes datos para generar el grafo de delegación.")
        return

    # Filtrar delegaciones por el eje seleccionado (o todas)
    if selected_axis != "TODOS":
        del_filtered = [d for d in delegations if d.get("axis_code") == selected_axis and d.get("status") == "ACTIVE_DELEGATION"]
    else:
        del_filtered = [d for d in delegations if d.get("status") == "ACTIVE_DELEGATION"]

    G = nx.DiGraph()

    # Mapeo rápido de DIDs a Alias
    alias_map = {a["did_id"]: a["alias_civico"] for a in afiliados}
    rol_map = {a["did_id"]: a["rol_partidario"] for a in afiliados}

    for a in afiliados:
        G.add_node(a["did_id"], label=a["alias_civico"], rol=a["rol_partidario"])

    for d in del_filtered:
        if d["sender_did"] in alias_map and d["target_did"] in alias_map:
            if G.has_edge(d["sender_did"], d["target_did"]):
                G[d["sender_did"]][d["target_did"]]["weight"] += d.get("tokens_delegated", 100)
            else:
                G.add_edge(d["sender_did"], d["target_did"], weight=d.get("tokens_delegated", 100))

    # Calcular centralidad e in-degree (quién recibe más delegación líquida)
    in_degrees = dict(G.in_degree(weight="weight"))
    try:
        pageranks = nx.pagerank(G, weight="weight")
    except Exception:
        pageranks = {node: 1.0 for node in G.nodes()}

    # Calcular layout de resorte (spring layout) o Fruchterman-Reingold
    pos = nx.spring_layout(G, k=0.55, iterations=40, seed=42)

    # Dibujar aristas (Edges)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.2, color='rgba(148, 163, 184, 0.35)'),
        hoverinfo='none',
        mode='lines'
    )

    # Dibujar nodos (Nodes)
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    node_symbols = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        tokens_recibidos = in_degrees.get(node, 0)
        pr = round(pageranks.get(node, 0) * 1000, 1)
        alias = alias_map.get(node, "Militante")
        rol = rol_map.get(node, "SIMPATIZANTE")

        # Tamaño en función de tokens recibidos
        size = max(14, min(65, 14 + int(tokens_recibidos / 35)))
        node_size.append(size)

        # Color según el rol partidario
        if rol == "DELEGADO_TEMATICO":
            node_color.append("#3B82F6") # Azul brillante
            node_symbols.append("diamond")
        elif rol == "MILITANTE_VERIFICADO":
            node_color.append("#10B981") # Verde
            node_symbols.append("circle")
        else:
            node_color.append("#64748B") # Gris
            node_symbols.append("circle")

        node_text.append(f"<b>{alias}</b><br>Rol: {rol}<br>Tokens Delegados Recibidos: {tokens_recibidos}<br>Índice PageRank P2P: {pr}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[alias_map.get(n, "") if in_degrees.get(n, 0) >= 200 else "" for n in G.nodes()],
        textposition="top center",
        textfont=dict(family="Inter", size=11, color="#F8FAFC"),
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            symbol=node_symbols,
            line_width=2,
            line_color='#0F172A'
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=dict(
                        text=f"🌐 Grafo P2P de Democracia Líquida — Eje: <b>{selected_axis}</b>",
                        font=dict(family="Outfit", size=18, color="#F8FAFC")
                    ),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=50),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                ))

    st.plotly_chart(fig, use_container_width=True)

    # Ranking de Líderes Orgánicos
    st.subheader("🏆 Top Referentes Técnicos Legitimados por las Bases")
    top_leaders = sorted([(node, in_degrees.get(node, 0), pageranks.get(node, 0)) for node in G.nodes() if in_degrees.get(node, 0) > 0], key=lambda x: x[1], reverse=True)[:6]
    
    cols = st.columns(min(3, len(top_leaders)) if top_leaders else 1)
    for idx, (node, tokens, pr) in enumerate(top_leaders):
        col_idx = idx % 3
        with cols[col_idx]:
            alias = alias_map.get(node, "Desconocido")
            rol = rol_map.get(node, "")
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                <span style="font-size: 0.75rem; color: #60A5FA; text-transform: uppercase; font-weight: 700;">#{idx+1} LÍDER DE CONFIANZA P2P</span>
                <h4 style="margin: 4px 0; color: #F8FAFC; font-size: 1.1rem;">{alias}</h4>
                <p style="margin: 0; font-size: 0.85rem; color: #94A3B8;">Rol: {rol}</p>
                <div style="margin-top: 8px; display: flex; justify-content: space-between; font-size: 0.85rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;">
                    <span>⚡ Tokens Recibidos: <b style="color: #3B82F6;">{tokens}</b></span>
                    <span>📈 PageRank: <b>{round(pr*1000, 1)}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
