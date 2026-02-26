"""
tesis_alcaldesas.config — Configuración centralizada del proyecto.

Provee:
  - Rutas canónicas (BASE_DIR, DATA_DIR, OUTPUT_DIR, …)
  - get_engine()  → SQLAlchemy Engine desde variables de entorno PG*
  - Listas de outcomes, leakage y constantes reutilizables
"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# ============================================================
# 1. Rutas
# ============================================================
# BASE_DIR = raíz del repositorio (…/Code/)
BASE_DIR: Path = Path(__file__).resolve().parents[2]

DATA_DIR: Path = BASE_DIR / "data" / "processed"
OUTPUT_DIR: Path = BASE_DIR / "outputs"
OUTPUT_PAPER: Path = OUTPUT_DIR / "paper"
OUTPUT_QC: Path = OUTPUT_DIR / "qc"
SQL_DIR: Path = BASE_DIR / "sql"
DOCS_DIR: Path = BASE_DIR / "docs"

# Archivos clave
PARQUET_RAW: Path = DATA_DIR / "analytical_panel.parquet"
PARQUET_FEATURES: Path = DATA_DIR / "analytical_panel_features.parquet"


# ============================================================
# 2. Conexión a PostgreSQL
# ============================================================
def get_engine() -> Engine:
    """
    Construye un SQLAlchemy Engine a partir de variables de entorno PG*.

    Variables esperadas (con defaults para desarrollo local):
      PGHOST     (default: localhost)
      PGPORT     (default: 5432)
      PGDATABASE (default: tesis_db)
      PGUSER     (default: $USER)
      PGPASSWORD (default: vacío)

    Alternativamente, si DATABASE_URL está definida, se usa directamente.
    """
    url = os.environ.get("DATABASE_URL")
    if url:
        return create_engine(url)

    host = os.environ.get("PGHOST", "localhost")
    port = os.environ.get("PGPORT", "5432")
    database = os.environ.get("PGDATABASE", "tesis_db")
    user = os.environ.get("PGUSER", os.environ.get("USER", "postgres"))
    password = os.environ.get("PGPASSWORD", "")

    if password:
        url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    else:
        url = f"postgresql://{user}@{host}:{port}/{database}"

    return create_engine(url)


# ============================================================
# 3. Outcomes y variables
# ============================================================

# --- 17 outcomes crudos (mujeres) ---
RAW_OUTCOMES_M: list[str] = [
    # Extensión
    "ncont_total_m", "ncont_ahorro_m", "ncont_plazo_m",
    "ncont_n1_m", "ncont_n2_m", "ncont_n3_m", "ncont_tradic_m",
    # Profundidad (saldos)
    "saldocont_total_m", "saldocont_ahorro_m", "saldocont_plazo_m",
    "saldocont_n1_m", "saldocont_n2_m", "saldocont_n3_m", "saldocont_tradic_m",
    # Productos
    "numtar_deb_m", "numtar_cred_m", "numcontcred_hip_m",
]

# --- 17 outcomes crudos (hombres) — para placebos de género ---
RAW_OUTCOMES_H: list[str] = [col.replace("_m", "_h") for col in RAW_OUTCOMES_M]

# --- 5 outcomes primarios (mujeres) ---
PRIMARY_OUTCOMES: list[str] = [
    "ncont_total_m",
    "numtar_deb_m",
    "numtar_cred_m",
    "numcontcred_hip_m",
    "saldocont_total_m",
]

# --- Etiquetas ---
OUTCOME_LABELS: dict[str, dict[str, str]] = {
    "ncont_total_m":      {"es": "Contratos totales",       "en": "Total contracts"},
    "numtar_deb_m":       {"es": "Tarjetas débito",         "en": "Debit cards"},
    "numtar_cred_m":      {"es": "Tarjetas crédito",        "en": "Credit cards"},
    "numcontcred_hip_m":  {"es": "Créditos hipotecarios",   "en": "Mortgage loans"},
    "saldocont_total_m":  {"es": "Saldo total",             "en": "Total balance"},
}

# --- Columnas de leakage (nunca usar como controles) ---
LEAKAGE_COLS: list[str] = [
    "ever_alcaldesa",
    "alcaldesa_acumulado",
    "alcaldesa_final_f1", "alcaldesa_final_f2", "alcaldesa_final_f3",
    "alcaldesa_final_l1", "alcaldesa_final_l2", "alcaldesa_final_l3",
    "alcaldesa_excl_trans", "alcaldesa_end_excl_trans",
]
