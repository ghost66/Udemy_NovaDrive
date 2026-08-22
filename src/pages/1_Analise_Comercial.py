import sys
from datetime import date
from pathlib import Path

import plotly.express as px
import streamlit as st

# `streamlit run` só adiciona a pasta deste arquivo ao sys.path, não a raiz
# do projeto — garantimos aqui que `import src` funciona independente de
# onde/como o comando for executado.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src import queries
from src.database import DatabaseConnectionError

st.set_page_config(page_title="Análise Comercial", layout="wide")
st.title("Análise Comercial")
st.caption(
    "Funil de conversão (leads/visitas) e veículos parados no pátio estão fora de escopo: "
    "o banco de dados não tem tabela de leads/visitas nem de estoque."
)

hoje = date.today()
data_inicio = st.sidebar.date_input("Data inicial", value=hoje.replace(day=1))
data_fim = st.sidebar.date_input("Data final", value=hoje)

if data_inicio > data_fim:
    st.error("Data inicial não pode ser maior que a data final.")
    st.stop()

try:
    df_concessionarias_lista = queries.get_concessionarias()
except DatabaseConnectionError as exc:
    st.error(str(exc))
    st.stop()

opcoes_concessionaria = {"Todas": None}
opcoes_concessionaria.update(
    dict(zip(df_concessionarias_lista["concessionaria"], df_concessionarias_lista["id_concessionarias"]))
)
concessionaria_selecionada = st.sidebar.selectbox("Concessionária", options=list(opcoes_concessionaria.keys()))
id_concessionaria = opcoes_concessionaria[concessionaria_selecionada]

try:
    df_ranking = queries.get_ranking_vendedores(data_inicio, data_fim, id_concessionaria)
    df_modelos = queries.get_modelos_mais_vendidos(data_inicio, data_fim, id_concessionaria)
    df_desempenho = queries.get_desempenho_por_concessionaria(data_inicio, data_fim)
except DatabaseConnectionError as exc:
    st.error(str(exc))
    st.stop()

st.subheader("Ranking de vendedores")
st.dataframe(
    df_ranking.rename(
        columns={
            "vendedor": "Vendedor",
            "concessionaria": "Concessionária",
            "faturamento": "Faturamento",
            "quantidade_vendas": "Quantidade vendida",
            "ticket_medio": "Ticket médio",
            "desconto_medio": "Desconto médio (R$)",
            "desconto_percentual": "Desconto médio (%)",
        }
    ),
    use_container_width=True,
)

st.subheader("Modelos mais vendidos")
if df_modelos.empty:
    st.info("Sem vendas no período/concessionária selecionados.")
else:
    st.plotly_chart(
        px.pie(
            df_modelos,
            names="modelo",
            values="quantidade_vendas",
            title="Participação de cada modelo na quantidade vendida",
        ),
        use_container_width=True,
    )

st.subheader("Comparação entre concessionárias")
concessionarias_com_venda = df_desempenho[df_desempenho["quantidade_vendas"] > 0]
if len(concessionarias_com_venda) <= 1:
    st.info("É preciso mais de uma concessionária com vendas no período para comparar.")
else:
    col_ticket, col_desconto = st.columns(2)
    col_ticket.plotly_chart(
        px.bar(df_desempenho, x="concessionaria", y="ticket_medio", title="Ticket médio por concessionária"),
        use_container_width=True,
    )
    col_desconto.plotly_chart(
        px.bar(
            df_desempenho,
            x="concessionaria",
            y="desconto_percentual",
            title="Desconto médio (%) por concessionária",
        ),
        use_container_width=True,
    )
