from datetime import date
from typing import Optional

import pandas as pd
import streamlit as st

from .database import run_query

_SQL_FATURAMENTO_PERIODO = """
    SELECT COALESCE(SUM(valor_pago), 0) AS faturamento
    FROM vendas
    WHERE data_venda BETWEEN :data_inicio AND :data_fim
"""

_SQL_QUANTIDADE_VENDAS_PERIODO = """
    SELECT COUNT(*) AS quantidade_vendas
    FROM vendas
    WHERE data_venda BETWEEN :data_inicio AND :data_fim
"""

_SQL_TICKET_MEDIO_PERIODO = """
    SELECT COALESCE(AVG(valor_pago), 0) AS ticket_medio
    FROM vendas
    WHERE data_venda BETWEEN :data_inicio AND :data_fim
"""

_SQL_VENDAS_POR_DIA = """
    SELECT
        data_venda::date AS dia,
        SUM(valor_pago) AS faturamento,
        COUNT(*) AS quantidade_vendas
    FROM vendas
    WHERE data_venda BETWEEN :data_inicio AND :data_fim
    GROUP BY data_venda::date
    ORDER BY data_venda::date
"""

_SQL_VENDAS_POR_CONCESSIONARIA = """
    SELECT
        c.concessionaria AS concessionaria,
        COALESCE(SUM(v.valor_pago), 0) AS faturamento,
        COALESCE(COUNT(v.id_vendas), 0) AS quantidade_vendas
    FROM concessionarias c
    LEFT JOIN vendas v
        ON v.id_concessionarias = c.id_concessionarias
        AND v.data_venda BETWEEN :data_inicio AND :data_fim
    GROUP BY c.id_concessionarias, c.concessionaria
    ORDER BY faturamento DESC
"""

_SQL_VENDAS_POR_ESTADO = """
    SELECT
        e.estado AS estado,
        COALESCE(SUM(v.valor_pago), 0) AS faturamento,
        COALESCE(COUNT(v.id_vendas), 0) AS quantidade_vendas
    FROM estados e
    LEFT JOIN cidades ci ON ci.id_estados = e.id_estados
    LEFT JOIN concessionarias c ON c.id_cidades = ci.id_cidades
    LEFT JOIN vendas v
        ON v.id_concessionarias = c.id_concessionarias
        AND v.data_venda BETWEEN :data_inicio AND :data_fim
    GROUP BY e.id_estados, e.estado
    ORDER BY faturamento DESC
"""

_SQL_VENDAS_POR_CIDADE = """
    SELECT
        ci.cidade AS cidade,
        COALESCE(SUM(v.valor_pago), 0) AS faturamento,
        COALESCE(COUNT(v.id_vendas), 0) AS quantidade_vendas
    FROM cidades ci
    LEFT JOIN concessionarias c ON c.id_cidades = ci.id_cidades
    LEFT JOIN vendas v
        ON v.id_concessionarias = c.id_concessionarias
        AND v.data_venda BETWEEN :data_inicio AND :data_fim
    GROUP BY ci.id_cidades, ci.cidade
    ORDER BY faturamento DESC
"""

_SQL_RANKING_VENDEDORES = """
    SELECT
        vd.nome AS vendedor,
        c.concessionaria AS concessionaria,
        COALESCE(SUM(v.valor_pago), 0) AS faturamento,
        COALESCE(COUNT(v.id_vendas), 0) AS quantidade_vendas,
        COALESCE(AVG(v.valor_pago), 0) AS ticket_medio,
        COALESCE(AVG(ve.valor - v.valor_pago), 0) AS desconto_medio,
        COALESCE(AVG((ve.valor - v.valor_pago) / NULLIF(ve.valor, 0)), 0) AS desconto_percentual
    FROM vendedores vd
    JOIN concessionarias c ON c.id_concessionarias = vd.id_concessionarias
    LEFT JOIN vendas v
        ON v.id_vendedores = vd.id_vendedores
        AND v.data_venda BETWEEN :data_inicio AND :data_fim
    LEFT JOIN veiculos ve ON ve.id_veiculos = v.id_veiculos
    WHERE (:id_concessionaria IS NULL OR vd.id_concessionarias = :id_concessionaria)
    GROUP BY vd.id_vendedores, vd.nome, c.concessionaria
    ORDER BY faturamento DESC
"""

_SQL_DESEMPENHO_POR_CONCESSIONARIA = """
    SELECT
        c.concessionaria AS concessionaria,
        COALESCE(SUM(v.valor_pago), 0) AS faturamento,
        COALESCE(COUNT(v.id_vendas), 0) AS quantidade_vendas,
        COALESCE(AVG(v.valor_pago), 0) AS ticket_medio,
        COALESCE(AVG(ve.valor - v.valor_pago), 0) AS desconto_medio,
        COALESCE(AVG((ve.valor - v.valor_pago) / NULLIF(ve.valor, 0)), 0) AS desconto_percentual
    FROM concessionarias c
    LEFT JOIN vendas v
        ON v.id_concessionarias = c.id_concessionarias
        AND v.data_venda BETWEEN :data_inicio AND :data_fim
    LEFT JOIN veiculos ve ON ve.id_veiculos = v.id_veiculos
    GROUP BY c.id_concessionarias, c.concessionaria
    ORDER BY faturamento DESC
"""

_SQL_MODELOS_MAIS_VENDIDOS = """
    SELECT
        ve.nome AS modelo,
        ve.tipo AS tipo,
        COALESCE(SUM(v.valor_pago), 0) AS faturamento,
        COUNT(v.id_vendas) AS quantidade_vendas
    FROM veiculos ve
    JOIN vendas v ON v.id_veiculos = ve.id_veiculos
    WHERE v.data_venda BETWEEN :data_inicio AND :data_fim
        AND (:id_concessionaria IS NULL OR v.id_concessionarias = :id_concessionaria)
    GROUP BY ve.id_veiculos, ve.nome, ve.tipo
    ORDER BY quantidade_vendas DESC
"""

_SQL_CONCESSIONARIAS = """
    SELECT id_concessionarias, concessionaria
    FROM concessionarias
    ORDER BY concessionaria
"""

BASE_QUERIES = {
    "faturamento_periodo": _SQL_FATURAMENTO_PERIODO,
    "quantidade_vendas_periodo": _SQL_QUANTIDADE_VENDAS_PERIODO,
    "ticket_medio_periodo": _SQL_TICKET_MEDIO_PERIODO,
    "vendas_por_dia": _SQL_VENDAS_POR_DIA,
    "vendas_por_concessionaria": _SQL_VENDAS_POR_CONCESSIONARIA,
    "vendas_por_estado": _SQL_VENDAS_POR_ESTADO,
    "vendas_por_cidade": _SQL_VENDAS_POR_CIDADE,
    "ranking_vendedores": _SQL_RANKING_VENDEDORES,
    "desempenho_por_concessionaria": _SQL_DESEMPENHO_POR_CONCESSIONARIA,
    "modelos_mais_vendidos": _SQL_MODELOS_MAIS_VENDIDOS,
}

# Consultas de dimensão (sem filtro de período): usadas só para popular filtros na UI.
DIMENSION_QUERIES = {
    "concessionarias": _SQL_CONCESSIONARIAS,
}


@st.cache_data(ttl=60)
def get_faturamento_periodo(data_inicio: date, data_fim: date) -> float:
    df = run_query(_SQL_FATURAMENTO_PERIODO, {"data_inicio": data_inicio, "data_fim": data_fim})
    return float(df["faturamento"].iloc[0])


@st.cache_data(ttl=60)
def get_quantidade_vendas_periodo(data_inicio: date, data_fim: date) -> int:
    df = run_query(_SQL_QUANTIDADE_VENDAS_PERIODO, {"data_inicio": data_inicio, "data_fim": data_fim})
    return int(df["quantidade_vendas"].iloc[0])


@st.cache_data(ttl=60)
def get_ticket_medio_periodo(data_inicio: date, data_fim: date) -> float:
    df = run_query(_SQL_TICKET_MEDIO_PERIODO, {"data_inicio": data_inicio, "data_fim": data_fim})
    return float(df["ticket_medio"].iloc[0])


@st.cache_data(ttl=60)
def get_vendas_por_dia(data_inicio: date, data_fim: date) -> pd.DataFrame:
    return run_query(_SQL_VENDAS_POR_DIA, {"data_inicio": data_inicio, "data_fim": data_fim})


@st.cache_data(ttl=900)
def get_vendas_por_concessionaria(data_inicio: date, data_fim: date) -> pd.DataFrame:
    return run_query(_SQL_VENDAS_POR_CONCESSIONARIA, {"data_inicio": data_inicio, "data_fim": data_fim})


@st.cache_data(ttl=900)
def get_vendas_por_estado(data_inicio: date, data_fim: date) -> pd.DataFrame:
    return run_query(_SQL_VENDAS_POR_ESTADO, {"data_inicio": data_inicio, "data_fim": data_fim})


@st.cache_data(ttl=900)
def get_vendas_por_cidade(data_inicio: date, data_fim: date) -> pd.DataFrame:
    return run_query(_SQL_VENDAS_POR_CIDADE, {"data_inicio": data_inicio, "data_fim": data_fim})


@st.cache_data(ttl=900)
def get_ranking_vendedores(
    data_inicio: date, data_fim: date, id_concessionaria: Optional[int] = None
) -> pd.DataFrame:
    return run_query(
        _SQL_RANKING_VENDEDORES,
        {"data_inicio": data_inicio, "data_fim": data_fim, "id_concessionaria": id_concessionaria},
    )


@st.cache_data(ttl=900)
def get_desempenho_por_concessionaria(data_inicio: date, data_fim: date) -> pd.DataFrame:
    return run_query(
        _SQL_DESEMPENHO_POR_CONCESSIONARIA, {"data_inicio": data_inicio, "data_fim": data_fim}
    )


@st.cache_data(ttl=900)
def get_modelos_mais_vendidos(
    data_inicio: date, data_fim: date, id_concessionaria: Optional[int] = None
) -> pd.DataFrame:
    return run_query(
        _SQL_MODELOS_MAIS_VENDIDOS,
        {"data_inicio": data_inicio, "data_fim": data_fim, "id_concessionaria": id_concessionaria},
    )


@st.cache_data(ttl=900)
def get_concessionarias() -> pd.DataFrame:
    return run_query(_SQL_CONCESSIONARIAS)
