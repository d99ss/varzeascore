import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from PIL import Image

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================

st.set_page_config(
    page_title="Grêmio Brasilândia F.S",
    layout="wide",
    page_icon="⚽"
)

# =========================
# ESTILO OFICIAL DO CLUBE
# =========================

st.markdown("""
<style>

/* Fundo geral */
.stApp {
    background-color: #FFFFFF;
}

/* Títulos */
h1 {
    color: #D71920;
    font-weight: 900;
}

h2, h3 {
    color: #D71920;
}

h4 {
    color: #C9A227;
}

/* Métricas */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #D71920 0%, #b0151b 100%);
    padding: 18px;
    border-radius: 14px;
    color: white;
    border: 3px solid #C9A227;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
}

div[data-testid="metric-container"] label {
    color: white !important;
    font-weight: bold;
}

/* Botões */
.stButton>button {
    background-color: #D71920;
    color: white;
    border-radius: 10px;
    border: 2px solid #C9A227;
    font-weight: bold;
    padding: 8px 20px;
}

.stButton>button:hover {
    background-color: #a50f14;
    color: white;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 2px solid #C9A227;
    border-radius: 12px;
}

/* Inputs */
input {
    border-radius: 8px !important;
    border: 2px solid #C9A227 !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    border: 2px solid #C9A227;
    border-radius: 8px;
}

/* Divider */
hr {
    border: 1px solid #C9A227;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER COM LOGO + TÍTULO
# =========================

logo = Image.open("logo_gremio.jpeg")

col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    st.image(logo, width=140)

with col_titulo:
    st.markdown("""
        <h1 style='margin-bottom:0;'>
            GRÊMIO BRASILÂNDIA F.S
        </h1>
        <h4 style='margin-top:5px;'>
            Painel Oficial de Estatísticas
        </h4>
    """, unsafe_allow_html=True)

st.divider()

# =========================
# CONFIGURAÇÃO SUPABASE
# =========================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# BUSCAR DADOS
# =========================

response = supabase.table("estatisticas") \
    .select("id, jogador, jogos, gols, assistencias") \
    .execute()

data = response.data

if data:
    df = pd.DataFrame(data)

    # =========================
    # MÉTRICAS
    # =========================

    total_jogadores = df["jogador"].nunique()
    total_gols = df["gols"].sum()
    total_assistencias = df["assistencias"].sum()
    total_jogos = df["jogos"].sum()

    media_gols = round(total_gols / total_jogos, 2) if total_jogos > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Jogadores", total_jogadores)
    col2.metric("⚽ Gols", total_gols)
    col3.metric("🎯 Assistências", total_assistencias)
    col4.metric("📊 Média de Gols/Jogo", media_gols)

    st.divider()

    # =========================
    # RANKING
    # =========================

    st.subheader("🏆 Ranking de Artilheiros")

    ranking = df.sort_values(by="gols", ascending=False)

    st.dataframe(
        ranking[["jogador", "gols", "assistencias", "jogos"]],
        width="stretch"
    )

    st.divider()

    # =========================
    # GRÁFICOS PERSONALIZADOS
    # =========================

    st.subheader("📈 Desempenho por Jogador")

    col_gols, col_assist = st.columns(2)

    # 🔴 GOLS
    with col_gols:
        st.markdown("### ⚽ Gols")

        fig_gols = px.bar(
            ranking,
            x="jogador",
            y="gols",
            text="gols"
        )

        fig_gols.update_traces(
            marker_color="#D71920",
            textposition="outside"
        )

        fig_gols.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#D71920"),
            xaxis_title="",
            yaxis_title="Gols",
            showlegend=False
        )

        st.plotly_chart(fig_gols, use_container_width=True)

    # 🟡 ASSISTÊNCIAS
    with col_assist:
        st.markdown("### 🎯 Assistências")

        fig_assist = px.bar(
            ranking,
            x="jogador",
            y="assistencias",
            text="assistencias"
        )

        fig_assist.update_traces(
            marker_color="#C9A227",
            textposition="outside"
        )

        fig_assist.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#D71920"),
            xaxis_title="",
            yaxis_title="Assistências",
            showlegend=False
        )

        st.plotly_chart(fig_assist, use_container_width=True)

    st.divider()

    # =========================
    # REMOVER JOGADOR
    # =========================

    st.subheader("🗑️ Remover Jogador")

    ids = {f"{item['jogador']} ({item['id'][:8]})": item["id"] for item in data}

    selected = st.selectbox("Selecione o jogador", list(ids.keys()))

    if st.button("Remover"):
        supabase.table("estatisticas") \
            .delete() \
            .eq("id", ids[selected]) \
            .execute()

        st.success("Jogador removido com sucesso!")
        st.rerun()

else:
    st.info("Nenhum registro encontrado.")

# =========================
# FORMULÁRIO
# =========================

st.divider()
st.subheader("➕ Adicionar Estatísticas")

with st.form("add_stats_form"):
    jogador = st.text_input("Nome do Jogador")
    jogos = st.number_input("Jogos", min_value=0, max_value=200, step=1)
    gols = st.number_input("Gols", min_value=0, max_value=200, step=1)
    assistencias = st.number_input("Assistências", min_value=0, max_value=200, step=1)

    submit = st.form_submit_button("Salvar Estatísticas")

    if submit:
        if jogador.strip() == "":
            st.error("O nome do jogador é obrigatório.")
        else:
            supabase.table("estatisticas").insert({
                "jogador": jogador,
                "jogos": jogos,
                "gols": gols,
                "assistencias": assistencias
            }).execute()

            st.success("Estatísticas salvas com sucesso!")
            st.rerun()
