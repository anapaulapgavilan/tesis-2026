# Tesis: Inclusión Financiera y Alcaldesas — Base de Datos

## Descripción

Panel municipal-trimestral que combina datos de **inclusión financiera** (CNBV) con el **género de la autoridad municipal** (alcaldesa), para evaluar el efecto causal del liderazgo femenino sobre la inclusión financiera a nivel local.

## Base de datos

| Parámetro | Valor |
|---|---|
| **Motor** | PostgreSQL 17.8 (Homebrew) |
| **Base de datos** | `tesis_db` |
| **Tabla** | `inclusion_financiera` |
| **Registros** | 41,905 |
| **Columnas** | 175 |
| **Llave primaria** | `(cve_mun, periodo_trimestre)` |

### Conexión

| Campo | Valor |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `tesis_db` |
| Username | `anapaulaperezgavilan` |
| Password | *(vacío)* |

**Desde Python:**
```python
from sqlalchemy import create_engine
engine = create_engine("postgresql://anapaulaperezgavilan@localhost:5432/tesis_db")
```

---

## Cobertura del panel

| Dimensión | Detalle |
|---|---|
| **Municipios** | 2,471 (clave: `cve_mun`) |
| **Estados** | 32 |
| **Periodo** | 2018Q3 – 2022Q3 (17 trimestres) |
| **Balance** | 100% — todos los municipios tienen 17 trimestres |
| **Regiones** | Occidente y Bajio, Noroeste, Sur, Noreste, Ciudad de Mexico, Centro Sur y Oriente |

---

## Diccionario de variables (175 columnas)

### Bloque 1: Identificadores (9 cols)

| Columna | Tipo | Descripción |
|---|---|---|
| `cve_mun` | INTEGER | **PK.** Clave del municipio (INEGI) |
| `trim` | INTEGER | Trimestre codificado (ej. 318 = Q3 2018) |
| `cve_edo` | INTEGER | Clave del estado (1–32) |
| `cve_ent` | TEXT | Clave de entidad zero-padded AGEE (ej. "01") |
| `cve_mun3` | TEXT | Clave municipal zero-padded AGEM (ej. "001") |
| `cvegeo_mun` | TEXT | Clave geoestadística canónica INEGI (ej. "01001") |
| `region` | TEXT | Región geográfica |
| `estado` | TEXT | Nombre del estado |
| `municipio` | TEXT | Nombre del municipio |

### Bloque 2: Demográficas (5 cols)

| Columna | Tipo | Descripción |
|---|---|---|
| `pob` | INTEGER | Población total del municipio |
| `pob_adulta` | INTEGER | Población adulta |
| `pob_adulta_m` | INTEGER | Población adulta mujeres |
| `pob_adulta_h` | INTEGER | Población adulta hombres |
| `tipo_pob` | TEXT | Categoría: Rural, Semi-urbano, En Transicion, Urbano, Semi-metropoli, Metropoli |

### Bloque 3: Inclusión financiera – CNBV (95 cols)

Desagregación por sexo: `_m` = mujeres, `_h` = hombres, `_pm` = persona moral, `_t` = total.

#### Número de contratos (`ncont_*`) — 28 cols, tipo INTEGER

| Prefijo | Producto |
|---|---|
| `ncont_ahorro_` | Cuentas de ahorro |
| `ncont_plazo_` | Depósitos a plazo |
| `ncont_n1_` | Cuentas nivel 1 |
| `ncont_n2_` | Cuentas nivel 2 |
| `ncont_n3_` | Cuentas nivel 3 |
| `ncont_tradic_` | Cuentas tradicionales |
| `ncont_total_` | Total de contratos |

#### Saldo de contratos (`saldocont_*`) — 28 cols, tipo INTEGER/BIGINT

| Prefijo | Producto | Nota |
|---|---|---|
| `saldocont_ahorro_` | Saldo en ahorro | INTEGER |
| `saldocont_plazo_` | Saldo a plazo | **BIGINT** (valores > 2 mil millones) |
| `saldocont_n1_` | Saldo nivel 1 | INTEGER |
| `saldocont_n2_` | Saldo nivel 2 | BIGINT parcial |
| `saldocont_n3_` | Saldo nivel 3 | INTEGER |
| `saldocont_tradic_` | Saldo tradicional | **BIGINT** |
| `saldocont_total_` | Saldo total | **BIGINT** |

#### Saldo promedio (`saldoprom_*`) — 28 cols, tipo FLOAT (NULLable)

Saldo promedio por contrato. Mismos sufijos que arriba.

> **Nota:** Los valores originales con `"-"` (sin dato) fueron convertidos a `NULL`. Estos NULLs son **indefiniciones estructurales** (0 contratos → saldo promedio = ÷0), no datos faltantes. Las columnas `flag_undef_saldoprom_*` marcan cuáles son (ver Bloque 6). Tasas de NULL van del 1.4% (`total_t`) al 99.9% (`n1_pm`).

#### Créditos y tarjetas (11 cols, tipo INTEGER)

| Columna(s) | Descripción |
|---|---|
| `numcontcred_hip_m/h/t` | Número de créditos hipotecarios |
| `numtar_deb_m/h/pm/t` | Número de tarjetas de débito |
| `numtar_cred_m/h/pm/t` | Número de tarjetas de crédito |

### Bloque 4: Auxiliares temporales (5 cols)

| Columna | Tipo | Descripción |
|---|---|---|
| `cve_mun_int` | INTEGER | Clave municipal (solo parte municipal) |
| `cve_edo_int` | INTEGER | Clave estatal (solo parte estatal) |
| `year` | INTEGER | Año (2018–2022) |
| `quarter` | INTEGER | Trimestre del año (1–4) |
| `periodo_trimestre` | TEXT | **PK.** Periodo en formato "2019Q1" |

### Bloque 5: Indicador Alcaldesa (33 cols)

#### Construcción del indicador

| Columna | Tipo | Descripción |
|---|---|---|
| `days_total` | INTEGER | Días totales del trimestre (90–92) |
| `days_female` | INTEGER | Días con mujer como autoridad |
| `days_male` | INTEGER | Días con hombre como autoridad |
| `days_missing` | INTEGER | Días sin cobertura en el histórico |

#### Indicadores principales

| Columna | Tipo | Descripción | NULLs |
|---|---|---|---|
| `alcaldesa` | INTEGER | 1 si days_female > days_male (mayoría de días) | 4.7% |
| `alcaldesa_end` | INTEGER | 1 si mujer al cierre del trimestre | 4.3% |
| `alcaldesa_final` | INTEGER | **Variable recomendada.** Versión final con llenado manual | **0%** |

#### Marcadores de transición

| Columna | Tipo | Descripción |
|---|---|---|
| `alcaldesa_transition` | INTEGER | 1 si hubo cambio de autoridad en el trimestre |
| `alcaldesa_transition_gender` | INTEGER | 1 si además hubo cambio de género |

#### Variantes excluyendo transiciones

| Columna | Tipo | Descripción |
|---|---|---|
| `alcaldesa_excl_trans` | INTEGER | alcaldesa = NULL en trimestres de transición |
| `alcaldesa_end_excl_trans` | INTEGER | alcaldesa_end = NULL en trimestres de transición |

#### Rezagos (lags) y adelantos (forwards)

| Columna | Tipo | Descripción |
|---|---|---|
| `alcaldesa_l1`, `alcaldesa_l2` | INTEGER | Rezagos de `alcaldesa` (t-1, t-2) |
| `alcaldesa_end_l1`, `alcaldesa_end_l2` | INTEGER | Rezagos de `alcaldesa_end` |
| `alcaldesa_excl_trans_l1/l2` | INTEGER | Rezagos excluyendo transiciones |
| `alcaldesa_end_excl_trans_l1/l2` | INTEGER | Rezagos de end excluyendo transiciones |
| `alcaldesa_final_l1/l2/l3` | INTEGER | Rezagos de `alcaldesa_final` (t-1, t-2, t-3) |
| `alcaldesa_final_f1/f2/f3` | INTEGER | Adelantos de `alcaldesa_final` (t+1, t+2, t+3) |

#### Calidad del panel

| Columna | Tipo | Descripción |
|---|---|---|
| `hist_mun_available` | INTEGER | 1 si el municipio tiene histórico de autoridades |
| `hist_state_available` | INTEGER | 1 si el estado tiene histórico |
| `quarters_in_base` | INTEGER | Trimestres del municipio en la base (siempre 17) |
| `missing_quarters_alcaldesa` | INTEGER | Trimestres sin dato de alcaldesa |
| `ok_panel_completo` | INTEGER | 1 si el panel original estaba completo |
| `ok_panel_completo_final` | INTEGER | 1 si el panel final está completo (siempre 1) |
| `filled_by_manual` | INTEGER | 1 si `alcaldesa_final` fue llenado manualmente |
| `t_index` | INTEGER | Índice temporal (0–16) |

### Bloque 6: Flags de missingness estructural (28 cols)

Patrón: `flag_undef_saldoprom_{producto}_{sexo}` — tipo INTEGER (0/1).

Marcan con `1` los registros donde el saldo promedio es NULL por indefinición estructural (0 contratos → ÷0). Productos: ahorro, plazo, n1, n2, n3, tradic, total. Sufijos: m, h, pm, t.

| Producto | % undefined (sufijo `_t`) |
|---|---|
| `ahorro` | 92.7% |
| `n1` | 90.6% |
| `n3` | 82.0% |
| `plazo` | 56.9% |
| `tradic` | 56.1% |
| `n2` | 1.5% |
| `total` | 1.4% |

> **Uso:** Para regresiones sobre `saldoprom_*`, filtrar `flag_undef_saldoprom_* = 0`.

---

### Resumen de tipos actuales

| Tipo | Columnas | Ejemplos |
|---|---|---|
| INTEGER | 149 | Conteos, indicadores, población, flags |
| BIGINT | 15 | Saldos monetarios (`saldocont_plazo_*`, `saldocont_tradic_*`, `saldocont_total_*`) |
| TEXT | 8 | `region`, `estado`, `municipio`, `tipo_pob`, `periodo_trimestre`, `cve_ent`, `cve_mun3`, `cvegeo_mun` |
| FLOAT | 3 | `saldoprom_*` (NULLable por indefinición estructural) |
| **Total** | **175** | |

> **Nota:** En pandas, las columnas INTEGER con NULLs se leen como `float64`. Las 28 `saldoprom_*` se leen como `float64` por sus NULLs. Las columnas INTEGER sin NULLs se leen como `int64`.

---

## Cambios realizados

### 20/02/2026 — Carga inicial
- Origen: `Base_20_02_2026.xlsx` (32.9 MB, 1 hoja)
- Se leyó el Excel con pandas y se cargó a PostgreSQL vía SQLAlchemy
- Columnas `saldoprom_*` con `"-"` se convirtieron a `NULL` numérico

### 22/02/2026 — Tipificación de columnas
- **`double precision` → `INTEGER`** en 62 columnas (población, indicadores binarios, saldos promedio, etc.)
- **`double precision` → `BIGINT`** en 15 columnas de saldos monetarios que exceden 2,147,483,647
- **`bigint` → `INTEGER`** en 62 columnas donde el máximo cabía en 32 bits
- **`boolean` → `INTEGER`** en 1 columna (`ok_panel_completo_final`)
- Resultado post-tipificación: `INTEGER` (124 cols), `BIGINT` (15 cols) y `TEXT` (5 cols)
- Resultado actual (post claves INEGI + flags): `INTEGER` (149 cols), `BIGINT` (15 cols), `TEXT` (8 cols), `FLOAT` (3 cols) = **175 cols**

### 22/02/2026 — Llave primaria
- Se verificó unicidad: 41,905 filas = 41,905 combinaciones únicas de `(cve_mun, periodo_trimestre)`
- Se creó la constraint `pk_inclusion_financiera PRIMARY KEY (cve_mun, periodo_trimestre)`
- Esto impide duplicados por construcción y crea un índice B-tree automático

### 22/02/2026 — Claves geográficas canónicas INEGI
- Se crearon 3 columnas nuevas para facilitar merges con otras bases de datos:
  - `cve_ent` (TEXT, 2 chars): clave de entidad zero-padded (AGEE), ej. `"01"`
  - `cve_mun3` (TEXT, 3 chars): clave municipal zero-padded (AGEM), ej. `"001"`
  - `cvegeo_mun` (TEXT, 5 chars): clave geográfica canónica = `cve_ent || cve_mun3`, ej. `"01001"`
- Las 3 columnas tienen constraint `NOT NULL`
- 2,471 municipios únicos verificados con formato estándar INEGI de 5 dígitos

### 22/02/2026 — Flags de missingness estructural (`saldoprom_*`)
- **Problema:** Las columnas `saldoprom_*` contenían `"-"` en el Excel original cuando `ncont_* = 0` (denominador cero → saldo promedio indefinido). Al migrar a PostgreSQL estos se convirtieron a `NULL`, pero conceptualmente no son datos faltantes sino **indefiniciones estructurales** (÷0).
- **Verificación:** Se confirmó que el 100% de los NULLs en `saldoprom_*` corresponden exactamente a `ncont_* = 0`. No hay NULLs por dato faltante real.
- **Solución:** Se crearon 28 columnas `flag_undef_saldoprom_{producto}_{sexo}` (INTEGER):
  - `1` = NULL estructural (0 contratos → saldo promedio indefinido)
  - `0` = valor legítimo (hay contratos, saldo promedio bien definido)
- **Tasas de undefined por producto (total):**

  | Producto | % undefined |
  |---|---|
  | `ahorro_t` | 92.7% |
  | `n1_t` | 90.6% |
  | `n3_t` | 82.0% |
  | `plazo_t` | 56.9% |
  | `tradic_t` | 56.1% |
  | `n2_t` | 1.5% |
  | `total_t` | 1.4% |

- **Implicación para análisis:**
  - **Margen extensivo** (¿hay contratos?): usar `ncont_* > 0`
  - **Margen intensivo** (¿cuánto ahorran?): usar `saldoprom_*` filtrando `flag_undef_saldoprom_* = 0`
  - Regresiones sobre `saldoprom_*` deben excluir observaciones con `flag = 1` para no confundir "no existe" con "dato faltante"

### 23/02/2026 — Auditoría del diccionario
- Se cruzó diccionario Excel (148 vars) vs base real PostgreSQL (175 cols)
- **31 columnas faltantes** en el diccionario → agregadas (3 identificadores INEGI + 28 flags)
- **4 variables fantasma** en el diccionario → eliminadas (`alcaldesa_manual`, `fuente_manual`, `pm_nombre_manual`, `reason_detailed`)
- **61 tipos corregidos** en el diccionario (reflejaban estado pre-tipificación)
- **28 conteos de NULLs corregidos** en columnas `saldoprom_*`
- Conteo de columnas actualizado: 144/148 → **175**
- Se creó `01_BRIEF.md`, `requirements.txt` y módulo `src/`

---

## Archivos en el repositorio

| Archivo | Descripción |
|---|---|
| `Base_20_02_2026.xlsx` | Archivo fuente original (Excel, 32.9 MB) |
| `Base_de_Datos_de_Inclusion_Financiera_201812.xlsm` | Referencia CNBV original |
| `Diccionario_y_QC_Base_CNBV_alcaldesa_v2.xlsx` | Diccionario de variables y control de calidad |
| `tesis_analisis.ipynb` | Notebook Jupyter con conexión, carga y consultas |
| `01_BRIEF.md` | Brief analítico del proyecto |
| `requirements.txt` | Dependencias Python versionadas |
| `src/` | Módulo con funciones reutilizables (`db.py`, `catalog.py`, `plot_style.py`) |
| `00_README.md` | Este archivo |

---

## Requisitos

- PostgreSQL 17+ (`brew install postgresql@17`)
- Python 3.12+ con: `pandas`, `sqlalchemy`, `psycopg2-binary`, `openpyxl`
- Para iniciar PostgreSQL: `brew services start postgresql@17`
