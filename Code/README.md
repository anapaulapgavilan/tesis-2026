# Alcaldesas e Inclusión Financiera de las Mujeres en México

> **Pregunta de investigación:** ¿Cuál es el efecto de la representación política
> a nivel municipal (alcaldesas) en la inclusión financiera de las mujeres en México?

**Autora:** Ana Paula Pérez Gavilán  
**Tipo:** Tesis de grado

---

## Descripción general

Este repositorio contiene el código, la documentación metodológica y los outputs
del análisis empírico de la tesis. La investigación estima el efecto causal de
que una mujer ocupe la presidencia municipal (alcaldesa) sobre indicadores de
inclusión financiera femenina, utilizando datos administrativos de la Comisión
Nacional Bancaria y de Valores (CNBV) e información del género de la autoridad
municipal.

**Estrategia empírica:**

- Panel municipal-trimestral: 2,471 municipios × 17 trimestres (2018-T3 a 2022-T3).
- Diseño de **diferencias-en-diferencias (DiD)** con efectos fijos de municipio
  y trimestre (TWFE), errores estándar agrupados a nivel municipal.
- **Event study** (4 leads, 8 lags) para diagnosticar tendencias paralelas.
- **Robustez:** transformación funcional alternativa (log1p), winsorización,
  exclusión de transiciones, placebo temporal (+4 trimestres) y placebo de género
  (outcomes masculinos).
- **Heterogeneidad** por tipo de localidad (CONAPO) y tercil de población,
  con corrección Benjamini-Hochberg por múltiples pruebas.

Los cinco outcomes primarios (contratos totales, tarjetas de débito, tarjetas
de crédito, créditos hipotecarios y saldo total de mujeres) se miden en tasas
per cápita por cada 10,000 mujeres adultas, en escala asinh (seno hiperbólico
inverso).

---

## Estructura del repositorio

```
├── src/
│   ├── tesis_alcaldesas/              # ← Paquete principal (activo)
│   │   ├── __init__.py
│   │   ├── config.py                  #   Rutas, get_engine(), constantes
│   │   ├── data/
│   │   │   ├── extract_panel.py       #   PostgreSQL → parquet (61 cols)
│   │   │   └── build_features.py      #   Per cápita, asinh, winsor → 170 cols
│   │   └── models/
│   │       ├── utils.py               #   load_panel, run_panel_ols, formateo
│   │       ├── table1_descriptives.py #   Tabla 1: descriptivos pre-tratamiento
│   │       ├── twfe.py                #   Tabla 2: TWFE baseline
│   │       ├── event_study.py         #   Figura 1 + pre-trends tests
│   │       ├── robustness.py          #   Tabla 3: robustez
│   │       └── heterogeneity.py       #   Tabla 4: heterogeneidad + BH
│   │
│   ├── eda/                           # Pipeline EDA automatizado
│   │   └── run_eda.py
│   ├── transformaciones_criticas.py   # Recs 1-4 EDA (per cápita, asinh…)
│   ├── transformaciones_altas.py      # Recs 5-9 EDA (log pob, flags…)
│   ├── transformaciones_medias.py     # Recs 10-12 EDA (acumulados, panel…)
│   ├── tests/                         # 43 tests de validación del EDA
│   ├── db.py                          # Conexión legacy a PostgreSQL
│   ├── catalog.py                     # Catálogo programático de variables
│   ├── plot_style.py                  # Estilo de gráficos
│   ├── adhoc/                         # Scripts exploratorios (one-off)
│   ├── data/   [LEGACY]              # Originales — ver tesis_alcaldesas/data/
│   └── models/ [LEGACY]              # Originales — ver tesis_alcaldesas/models/
│
├── sql/
│   └── 00_schema_discovery.sql        # 12 queries QC (read-only)
│
├── data/
│   └── processed/                     # Parquets analíticos (en .gitignore)
│       ├── analytical_panel.parquet
│       └── analytical_panel_features.parquet
│
├── docs/                              # Documentación secuencial
│   ├── 00_README.md                   #   Diccionario de la base de datos
│   ├── 01_BRIEF.md                    #   Brief del proyecto
│   ├── 02–05_EDA_EXPLICACION*.md      #   Notas del EDA
│   ├── 06_MODELADO_PROPUESTA.md       #   Propuesta de modelado
│   ├── 07_DATA_CONTRACT.md            #   Contrato de datos (348 columnas)
│   ├── 08_DATASET_CONSTRUCCION.md     #   Construcción del dataset analítico
│   ├── 09_MODELADO_ECONOMETRICO.md    #   Ecuaciones, supuestos, decisiones
│   └── 10_RESULTADOS_EMPIRICOS.md     #   Sección de resultados (texto tesis)
│
├── notebooks/
│   ├── tesis_analisis.ipynb           # Notebook exploratorio principal
│   └── eda.ipynb                      # EDA interactivo
│
├── outputs/
│   ├── eda/                           # Figuras y tablas del EDA (13 archivos)
│   ├── paper/                         # Tablas (.csv/.tex), figuras, coeficientes
│   │   ├── tabla_1_descriptiva.*
│   │   ├── tabla_2_twfe.*
│   │   ├── tabla_3_robustez.*
│   │   ├── tabla_4_heterogeneidad.*
│   │   ├── figura_1_event_study.pdf/.png
│   │   ├── pretrends_tests.csv
│   │   └── event_study_coefs_*.csv
│   └── qc/                            # Perfiles y chequeos de calidad
│
├── requirements.txt                   # Dependencias Python
├── pyproject.toml                     # Empaquetado (pip install -e .)
├── .gitignore
└── README.md                          # ← Este archivo
```

---

## Requisitos y entorno

### Python

- **Versión mínima:** Python 3.10+
- **Paquetes clave:**

| Paquete | Uso |
|---|---|
| `pandas`, `numpy` | Manipulación de datos |
| `pyarrow` | Lectura/escritura parquet |
| `sqlalchemy`, `psycopg2-binary` | Conexión PostgreSQL |
| `linearmodels` | PanelOLS (TWFE, event study) |
| `statsmodels` | Diagnósticos, corrección BH |
| `scipy` | Tests chi-cuadrado |
| `matplotlib`, `seaborn` | Figuras |
| `jinja2` | Exportación LaTeX |

### Base de datos

- **PostgreSQL 17+** con la base `tesis_db` poblada (tabla `inclusion_financiera_clean`,
  41,905 filas × 348 columnas).

### Variables de entorno

Las credenciales de conexión se leen desde variables de entorno estándar de PostgreSQL.
Copia `.env.example` → `.env` y ajusta según tu configuración:

```bash
# .env.example
PGHOST=localhost
PGPORT=5432
PGDATABASE=tesis_db
PGUSER=tu_usuario
PGPASSWORD=
```

> También se acepta la variable `DATABASE_URL` como alternativa:
> `DATABASE_URL=postgresql://usuario:password@host:puerto/tesis_db`

---

## Orden de ejecución desde cero (pipeline)

### Paso 0 — Preparar entorno

```bash
git clone https://github.com/<tu-usuario>/tesis-2026.git
cd tesis-2026

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .                   # instala tesis_alcaldesas como paquete
```

Configurar las variables de entorno para PostgreSQL (ver sección anterior).

### Paso 1 — Perfil de la base y data contract *(opcional)*

El resultado ya está documentado en `docs/07_DATA_CONTRACT.md` y los queries en
`sql/00_schema_discovery.sql`. Si se necesita regenerar:

```bash
psql -d tesis_db -f sql/00_schema_discovery.sql
```

### Paso 2 — Transformaciones EDA *(solo si la tabla limpia no existe)*

Si `inclusion_financiera_clean` no existe en la base, ejecutar las transformaciones
del EDA para crearla a partir de `inclusion_financiera`:

```bash
python src/transformaciones_criticas.py    # Recs 1-4: per cápita, asinh, etc.
python src/transformaciones_altas.py       # Recs 5-9: log pob, flags
python src/transformaciones_medias.py      # Recs 10-12: acumulados, panel
```

Validar con:
```bash
python -m pytest src/tests/ -v             # 43 tests
```

### Paso 3 — Construir dataset analítico

```bash
python -m tesis_alcaldesas.data.extract_panel     # → data/processed/analytical_panel.parquet
python -m tesis_alcaldesas.data.build_features    # → data/processed/analytical_panel_features.parquet
```

Esto genera el panel analítico final (41,905 × 170) y los diagnósticos en `outputs/qc/`.

### Paso 4 — Correr modelos econométricos

```bash
python -m tesis_alcaldesas.models.table1_descriptives   # Tabla 1: descriptivos
python -m tesis_alcaldesas.models.twfe                  # Tabla 2: TWFE baseline
python -m tesis_alcaldesas.models.event_study           # Figura 1 + pre-trends
python -m tesis_alcaldesas.models.robustness            # Tabla 3: robustez
python -m tesis_alcaldesas.models.heterogeneity         # Tabla 4: heterogeneidad
```

Los resultados (tablas `.csv` / `.tex` y figuras) se depositan en `outputs/paper/`.

### Paso 5 — Usar resultados para la tesis

Las tablas y figuras en `outputs/paper/` son las que se incluyen directamente en
el capítulo de resultados de la tesis. La lógica metodológica está documentada en:

- `docs/08_DATASET_CONSTRUCCION.md` — cómo se construyó el dataset analítico
- `docs/09_MODELADO_ECONOMETRICO.md` — ecuaciones, supuestos, decisiones
- `docs/10_RESULTADOS_EMPIRICOS.md` — texto de la sección de resultados

---

## Estado actual del proyecto

| Fase | Estado |
|---|---|
| EDA | ✅ Completado (12/12 recomendaciones, 43/43 tests) |
| Propuesta de modelado | ✅ docs/06_MODELADO_PROPUESTA.md |
| Contrato de datos | ✅ docs/07_DATA_CONTRACT.md (348 columnas) |
| Dataset analítico | ✅ 41,905 × 170 features |
| Modelos econométricos | ✅ TWFE, event study, robustez, heterogeneidad |
| Resultados empíricos | ✅ docs/10_RESULTADOS_EMPIRICOS.md |

### Resultado principal

> **No se detecta efecto estadísticamente significativo** de la presencia de una
> alcaldesa sobre la inclusión financiera de las mujeres a nivel municipal,
> en ninguno de los cinco indicadores analizados. Los intervalos de confianza
> descartan efectos superiores a ±5% en contratos per cápita (escala asinh).
> El resultado es robusto a transformaciones funcionales alternativas,
> exclusión de transiciones, placebos temporales y de género, y no se modifica
> al explorar heterogeneidad por grado de urbanización o tamaño poblacional.

---

## Licencia

Proyecto académico — uso personal.
