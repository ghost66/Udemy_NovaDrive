import os
import re
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import URL, Engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

_WRITE_KEYWORDS = (
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "TRUNCATE", "CREATE", "GRANT", "REVOKE", "MERGE",
)

# st.secrets, ao ser acessado, escreve um aviso na própria página quando não
# existe secrets.toml (mesmo dentro de try/except) — por isso só o tocamos
# se um dos arquivos realmente existir.
_SECRETS_PATHS = (
    Path.home() / ".streamlit" / "secrets.toml",
    Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml",
)


class DatabaseConnectionError(Exception):
    pass


def _get_setting(key: str) -> Optional[str]:
    if any(path.exists() for path in _SECRETS_PATHS):
        try:
            if key in st.secrets:
                return str(st.secrets[key])
        except Exception:
            pass
    value = os.environ.get(key)
    return value.strip() if value else value


def assert_read_only_sql(sql: str) -> None:
    normalized = sql.strip().upper()
    if not (normalized.startswith("SELECT") or normalized.startswith("WITH")):
        raise ValueError("Somente instruções SELECT/WITH são permitidas.")
    for keyword in _WRITE_KEYWORDS:
        # \b evita falso positivo em colunas como "data_atualizacao" ou "created_at"
        if re.search(rf"\b{keyword}\b", normalized):
            raise ValueError(f"Instrução SQL contém palavra-chave de escrita proibida: {keyword}")


@st.cache_resource
def get_engine() -> Engine:
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=_get_setting("DB_USER"),
        password=_get_setting("DB_PASSWORD"),
        host=_get_setting("DB_HOSTS"),
        port=int(_get_setting("DB_PORT")),
        database=_get_setting("DB_NAME"),
    )
    engine = create_engine(url)

    @event.listens_for(engine, "connect")
    def _enforce_read_only(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        cursor.close()

    return engine


def run_query(sql: str, params: Optional[dict] = None) -> pd.DataFrame:
    assert_read_only_sql(sql)
    try:
        engine = get_engine()
        with engine.connect() as connection:
            return pd.read_sql(text(sql), connection, params=params or {})
    except SQLAlchemyError:
        raise DatabaseConnectionError(
            "Não foi possível conectar ao banco de dados. Tente novamente mais tarde."
        ) from None
