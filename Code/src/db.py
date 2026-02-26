"""
src/db.py — Conexión y carga de datos desde PostgreSQL.
"""

import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql://anapaulaperezgavilan@localhost:5432/tesis_db"
TABLE = "inclusion_financiera"


def get_engine():
    """Devuelve un engine de SQLAlchemy conectado a tesis_db."""
    return create_engine(DB_URL)


def load_table(engine=None, table: str = TABLE) -> pd.DataFrame:
    """Carga la tabla completa a un DataFrame."""
    if engine is None:
        engine = get_engine()
    return pd.read_sql(f"SELECT * FROM {table}", engine)


def query(sql: str, engine=None) -> pd.DataFrame:
    """Ejecuta una consulta SQL y devuelve un DataFrame."""
    if engine is None:
        engine = get_engine()
    return pd.read_sql(sql, engine)


def check_connection(engine=None) -> dict:
    """Verifica la conexión y devuelve conteo de filas y columnas."""
    if engine is None:
        engine = get_engine()
    with engine.connect() as conn:
        n_rows = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE}")).scalar()
        n_cols = conn.execute(text(
            f"SELECT COUNT(*) FROM information_schema.columns "
            f"WHERE table_name = '{TABLE}'"
        )).scalar()
    return {"table": TABLE, "rows": n_rows, "cols": n_cols}
