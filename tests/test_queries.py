import pytest

from src.database import assert_read_only_sql
from src.queries import BASE_QUERIES, DIMENSION_QUERIES


@pytest.mark.parametrize("nome_query,sql", BASE_QUERIES.items())
def test_base_queries_are_read_only(nome_query, sql):
    assert_read_only_sql(sql)


@pytest.mark.parametrize("nome_query,sql", BASE_QUERIES.items())
def test_base_queries_filtram_por_periodo(nome_query, sql):
    assert ":data_inicio" in sql
    assert ":data_fim" in sql
    assert "vendas" in sql.lower()


@pytest.mark.parametrize(
    "nome_query",
    ["vendas_por_concessionaria", "vendas_por_estado", "vendas_por_cidade"],
)
def test_consultas_geograficas_usam_left_join(nome_query):
    assert "LEFT JOIN" in BASE_QUERIES[nome_query]


@pytest.mark.parametrize(
    "nome_query",
    ["ranking_vendedores", "desempenho_por_concessionaria"],
)
def test_desconto_usa_formula_correta_e_nao_esconde_negativos(nome_query):
    sql = BASE_QUERIES[nome_query]
    assert "ve.valor - v.valor_pago" in sql
    # Sem HAVING/filtro sobre o desconto agregado: vendas acima da tabela
    # (desconto negativo) continuam aparecendo no resultado.
    assert "HAVING" not in sql.upper()


def test_ranking_vendedores_filtra_por_concessionaria_opcional():
    sql = BASE_QUERIES["ranking_vendedores"]
    assert ":id_concessionaria" in sql
    assert "IS NULL" in sql


def test_modelos_mais_vendidos_filtra_por_concessionaria_opcional():
    sql = BASE_QUERIES["modelos_mais_vendidos"]
    assert ":id_concessionaria" in sql
    assert "IS NULL" in sql


@pytest.mark.parametrize("nome_query,sql", DIMENSION_QUERIES.items())
def test_dimension_queries_are_read_only(nome_query, sql):
    assert_read_only_sql(sql)
