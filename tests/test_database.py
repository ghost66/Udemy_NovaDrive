import pytest
from sqlalchemy.exc import OperationalError

from src import database
from src.database import DatabaseConnectionError, assert_read_only_sql


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM vendas",
        "  select id_vendas from vendas  ",
        "WITH totais AS (SELECT 1) SELECT * FROM totais",
    ],
)
def test_assert_read_only_sql_accepts_select_and_with(sql):
    assert_read_only_sql(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO vendas (valor_pago) VALUES (1)",
        "UPDATE vendas SET valor_pago = 0",
        "DELETE FROM vendas",
        "DROP TABLE vendas",
        "ALTER TABLE vendas ADD COLUMN x INT",
        "TRUNCATE TABLE vendas",
        "CREATE TABLE x (id INT)",
        "GRANT ALL ON vendas TO public",
        "REVOKE ALL ON vendas FROM public",
        "MERGE INTO vendas USING x ON true WHEN MATCHED THEN DELETE",
    ],
)
def test_assert_read_only_sql_rejects_write_statements(sql):
    with pytest.raises(ValueError):
        assert_read_only_sql(sql)


def test_assert_read_only_sql_rejects_non_select_start():
    with pytest.raises(ValueError):
        assert_read_only_sql("vendas; SELECT 1")


def test_assert_read_only_sql_ignores_write_keyword_substrings():
    assert_read_only_sql("SELECT data_atualizacao, data_inclusao FROM estados")


def test_run_query_error_message_hides_credentials(monkeypatch):
    secret = "novadrive376A@"

    class _FakeEngine:
        def connect(self):
            raise OperationalError(f"connection failed password={secret}", None, None)

    monkeypatch.setattr(database, "get_engine", lambda: _FakeEngine())

    with pytest.raises(DatabaseConnectionError) as exc_info:
        database.run_query("SELECT 1")

    assert secret not in str(exc_info.value)
    assert exc_info.value.__cause__ is None
