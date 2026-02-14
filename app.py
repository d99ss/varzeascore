import streamlit as st
import pandas as pd
from supabase import create_client

# =========================
# CONFIGURAÇÃO SUPABASE
# =========================

SUPABASE_URL = "https://hpkhpgplhmbqlumkemqi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhwa2hwZ3BsaG1icWx1bWtlbXFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzI1NDMsImV4cCI6MjA4NjE0ODU0M30.t595OHBgdooxvi5KFSH02E2yKWGPF5xJvLxzQfptRVA"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Football Analytics", layout="wide")

st.title("⚽ Football Analytics Dashboard")

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
    # MÉTRICAS PRINCIPAIS
    # =========================

    total_jogadores = df["jogador"].nunique()
    total_gols = df["gols"].sum()
    total_assistencias = df["assistencias"].sum()
    total_jogos = df["jogos"].sum()

    media_gols = round(total_gols / total_jogos, 2) if total_jogos > 0 else 0
    media_assist = round(total_assistencias / total_jogos, 2) if total_jogos > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Jogadores", total_jogadores)
    col2.metric("⚽ Gols", total_gols)
    col3.metric("🎯 Assistências", total_assistencias)
    col4.metric("📊 Média Gols/Jogo", media_gols)

    st.divider()

    # =========================
    # RANKING
    # =========================

    st.subheader("🏆 Ranking de Artilheiros")

    ranking = df.sort_values(by="gols", ascending=False)
    st.dataframe(ranking[["jogador", "gols", "assistencias", "jogos"]], use_container_width=True)

    st.divider()

    # =========================
    # GRÁFICOS
    # =========================

    st.subheader("📈 Estatísticas por Jogador")

    col_gols, col_assist = st.columns(2)

    with col_gols:
        st.markdown("### ⚽ Gols")
        gols_chart = ranking.set_index("jogador")
        st.bar_chart(gols_chart["gols"])

    with col_assist:
        st.markdown("### 🎯 Assistências")
        assist_chart = ranking.set_index("jogador")
        st.bar_chart(assist_chart["assistencias"])

    st.divider()

    # =========================
    # DELETE
    # =========================

    st.subheader("🗑️ Deletar Jogador")

    ids = {f"{item['jogador']} ({item['id'][:8]})": item["id"] for item in data}

    selected = st.selectbox("Selecione o jogador", list(ids.keys()))

    if st.button("Deletar"):
        supabase.table("estatisticas") \
            .delete() \
            .eq("id", ids[selected]) \
            .execute()

        st.success("Jogador deletado com sucesso!")
        st.rerun()

else:
    st.info("Nenhum registro encontrado.")

# =========================
# FORMULÁRIO DE INSERÇÃO
# =========================

st.divider()
st.subheader("➕ Adicionar Estatísticas")

with st.form("add_stats_form"):
    jogador = st.text_input("Nome do Jogador")
    jogos = st.number_input("Jogos", min_value=0, max_value=200, step=1)
    gols = st.number_input("Gols", min_value=0, max_value=200, step=1)
    assistencias = st.number_input("Assistências", min_value=0, max_value=200, step=1)

    submit = st.form_submit_button("Salvar")

    if submit:
        if jogador.strip() == "":
            st.error("O nome do jogador é obrigatório")
        else:
            supabase.table("estatisticas").insert({
                "jogador": jogador,
                "jogos": jogos,
                "gols": gols,
                "assistencias": assistencias
            }).execute()

            st.success("Estatísticas salvas com sucesso!")
            st.rerun()
