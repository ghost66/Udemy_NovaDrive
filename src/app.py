import sys
from datetime import date
from pathlib import Path

import plotly.express as px
import streamlit as st

# `streamlit run` só adiciona a pasta deste arquivo ao sys.path, não a raiz
# do projeto — garantimos aqui que `import src` funciona independente de
# onde/como o comando for executado.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import queries
from src.database import DatabaseConnectionError
from src.projecao import calcular_projecao_run_rate, periodo_e_mes_corrente

st.set_page_config(page_title="Dashboard Executivo", layout="wide")
st.title("Dashboard Executivo")

hoje = date.today()
data_inicio = st.sidebar.date_input("Data inicial", value=hoje.replace(day=1))
data_fim = st.sidebar.date_input("Data final", value=hoje)

if data_inicio > data_fim:
    st.error("Data inicial não pode ser maior que a data final.")
    st.stop()

try:
    faturamento = queries.get_faturamento_periodo(data_inicio, data_fim)
    quantidade = queries.get_quantidade_vendas_periodo(data_inicio, data_fim)
    ticket_medio = queries.get_ticket_medio_periodo(data_inicio, data_fim)
    df_evolucao = queries.get_vendas_por_dia(data_inicio, data_fim)
    df_concessionarias = queries.get_vendas_por_concessionaria(data_inicio, data_fim)
    df_estados = queries.get_vendas_por_estado(data_inicio, data_fim)
    df_cidades = queries.get_vendas_por_cidade(data_inicio, data_fim)
except DatabaseConnectionError as exc:
    st.error(str(exc))
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Faturamento", f"R$ {faturamento:,.2f}")
col2.metric("Quantidade vendida", quantidade)
col3.metric("Ticket médio", f"R$ {ticket_medio:,.2f}")

if periodo_e_mes_corrente(data_inicio, data_fim, hoje):
    projecao = calcular_projecao_run_rate(hoje)
    st.info(
        f"Projeção de fechamento do mês: R$ {projecao['projecao_mes']:,.2f} "
        f"(com base em {projecao['dias_passados']} de {projecao['dias_no_mes']} dias do mês). "
        "Estimativa simples (run-rate), não é previsão estatística."
    )

st.subheader("Evolução de vendas no período")
if df_evolucao.empty:
    st.info("Sem vendas no período selecionado.")
else:
    st.plotly_chart(
        px.line(df_evolucao, x="dia", y=["faturamento", "quantidade_vendas"], markers=True),
        use_container_width=True,
    )

st.subheader("Comparação entre concessionárias")
col_fat, col_qtd = st.columns(2)
col_fat.plotly_chart(
    px.bar(df_concessionarias, x="concessionaria", y="faturamento", title="Faturamento"),
    use_container_width=True,
)
col_qtd.plotly_chart(
    px.bar(df_concessionarias, x="concessionaria", y="quantidade_vendas", title="Quantidade vendida"),
    use_container_width=True,
)

st.subheader("Comparação por região")
col_estado, col_cidade = st.columns(2)
with col_estado:
    if df_estados.empty:
        st.info("Sem dados de estado disponíveis.")
    else:
        st.plotly_chart(
            px.bar(df_estados, x="estado", y="faturamento", title="Faturamento por estado"),
            use_container_width=True,
        )
with col_cidade:
    if df_cidades.empty:
        st.info("Sem dados de cidade disponíveis.")
    else:
        st.plotly_chart(
            px.bar(df_cidades, x="cidade", y="faturamento", title="Faturamento por cidade"),
            use_container_width=True,
        )
