# Guía Completa para Principiantes — Tesis: Alcaldesas e Inclusión Financiera

> **¿Para quién es esta guía?**
> Para alguien que **no sabe programar** y **no tiene formación en economía**.
> Vamos paso a paso, sin saltarnos nada. Si algo no queda claro, vuelve a leerlo
> con calma — cada sección construye sobre la anterior.

---

## Índice

| Parte | Tema | ¿Qué aprenderás? |
|-------|------|-------------------|
| **0** | [Conceptos de Python que necesitas](#parte-0--conceptos-de-python-que-necesitas) | Variables, listas, funciones, archivos |
| **1** | [¿De qué trata esta investigación?](#parte-1--de-qué-trata-esta-investigación) | La pregunta, los datos, la estrategia |
| **2** | [¿Cómo se organizan los datos?](#parte-2--cómo-se-organizan-los-datos-pipeline-de-datos) | El pipeline de extracción y transformación |
| **3** | [¿Cómo funcionan los modelos?](#parte-3--cómo-funcionan-los-modelos-econométricos) | TWFE, event study, robustez, DiD moderno |
| **4** | [¿Cómo se leen los resultados?](#parte-4--cómo-leer-e-interpretar-los-resultados) | Tablas, figuras, p-valores |
| **5** | [¿Cómo corro el código yo mismo/a?](#parte-5--cómo-correr-el-código-tú-mismoa) | Instalación, ejecución, troubleshooting |
| **A** | [Glosario](#apéndice-a--glosario) | Términos técnicos explicados |

---

## Parte 0 — Conceptos de Python que necesitas

Antes de entrar al código de la tesis, necesitas entender algunos conceptos
básicos de Python. No necesitas ser experto/a; solo necesitas poder **leer**
el código y entender qué hace.

### 0.1 ¿Qué es Python?

Python es un **lenguaje de programación**. Es como darle instrucciones a la
computadora en un idioma que ella entiende. Por ejemplo:

```python
# Esto es un comentario — Python lo ignora.
# Los comentarios empiezan con #

nombre = "Ana Paula"       # Guardar texto en una "caja" llamada nombre
edad = 25                  # Guardar un número
print(nombre)              # Mostrar en pantalla: Ana Paula
```

### 0.2 Variables: las "cajas" donde guardamos datos

Una **variable** es un nombre que le damos a un dato para poder usarlo después.

```python
municipios = 2471          # Un número entero (integer)
porcentaje = 0.047         # Un número con decimales (float)
nombre = "Oaxaca"          # Texto (string) — siempre entre comillas
es_alcaldesa = True        # Verdadero/Falso (boolean)
```

En el código de la tesis, verás variables como:

```python
treatment = "alcaldesa_final"   # El nombre de la columna de tratamiento
controls = ["log_pob"]          # Una lista con un control
K_LEADS = 4                     # Número de periodos "antes" del evento
```

### 0.3 Listas y diccionarios

Una **lista** es una colección ordenada de elementos:

```python
# Lista de 5 outcomes (resultados que medimos)
PRIMARY_5 = [
    "ncont_total_m",       # Contratos totales de mujeres
    "numtar_deb_m",        # Tarjetas de débito de mujeres
    "numtar_cred_m",       # Tarjetas de crédito de mujeres
    "numcontcred_hip_m",   # Créditos hipotecarios de mujeres
    "saldocont_total_m",   # Saldo total de mujeres
]
```

Un **diccionario** asocia "claves" con "valores" (como un diccionario real):

```python
OUTCOME_LABELS = {
    "ncont_total_m": {"es": "Contratos totales", "en": "Total contracts"},
    "numtar_deb_m":  {"es": "Tarjetas débito",   "en": "Debit cards"},
}
# Para acceder: OUTCOME_LABELS["ncont_total_m"]["es"] → "Contratos totales"
```

### 0.4 Funciones: bloques de código reutilizables

Una **función** es un bloque de código con un nombre. La defines una vez y
la puedes usar muchas veces.

```python
def saludar(nombre):
    """Esta función saluda a alguien."""    # ← Docstring (documentación)
    print(f"¡Hola, {nombre}!")

saludar("Ana Paula")   # Imprime: ¡Hola, Ana Paula!
saludar("María")       # Imprime: ¡Hola, María!
```

En el código de la tesis verás funciones como:

```python
def load_panel():
    """Carga el parquet y setea el MultiIndex para PanelOLS."""
    df = pd.read_parquet(path)        # Leer archivo de datos
    df = df.set_index(["cve_mun", "t_index"])  # Definir índice
    return df                          # Devolver el resultado
```

Esto significa: "la función `load_panel` lee un archivo de datos y lo prepara
para análisis. Devuelve una tabla (`df`)."

### 0.5 Importaciones: usar código de otros

Python tiene "paquetes" (libraries) que otros programadores crearon. Los
importamos así:

```python
import pandas as pd          # Paquete para manipular tablas de datos
import numpy as np           # Paquete para cálculos matemáticos
import matplotlib.pyplot as plt  # Paquete para hacer gráficos
```

El `as pd` es un **alias** (apodo) para no escribir `pandas` completo cada vez.

Los paquetes más usados en la tesis:

| Paquete | Para qué sirve | Ejemplo |
|---------|----------------|---------|
| `pandas` | Tablas de datos (como Excel pero en Python) | `df = pd.read_parquet("datos.parquet")` |
| `numpy` | Cálculos matemáticos | `np.log(100)` → logaritmo de 100 |
| `linearmodels` | Regresiones econométricas | `PanelOLS(y, X)` |
| `matplotlib` | Gráficos | `plt.plot(x, y)` |
| `scipy` | Estadística | Tests chi-cuadrado |

### 0.6 DataFrames: la tabla de datos

La estructura más importante de la tesis es el **DataFrame** de pandas. Piensa
en él como una hoja de Excel:

```
            cve_mun  periodo_trimestre  alcaldesa_final  ncont_total_m
0              1001            2018Q3                0          15230
1              1001            2018Q4                0          15456
2              1001            2019Q1                1          15890
...
41904        32056            2022Q3                0           2105
```

- Cada **fila** es una observación (un municipio en un trimestre).
- Cada **columna** es una variable (dato que medimos).
- El DataFrame tiene **41,905 filas** y muchas columnas.

### 0.7 Archivos `.py` y módulos

Cada archivo `.py` es un **módulo** de Python. Cuando ves:

```python
from tesis_alcaldesas.models.utils import load_panel
```

Esto significa: "del paquete `tesis_alcaldesas`, subcarpeta `models`, archivo
`utils.py`, trae la función `load_panel`."

### 0.8 El bloque `if __name__ == "__main__"`

Al final de muchos archivos verás:

```python
if __name__ == "__main__":
    main()
```

Esto significa: "si ejecutas este archivo directamente (no lo estás importando
desde otro), ejecuta la función `main()`." Es el punto de entrada del programa.

---

## Parte 1 — ¿De qué trata esta investigación?

### 1.1 La pregunta de investigación

> **¿Tener una alcaldesa (mujer al frente del municipio) mejora la inclusión
> financiera de las mujeres en ese municipio?**

Es decir: cuando una mujer se convierte en presidenta municipal, ¿las mujeres
del municipio empiezan a tener más cuentas de banco, más tarjetas, más créditos?

### 1.2 ¿Por qué es importante?

- En México, las mujeres tienen **menos acceso a servicios financieros** que
  los hombres.
- Si tener una alcaldesa mejora esa situación, eso nos dice algo importante
  sobre el efecto de la **representación política femenina**.

### 1.3 ¿Qué datos usamos?

Tenemos una tabla gigante con información de **2,471 municipios** de México,
observados cada **trimestre** (cada 3 meses) durante **17 trimestres**
(de 2018-Q3 a 2022-Q3).

Para cada municipio en cada trimestre, sabemos:

| Tipo de dato | Ejemplos |
|-------------|----------|
| **¿Quién gobierna?** | `alcaldesa_final` = 1 si hay alcaldesa, 0 si no |
| **Inclusión financiera de mujeres** | Número de contratos, tarjetas de débito, tarjetas de crédito, créditos hipotecarios, saldo total |
| **Población** | Cuántas personas viven ahí, cuántas mujeres adultas |
| **Ubicación** | Estado, región, tipo de municipio (rural, urbano, etc.) |

### 1.4 ¿Qué medimos exactamente? (Los 5 outcomes)

Medimos 5 indicadores de inclusión financiera de las mujeres:

| # | Variable en el código | ¿Qué mide? |
|---|----------------------|-------------|
| 1 | `ncont_total_m` | **Contratos totales** de mujeres (cuentas de banco) |
| 2 | `numtar_deb_m` | **Tarjetas de débito** de mujeres |
| 3 | `numtar_cred_m` | **Tarjetas de crédito** de mujeres |
| 4 | `numcontcred_hip_m` | **Créditos hipotecarios** de mujeres |
| 5 | `saldocont_total_m` | **Saldo total** de mujeres (cuánto dinero tienen en el banco) |

El sufijo `_m` siempre significa "mujeres" y `_h` significa "hombres".

### 1.5 La estrategia: Diferencias en Diferencias (DiD)

El reto es: no podemos simplemente comparar municipios con alcaldesa vs sin
alcaldesa, porque podrían ser municipios **muy diferentes** desde el principio
(los más grandes, los más urbanos, etc.).

La estrategia se llama **Diferencias en Diferencias (DiD)**:

```
                    Antes de alcaldesa     Después de alcaldesa
Municipio tratado:        A₁                      A₂
Municipio control:        B₁                      B₂

Efecto estimado = (A₂ - A₁) - (B₂ - B₁)
```

Es decir: vemos cuánto **cambió** la inclusión financiera en municipios que
obtuvieron alcaldesa, y le **restamos** cuánto cambió en municipios que no la
obtuvieron. La diferencia de las diferencias es el **efecto de la alcaldesa**.

### 1.6 ¿Qué es un panel de datos?

Un **panel** es una tabla donde seguimos a las mismas unidades (municipios)
a lo largo del tiempo (trimestres). Es como tener una hoja de Excel donde:

- Cada municipio tiene **17 filas** (una por trimestre)
- Total: 2,471 municipios × 17 trimestres = **41,905 filas**

Esto nos permite ver cómo **cambian** las cosas dentro del mismo municipio
a lo largo del tiempo.

### 1.7 Conceptos clave que aparecen en el código

| Término | Significado |
|---------|-------------|
| **Tratamiento** | Que haya alcaldesa (`alcaldesa_final = 1`) |
| **Control** | Que NO haya alcaldesa (`alcaldesa_final = 0`) |
| **Per cápita** | Dividir entre la población (para comparar municipios grandes y pequeños) |
| **asinh** | Una transformación matemática que "comprime" los valores extremos (ver §2.5) |
| **Efectos fijos** | Controles automáticos para diferencias permanentes entre municipios y entre trimestres |
| **Cluster SE** | Errores estándar que tienen en cuenta que las observaciones del mismo municipio están correlacionadas |
| **p-valor** | Probabilidad de que el resultado sea por casualidad (ver §4.2) |
| **Never-treated** | Municipio que **nunca** tuvo alcaldesa en el periodo |
| **Switcher** | Municipio que **pasó** de hombre a mujer (o viceversa) |
| **Always-treated** | Municipio que **siempre** tuvo alcaldesa |

---

## Parte 2 — ¿Cómo se organizan los datos? (Pipeline de datos)

El código de la tesis sigue un **pipeline** (tubería): los datos entran crudos
y salen listos para el análisis. Hay dos pasos principales.

### 2.1 Paso 1: Extracción (`extract_panel.py`)

**Archivo:** `src/tesis_alcaldesas/data/extract_panel.py`

**¿Qué hace?** Saca los datos de la base de datos PostgreSQL y los guarda en
un archivo `.parquet` (un formato eficiente para datos tabulares).

**Analogía:** Es como ir a un almacén gigante (la base de datos con 175
columnas) y sacar solo lo que necesitas (unas 61 columnas) para tu análisis.

**Paso a paso:**

1. **Se conecta** a la base de datos PostgreSQL usando la función `get_engine()`:
   ```python
   engine = get_engine()
   # Esto lee variables de entorno como PGHOST, PGPORT, PGDATABASE...
   # y crea una conexión a la base de datos
   ```

2. **Define qué columnas necesita.** El archivo organiza las columnas en grupos:
   ```python
   ID_COLS = ["cve_mun", "periodo_trimestre", ...]      # Identificadores
   TREATMENT_COLS = ["alcaldesa_final", ...]             # Tratamiento
   CONTROL_COLS = ["log_pob", ...]                       # Controles
   RAW_OUTCOMES_M = ["ncont_total_m", "numtar_deb_m", ...]  # Lo que medimos
   ```

3. **Valida** que todas las columnas existan en la base de datos.

4. **Ejecuta una consulta SQL** para extraer los datos:
   ```python
   query = "SELECT col1, col2, ... FROM inclusion_financiera_clean
            ORDER BY cve_mun, periodo_trimestre"
   ```

5. **Guarda** el resultado como `data/processed/analytical_panel.parquet`.

**Resultado:** Un archivo con **41,905 filas × ~61 columnas** con los datos
crudos que necesitamos.

### 2.2 Paso 2: Construcción de features (`build_features.py`)

**Archivo:** `src/tesis_alcaldesas/data/build_features.py`

**¿Qué hace?** Toma los datos crudos y los transforma para que estén listos
para el análisis econométrico. Es como preparar los ingredientes antes de
cocinar.

**Las transformaciones paso a paso:**

#### 2.3 Per cápita: normalizar por población

**Problema:** Un municipio con 1 millón de habitantes va a tener más contratos
que uno con 10,000 habitantes simplemente porque tiene más gente. Eso no
significa que sea "mejor" en inclusión financiera.

**Solución:** Dividir entre la población y multiplicar por 10,000:

```python
# Fórmula: per_capita = 10,000 × (contratos / mujeres_adultas)
df["ncont_total_m_pc"] = 10_000 * df["ncont_total_m"] / df["pob_adulta_m"]
```

Esto nos da: "contratos por cada 10,000 mujeres adultas". Ahora sí podemos
comparar municipios de distintos tamaños.

**En el código:** La función `build_per_capita()` hace esto para los 17
outcomes.

#### 2.4 ¿Qué pasa si el denominador es cero?

Si un municipio tiene 0 mujeres adultas registradas, la división sería
`10000 × algo / 0`, que es indefinido. El código maneja esto:

```python
df["ncont_total_m_pc"] = np.where(
    df["pob_adulta_m"] > 0,                      # Si hay mujeres adultas...
    10_000 * df["ncont_total_m"] / df["pob_adulta_m"],  # ...calcular
    np.nan,                                       # Si no, poner "dato faltante"
)
```

`np.nan` significa "Not a Number" — es la forma de Python de decir "no tenemos
este dato".

#### 2.5 Transformación asinh: comprimir valores extremos

**Problema:** Algunos municipios tienen valores de inclusión financiera
**muy altos** (por ejemplo, la CDMX), mientras que otros tienen valores
cercanos a cero. Esa desigualdad tan grande dificulta el análisis.

**Solución:** Aplicar la transformación **asinh** (seno hiperbólico inverso):

```python
df["ncont_total_m_pc_asinh"] = np.arcsinh(df["ncont_total_m_pc"])
```

**¿Qué hace asinh?** "Comprime" los valores grandes sin destruir los valores
cercanos a cero:

| Valor original (pc) | Valor asinh | Efecto |
|---------------------|-------------|--------|
| 0 | 0.00 | Se queda igual |
| 1 | 0.88 | Casi igual |
| 10 | 2.99 | Se comprime un poco |
| 100 | 5.30 | Se comprime bastante |
| 10,000 | 9.90 | Se comprime mucho |

**¿Por qué asinh y no logaritmo?** El logaritmo de 0 es indefinido (−∞),
pero asinh(0) = 0. Como muchos municipios tienen 0 contratos, asinh es más
conveniente.

**Interpretación:** Un cambio de 0.05 en escala asinh es **aproximadamente**
un cambio de 5% en el valor original (para valores no muy pequeños).

#### 2.6 Otras transformaciones

| Transformación | Columna que genera | Para qué sirve |
|---------------|-------------------|----------------|
| **Winsorización** | `_pc_w` | Recorta los valores en los percentiles 1 y 99 para reducir efecto de extremos |
| **log(1+y)** | `_pc_log1p` | Alternativa a asinh, para prueba de robustez |
| **Ratios M/H** | `ratio_mh_*` | Brecha de género: outcome mujeres / outcome hombres |

#### 2.7 Cohortes y event time

Para el análisis, el código clasifica cada municipio:

```python
# ¿Este municipio alguna vez tuvo alcaldesa?
"cohort_type": "never-treated"    # Nunca tuvo alcaldesa
"cohort_type": "switcher"         # Cambió de hombre a mujer (o viceversa)
"cohort_type": "always-treated"   # Siempre tuvo alcaldesa

# ¿Cuándo fue la primera vez que tuvo alcaldesa?
"first_treat_t": 5               # En el trimestre 5 (2019-Q4)

# ¿En qué momento estamos respecto al tratamiento?
"event_time": -2                  # 2 trimestres ANTES de tener alcaldesa
"event_time": 0                   # El trimestre en que empezó la alcaldesa
"event_time": 3                   # 3 trimestres DESPUÉS
```

**Resultado final:** Un archivo con **41,905 filas × ~170 columnas** guardado
como `data/processed/analytical_panel_features.parquet`.

---

## Parte 3 — ¿Cómo funcionan los modelos econométricos?

Ahora entramos al corazón de la tesis. Cada modelo responde una pregunta
diferente. Los vamos a ver en el **mismo orden** en que se ejecutan.

### 3.1 Tabla 1: Estadísticos descriptivos (`table1_descriptives.py`)

**Pregunta:** ¿Cómo se ven los datos? ¿Los municipios tratados y no tratados
son similares antes del tratamiento?

**¿Qué hace?** Calcula promedios y desviaciones estándar para los tres grupos:

| Grupo | Descripción | N municipios |
|-------|-------------|-------------|
| Never-treated | Nunca tuvieron alcaldesa | ~1,476 |
| Switchers (pre) | Datos **antes** de que llegara la alcaldesa | ~877 |
| Always-treated | Siempre tuvieron alcaldesa | ~118 |

**¿Por qué importa?** Si los grupos son muy diferentes desde el principio,
el análisis DiD podría no ser confiable. Queremos que se **parezcan** antes
del tratamiento.

**En el código:**

```python
# Separar los grupos
mask_never = df["cohort_type"] == "never-treated"
mask_switch_pre = (df["cohort_type"] == "switcher") & (df["event_time"] < 0)

# Calcular promedios para cada grupo
vals = gdf[var].dropna()
mean = vals.mean()
sd = vals.std()
```

### 3.2 Tabla 2: TWFE Baseline (`twfe.py`)

**Pregunta:** ¿Tiene efecto la alcaldesa sobre la inclusión financiera?

**Este es el modelo principal.** TWFE significa "Two-Way Fixed Effects"
(efectos fijos bidireccionales).

**La ecuación (no te asustes, la vamos a descomponer):**

```
Y_{it} = α_i + γ_t + β · D_{it} + δ · log_pob_{it} + ε_{it}
```

Vamos pieza por pieza:

| Símbolo | Significado | En el código |
|---------|------------|--------------|
| `Y_{it}` | Inclusión financiera del municipio `i` en el trimestre `t` | `depvar = "ncont_total_m_pc_asinh"` |
| `α_i` | Efecto fijo de municipio — todo lo que es **permanente** del municipio (tamaño, ubicación, cultura) | `entity_effects=True` |
| `γ_t` | Efecto fijo de tiempo — todo lo que cambia igual para **todos** los municipios en un trimestre (inflación, COVID, política nacional) | `time_effects=True` |
| `β` | **EL NÚMERO QUE NOS INTERESA** — el efecto de tener alcaldesa | `res.params["alcaldesa_final"]` |
| `D_{it}` | ¿Hay alcaldesa en este municipio-trimestre? (1 = sí, 0 = no) | `"alcaldesa_final"` |
| `δ` | Efecto del tamaño poblacional | control: `"log_pob"` |
| `ε_{it}` | Error — todo lo que no podemos explicar | (residuo del modelo) |

**¿Cómo se ejecuta en el código?**

```python
# 1. Cargar datos
df = load_panel()

# 2. Definir la regresión
treatment = "alcaldesa_final"
controls = ["log_pob"]
exog = [treatment] + controls       # Variables explicativas

# 3. Para cada uno de los 5 outcomes:
for out_name in PRIMARY_5:
    depvar = f"{out_name}_pc_asinh"  # Variable dependiente (lo que medimos)

    # 4. Correr la regresión
    res = run_panel_ols(df, depvar=depvar, exog=exog)

    # 5. Extraer resultados
    beta = res.params[treatment]     # El coeficiente β
    se = res.std_errors[treatment]   # El error estándar
    pval = res.pvalues[treatment]    # El p-valor
```

**¿Qué hace `run_panel_ols`?** Esta función (definida en `utils.py`) es el
motor de la regresión:

```python
def run_panel_ols(df, depvar, exog, ...):
    y = sub[depvar]          # Variable que queremos explicar
    X = sub[exog]            # Variables que usamos para explicar

    mod = PanelOLS(          # Crear el modelo
        y, X,
        entity_effects=True,  # Absorber diferencias fijas entre municipios
        time_effects=True,    # Absorber diferencias fijas entre trimestres
    )

    res = mod.fit(cov_type="clustered", cluster_entity=True)
    # "clustered" = los errores estándar tienen en cuenta que las
    # observaciones del mismo municipio están correlacionadas.

    return res
```

**Resultado clave:** Si β es **positivo y estadísticamente significativo**,
significa que tener alcaldesa **aumenta** la inclusión financiera de las
mujeres. Si β es cercano a cero y no significativo, no hay efecto detectable.

### 3.3 Figura 1: Event Study (`event_study.py`)

**Pregunta:** ¿Había tendencias diferentes ANTES de que llegara la alcaldesa?
¿El efecto aparece de golpe o gradualmente?

**¿Por qué es importante?** Para que el DiD sea válido, necesitamos que los
municipios tratados y no tratados siguieran **tendencias paralelas** antes
del tratamiento. El event study lo verifica visualmente.

**La idea:**

En vez de estimar UN solo coeficiente β, estimamos un coeficiente δ_k para
**cada periodo relativo al tratamiento**:

```
k = -4: 4 trimestres ANTES de la alcaldesa → δ_{-4} debería ser ≈ 0
k = -3: 3 trimestres ANTES                 → δ_{-3} debería ser ≈ 0
k = -2: 2 trimestres ANTES                 → δ_{-2} debería ser ≈ 0
k = -1: 1 trimestre ANTES (REFERENCIA)     → δ_{-1} = 0 por definición
k =  0: El trimestre del inicio             → ¿δ_0 ≠ 0?
k =  1: 1 trimestre DESPUÉS                → ¿δ_1 ≠ 0?
...
k =  8: 8 trimestres DESPUÉS               → ¿δ_8 ≠ 0?
```

**Si los δ para k < 0 son ≈ 0:** ¡Las tendencias eran paralelas antes del
tratamiento! El supuesto clave del DiD se cumple.

**Si los δ para k ≥ 0 son ≠ 0:** Hay un efecto del tratamiento.

**En el código:**

```python
# 1. Construir "dummies" (variables binarias) para cada periodo relativo
df_es, dummy_cols = build_event_dummies(df)
# dummy_cols = ["evt_k_le-4", "evt_k-3", "evt_k-2", "evt_k+0", ..., "evt_k_ge8"]
# (k=-1 se omite como referencia)

# 2. Correr la regresión con todas las dummies
exog = dummy_cols + ["log_pob"]
mod = PanelOLS(y, X, entity_effects=True, time_effects=True)
res = mod.fit(cov_type="clustered", cluster_entity=True)

# 3. Extraer coeficientes para graficar
for col in dummy_cols:
    beta = res.params[col]   # Coeficiente δ_k
    se = res.std_errors[col]  # Error estándar
    ci_lo, ci_hi = res.conf_int().loc[col]  # Intervalo de confianza
```

**El test de pre-trends:** Además del gráfico, se hace un test estadístico
formal (chi-cuadrado) que prueba si **todos** los coeficientes pre-tratamiento
son conjuntamente iguales a cero:

```python
# Si el p-valor de este test es > 0.10, pasan las pre-trends
chi2_stat = pre_coefs @ np.linalg.solve(vcov, pre_coefs)
chi2_pval = 1 - stats.chi2.cdf(chi2_stat, df=n_restrictions)
```

### 3.4 Tabla 3: Pruebas de Robustez (`robustness.py`)

**Pregunta:** ¿El resultado cambia si hacemos las cosas un poco diferente?

Si el resultado es **robusto**, debería mantenerse aunque cambiemos detalles
del análisis. Se hacen 5 pruebas:

| Test | ¿Qué cambiamos? | ¿Qué esperamos? |
|------|-----------------|-----------------|
| **R1: log(1+y)** | En vez de asinh, usamos log(1+y) | Resultado similar |
| **R2: Winsorización** | Recortamos el 1% más extremo | Resultado similar |
| **R3: Excluir transiciones** | Quitamos los trimestres donde hubo cambio de gobierno | Resultado similar |
| **R4: Placebo temporal** | Fingimos que la alcaldesa llegó 4 trimestres antes | Resultado ≈ 0 (no hay efecto falso) |
| **R5: Placebo de género** | Medimos inclusión financiera de **hombres** | Resultado ≈ 0 (el efecto debería ser solo en mujeres) |

**En el código (ejemplo del placebo temporal):**

```python
# Crear un tratamiento "falso": adelantar 4 trimestres
df_r4_flat["placebo_tto_f4"] = (
    df_r4_flat.groupby("cve_mun")["alcaldesa_final"].shift(-4)
)
# shift(-4) = "mover hacia atrás 4 periodos"
# Es decir, si la alcaldesa llegó en t=5, el placebo dice que llegó en t=1

# Correr la misma regresión pero con el tratamiento falso
r4 = run_robustness_twfe(df_r4_flat, depvar, "placebo_tto_f4")
# Si β ≈ 0 → bien, no hay anticipación
```

### 3.5 Tabla 4: Heterogeneidad (`heterogeneity.py`)

**Pregunta:** ¿El efecto es diferente en municipios rurales vs urbanos?
¿En municipios grandes vs pequeños?

**¿Qué hace?** Corre la regresión TWFE **por separado** para cada subgrupo:

```python
# Para cada tipo de municipio (Rural, Urbano, etc.):
for val in ["Rural", "En Transicion", "Semi-urbano", "Urbano", ...]:
    sub = df[df["tipo_pob"] == val]    # Filtrar solo ese tipo
    res = run_panel_ols(sub, ...)       # Correr regresión
```

**Corrección Benjamini-Hochberg:** Cuando haces muchos tests al mismo tiempo,
aumenta el riesgo de encontrar un resultado falso por casualidad. La corrección
BH ajusta los p-valores para esto:

```python
from statsmodels.stats.multitest import multipletests
_, q_values, _, _ = multipletests(pvals, method="fdr_bh")
# q_values son los p-valores corregidos
```

### 3.6 Tabla 5 + Figura 3: DiD Moderno — Stacked DiD (`run_stacked_did.py`)

**Pregunta:** ¿El TWFE clásico tiene un sesgo? ¿Qué pasa si lo corregimos?

**El problema con TWFE:** Cuando los municipios reciben el tratamiento en
**diferentes momentos** (staggered treatment), el TWFE clásico puede tener
un sesgo. Algunos municipios tratados tempranamente sirven como "controles"
para los tratados tardíamente, lo que contamina la estimación.

**La solución: Stacked DiD** (Cengiz et al., 2019):

1. Para **cada cohorte** (grupo de municipios que recibió el tratamiento al
   mismo tiempo), crear un sub-dataset con:
   - Los municipios de esa cohorte (tratados)
   - Los municipios que **nunca** fueron tratados (controles)

2. **Apilar** todos los sub-datasets.

3. Estimar una sola regresión sobre el dataset apilado con efectos fijos
   anidados.

**En el código:**

```python
# 1. Para cada cohorte g (ej. municipios tratados en t=3):
def build_cohort_stack(df, cohort_first_t, never_treated_muns):
    # Tomar municipios tratados de esta cohorte + never-treated
    muns = treated_muns | never_treated_muns

    # Restringir a ventana alrededor del evento: [-4, +8]
    mask = (df["t_index"] >= t_min) & (df["t_index"] <= t_max)

    # Crear IDs de stack para FE anidados
    sub["mun_stack"] = sub["cve_mun"].astype(str) + "_" + str(cohort_first_t)
    sub["t_stack"] = sub["t_index"].astype(str) + "_" + str(cohort_first_t)

    return sub

# 2. Apilar todos los sub-datasets
stacked = pd.concat(stacks, ignore_index=True)

# 3. Regresión pooled con FE de municipio×stack y periodo×stack
mod = PanelOLS(y, X, entity_effects=True, time_effects=True)
# SE clustered a nivel del municipio ORIGINAL (no el de stack)
res = mod.fit(cov_type="clustered", clusters=_cluster_mun)
```

**¿Por qué clustered a nivel del municipio original?** Porque el mismo
municipio puede aparecer en varios stacks (si es never-treated, aparece como
control en todos). El clustering a nivel original captura esa correlación.

### 3.7 Tabla 6: MDES — Minimum Detectable Effect Size (`mdes_power.py`)

**Pregunta:** Si no encontramos un efecto significativo, ¿qué tan grande
tendría que ser el efecto para que lo hubiéramos detectado?

**¿Por qué importa?** Un resultado nulo (no significativo) puede significar
dos cosas:
1. **No hay efecto.** La alcaldesa no cambia nada.
2. **Hay efecto, pero no tenemos suficientes datos** para detectarlo.

El MDES nos dice cuál es el **efecto mínimo** que nuestros datos podrían
detectar con 80% de probabilidad (poder estadístico).

**La fórmula:**

```
MDES = (z_{α/2} + z_β) × SE

Donde:
  z_{α/2} = 1.96  (para α = 0.05, test bilateral)
  z_β     = 0.84  (para 80% de poder)
  SE      = error estándar del coeficiente TWFE

Factor total = 1.96 + 0.84 = 2.80
MDES = 2.80 × SE
```

**Interpretación:** Si el MDES para contratos totales es 0.10 en escala asinh
(≈ 10.5%), significa: "podemos descartar que la alcaldesa cause un aumento
mayor al 10.5% en contratos totales. Si el efecto fuera de esa magnitud,
lo habríamos detectado."

### 3.8 Figura 2: Sensibilidad del Event Study (`event_study_sensitivity.py`)

**Pregunta:** ¿Los resultados del event study cambian si ajustamos la ventana
temporal?

**El problema específico:** En tarjetas de crédito, un coeficiente tenía
p = 0.083 (marginalmente significativo), pero podría depender de cómo se
define el "bin extremo" (el periodo más alejado). El código prueba variantes:

| Variante | Descripción |
|----------|-------------|
| Baseline (K=4, L=8) | Ventana original |
| A: K=3, L=8 | Menos leads (3 en vez de 4) |
| B: K=6, L=8 | Más leads (6 en vez de 4) |
| C: Excl. cohorte g=0 | Excluir municipios tratados desde el principio |

### 3.9 Sample Policy (`sample_policy.py`)

**Pregunta:** ¿Importa si incluimos o excluimos los municipios con panel
incompleto?

```python
# Full sample: todos los municipios
raw_full = run_twfe_sample(df, "full")

# Main sample: solo municipios con panel completo (17 trimestres)
df_main = df[df["flag_incomplete_panel"] == 0]
raw_main = run_twfe_sample(df_main, "main")
```

Si los resultados son similares, la elección de muestra no afecta las
conclusiones.

### 3.10 Tabla 7: Margen Extensivo y Composición (`extensive_margin.py`)

**Pregunta:** ¿La alcaldesa hace que **más mujeres** tengan acceso a servicios
financieros (margen extensivo)? ¿Cambia la **proporción** de mujeres entre
los clientes (composición de género)?

| Panel | Variable | Interpretación |
|-------|----------|----------------|
| **A: Extensivo** | `any_ncont_total_m = 1{ncont > 0}` | ¿Hay **algún** contrato de mujer? (acceso mínimo) |
| **B: Composición** | `share_m = y_m / (y_m + y_h)` | ¿Qué **proporción** de los clientes son mujeres? |

```python
# Margen extensivo: variable binaria (0 o 1)
df["any_ncont_total_m"] = (df["ncont_total_m"] > 0).astype(float)

# Composición de género
total = df["ncont_total_m_pc"] + df["ncont_total_h_pc"]
df["share_m_ncont_total"] = df["ncont_total_m_pc"] / total
```

---

## Parte 4 — ¿Cómo leer e interpretar los resultados?

### 4.1 Anatomía de una tabla de resultados

Veamos una tabla típica (Tabla 2 — TWFE Baseline):

```
Outcome               Coef       SE      p-valor    IC 95%              N
Contratos totales     0.0121    (0.0152)  0.4280    [-0.0178, 0.0420]   41,485
Tarjetas débito      -0.0031    (0.0114)  0.7856    [-0.0255, 0.0193]   41,485
Tarjetas crédito      0.0189    (0.0146)  0.1946    [-0.0098, 0.0476]   41,485
...
```

| Columna | ¿Qué significa? |
|---------|-----------------|
| **Coef** | El valor de β — el efecto estimado de la alcaldesa |
| **SE** | Error estándar — la "incertidumbre" de la estimación |
| **p-valor** | Probabilidad de que este resultado sea por casualidad |
| **IC 95%** | Rango donde creemos que está el efecto verdadero (95% de confianza) |
| **N** | Número de observaciones usadas |

### 4.2 ¿Cómo interpretar el p-valor?

El **p-valor** responde: "Si no hubiera efecto real (β = 0), ¿qué tan probable
es obtener un resultado así de extremo solo por casualidad?"

| p-valor | Interpretación | Estrellas |
|---------|---------------|-----------|
| p < 0.01 | Muy fuerte evidencia de efecto | `***` |
| p < 0.05 | Evidencia de efecto | `**` |
| p < 0.10 | Evidencia débil de efecto | `*` |
| p ≥ 0.10 | No hay evidencia suficiente de efecto | (ninguna) |

**Ejemplo:** Si β = 0.082 y p = 0.003, decimos: "la probabilidad de obtener
un coeficiente así de grande solo por casualidad es de 0.3%. Hay evidencia
muy fuerte de un efecto."

### 4.3 ¿Cómo interpretar el coeficiente en escala asinh?

El coeficiente β está en escala **asinh** (seno hiperbólico inverso).
**Regla rápida:**

> Para valores no muy pequeños, un β de 0.05 ≈ un efecto del **~5%**.

Más precisamente:

```
% cambio ≈ (exp(|β|) − 1) × 100
```

| β (asinh) | % cambio aproximado |
|-----------|-------------------|
| 0.01 | ~1.0% |
| 0.05 | ~5.1% |
| 0.10 | ~10.5% |
| 0.20 | ~22.1% |
| 0.50 | ~64.9% |

### 4.4 ¿Qué son las estrellas (`***`, `**`, `*`)?

Son un código visual para el nivel de significancia estadística:

```python
def stars(pval):
    if pval < 0.01:
        return "***"    # Muy significativo
    elif pval < 0.05:
        return "**"     # Significativo
    elif pval < 0.10:
        return "*"      # Marginalmente significativo
    return ""           # No significativo
```

### 4.5 ¿Cómo leer un gráfico de event study?

El gráfico del event study muestra:

```
         δ_k (efecto)
          │
    0.1   │           ●───●
          │          /
    0.0   │──●──●──●─────────── línea de referencia (efecto = 0)
          │
   -0.1   │
          └──────────────────── event time (k)
           -4  -3  -2  -1   0   1   2   3
                         ↑
                  línea roja punteada
                  (inicio del tratamiento)
```

- **Puntos:** El coeficiente estimado δ_k para cada periodo.
- **Banda sombreada:** El intervalo de confianza al 95%.
- **Lado izquierdo (k < 0):** Si los puntos son ≈ 0, las pre-trends son
  paralelas (¡bien!).
- **Lado derecho (k ≥ 0):** Si los puntos se alejan de 0, hay efecto.
- **Línea roja punteada:** Marca el inicio del tratamiento.

### 4.6 El resultado principal de la tesis

> El TWFE convencional **no detecta** efectos significativos en ninguno de los
> 5 indicadores.
>
> Sin embargo, el **Stacked DiD** (DiD moderno) revela efectos positivos y
> significativos en:
> - **Contratos totales:** β = 0.082, p = 0.003 (≈ +8.5%)
> - **Saldo total:** β = 0.274, p < 0.001 (≈ +31.5%)
>
> Para tarjetas de débito, crédito e hipotecarios, ambos métodos coinciden
> en la **ausencia de efectos**.

---

## Parte 5 — ¿Cómo correr el código tú mismo/a?

### 5.1 Requisitos

Necesitas:
1. **Python 3.10 o superior** (descárgalo de python.org)
2. **PostgreSQL 17+** con la base de datos `tesis_db` poblada
3. **Git** para clonar el repositorio

### 5.2 Instalación paso a paso

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/tesis-2026.git
cd tesis-2026/Code

# 2. Crear un entorno virtual (para no mezclar con otros proyectos)
python3 -m venv .venv
source .venv/bin/activate     # En Mac/Linux
# .venv\Scripts\activate      # En Windows

# 3. Instalar dependencias
pip install -r requirements.txt
pip install -e .               # Instala el paquete tesis_alcaldesas

# 4. Configurar la base de datos
cp .env.example .env
# Edita .env con tus credenciales de PostgreSQL
```

### 5.3 Configurar la base de datos

Edita el archivo `.env`:

```bash
PGHOST=localhost       # Dónde está la base de datos
PGPORT=5432            # Puerto (el default de PostgreSQL)
PGDATABASE=tesis_db    # Nombre de la base de datos
PGUSER=tu_usuario      # Tu usuario de PostgreSQL
PGPASSWORD=            # Tu contraseña (vacía si no tienes)
```

### 5.4 Ejecutar el pipeline

```bash
# Paso 1: Extraer datos de PostgreSQL → archivo parquet
python -m tesis_alcaldesas.data.extract_panel

# Paso 2: Construir features (transformaciones)
python -m tesis_alcaldesas.data.build_features

# Paso 3: Correr modelos uno por uno
python -m tesis_alcaldesas.models.table1_descriptives   # Tabla 1
python -m tesis_alcaldesas.models.twfe                  # Tabla 2
python -m tesis_alcaldesas.models.event_study           # Figura 1
python -m tesis_alcaldesas.models.robustness            # Tabla 3
python -m tesis_alcaldesas.models.heterogeneity         # Tabla 4

# O correr TODO de una vez:
PYTHONPATH=src python -m tesis_alcaldesas.run_all
```

### 5.5 ¿Dónde están los resultados?

Todos los resultados se guardan en `outputs/paper/`:

| Archivo | Contenido |
|---------|-----------|
| `tabla_1_descriptiva.csv` | Estadísticos descriptivos |
| `tabla_2_twfe.csv` | Resultados TWFE baseline |
| `tabla_3_robustez.csv` | Pruebas de robustez |
| `tabla_4_heterogeneidad.csv` | Heterogeneidad |
| `tabla_5_did_moderno.csv` | DiD moderno (stacked) |
| `tabla_6_mdes.csv` | MDES / poder estadístico |
| `tabla_7_extensive.csv` | Margen extensivo y composición |
| `figura_1_event_study.pdf` | Gráfico event study |
| `figura_2_event_study_sens.pdf` | Sensibilidad event study |
| `figura_3_did_moderno_eventstudy.pdf` | Event study del DiD moderno |

### 5.6 Resolución de problemas comunes

| Problema | Solución |
|----------|---------|
| `ModuleNotFoundError: No module named 'tesis_alcaldesas'` | Ejecuta `pip install -e .` desde la carpeta `Code/` |
| Error de conexión a PostgreSQL | Verifica que PostgreSQL esté corriendo y que `.env` tenga las credenciales correctas |
| `FileNotFoundError: analytical_panel.parquet` | Ejecuta primero `python -m tesis_alcaldesas.data.extract_panel` |
| `PYTHONPATH` error con DiD moderno | Usa `PYTHONPATH=src` antes del comando |

---

## Apéndice A — Glosario

| Término | Definición |
|---------|-----------|
| **asinh** | Seno hiperbólico inverso. Transformación que comprime valores extremos. Similar al logaritmo pero funciona con ceros y negativos. |
| **ATT** | Average Treatment Effect on the Treated. El efecto promedio del tratamiento en los municipios que fueron tratados. |
| **Benjamini-Hochberg** | Método para corregir p-valores cuando se hacen muchas pruebas estadísticas al mismo tiempo, controlando la tasa de falsos descubrimientos. |
| **Cluster SE** | Errores estándar agrupados. Tienen en cuenta que las observaciones del mismo municipio no son independientes entre sí. |
| **Cohorte** | Grupo de municipios que recibieron el tratamiento al mismo tiempo. |
| **DataFrame** | Tabla de datos en Python (librería pandas). Equivalente a una hoja de Excel. |
| **DiD** | Diferencias en Diferencias. Método para estimar efectos causales comparando cambios entre grupos tratados y no tratados. |
| **Efecto fijo de municipio (α_i)** | Control estadístico para todas las características permanentes de un municipio. |
| **Efecto fijo de tiempo (γ_t)** | Control estadístico para todos los shocks comunes a todos los municipios en un trimestre. |
| **Error estándar (SE)** | Medida de incertidumbre del coeficiente estimado. Cuanto más pequeño, más precisa la estimación. |
| **Event study** | Análisis que descompone el efecto del tratamiento periodo por periodo, para verificar tendencias paralelas. |
| **Event time** | Tiempo relativo al inicio del tratamiento. k = −2 significa "2 periodos antes del tratamiento". |
| **LPM** | Linear Probability Model. Regresión lineal donde la variable dependiente es binaria (0 o 1). |
| **MDES** | Minimum Detectable Effect Size. El efecto mínimo que los datos pueden detectar con cierta probabilidad. |
| **Never-treated** | Municipio que nunca tuvo alcaldesa durante todo el periodo de estudio. |
| **p-valor** | Probabilidad de observar un resultado tan extremo si el efecto verdadero fuera cero. Valores bajos (< 0.05) sugieren un efecto real. |
| **Panel** | Datos donde se observan las mismas unidades (municipios) a lo largo del tiempo. |
| **Parquet** | Formato de archivo columnar eficiente para datos tabulares. Más rápido que CSV. |
| **Per cápita** | "Por persona" — dividir entre la población para poder comparar unidades de distinto tamaño. |
| **Pre-trends** | Tendencias anteriores al tratamiento. Si son paralelas entre grupos, el supuesto clave del DiD se cumple. |
| **Stacked DiD** | Variante del DiD que corrige sesgos cuando el tratamiento llega en diferentes momentos (staggered). |
| **Switcher** | Municipio que cambió de no tener alcaldesa a tener alcaldesa (o viceversa). |
| **TWFE** | Two-Way Fixed Effects. Regresión con efectos fijos de unidad (municipio) y de tiempo (trimestre). |
| **Winsorización** | Reemplazar los valores extremos (por encima del percentil 99 o debajo del percentil 1) por el valor del percentil correspondiente. |

---

## Apéndice B — Mapa de archivos del código

Para que puedas navegar el repositorio con confianza:

```
src/
├── tesis_alcaldesas/              ← Paquete principal
│   ├── __init__.py                ← Marca esto como paquete Python
│   ├── config.py                  ← Rutas, conexión BD, constantes
│   ├── run_all.py                 ← Ejecuta TODO el pipeline
│   ├── data/
│   │   ├── extract_panel.py       ← Paso 1: PostgreSQL → parquet
│   │   └── build_features.py      ← Paso 2: per cápita, asinh, etc.
│   └── models/
│       ├── utils.py               ← Funciones compartidas (load_panel, PanelOLS, etc.)
│       ├── table1_descriptives.py ← Tabla 1: estadísticos descriptivos
│       ├── twfe.py                ← Tabla 2: regresión TWFE principal
│       ├── event_study.py         ← Figura 1: diagnóstico de pre-trends
│       ├── robustness.py          ← Tabla 3: pruebas de robustez
│       ├── heterogeneity.py       ← Tabla 4: ¿efecto diferente por tipo?
│       ├── mdes_power.py          ← Tabla 6: ¿qué efectos descartamos?
│       ├── event_study_sensitivity.py ← Figura 2: ¿bin extremo importa?
│       ├── sample_policy.py       ← Main sample vs full sample
│       └── extensive_margin.py    ← Tabla 7: acceso y composición
│
├── did_moderno/                   ← DiD moderno (corrección TWFE)
│   ├── run_stacked_did.py         ← Tabla 5 + Figura 3
│   └── window_robustness.py       ← Robustez de ventana
│
├── eda/                           ← Análisis exploratorio
├── transformaciones_criticas.py   ← Transformaciones del EDA
├── transformaciones_altas.py      ← Más transformaciones
├── transformaciones_medias.py     ← Más transformaciones
└── tests/                         ← 43 tests de validación
```

---

## Apéndice C — Flujo completo del pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS (PostgreSQL)                    │
│              inclusion_financiera_clean                          │
│              41,905 filas × 175 columnas                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                  extract_panel.py
                   (seleccionar ~61 columnas)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              analytical_panel.parquet                            │
│              41,905 filas × ~61 columnas                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                  build_features.py
                   (per cápita, asinh, cohortes...)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│          analytical_panel_features.parquet                       │
│          41,905 filas × ~170 columnas                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
         ▼                 ▼                  ▼
  ┌──────────┐    ┌──────────────┐    ┌──────────────┐
  │ Tabla 1  │    │  Tabla 2     │    │  Figura 1    │
  │ Descr.   │    │  TWFE        │    │  Event Study │
  └──────────┘    └──────────────┘    └──────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
         ▼                 ▼                  ▼
  ┌──────────┐    ┌──────────────┐    ┌──────────────┐
  │ Tabla 3  │    │  Tabla 4     │    │  Tabla 5     │
  │ Robustez │    │  Heterog.    │    │  DiD moderno │
  └──────────┘    └──────────────┘    └──────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
         ▼                 ▼                  ▼
  ┌──────────┐    ┌──────────────┐    ┌──────────────┐
  │ Tabla 6  │    │  Figura 2    │    │  Tabla 7     │
  │ MDES     │    │  Sensib.     │    │  Extensivo   │
  └──────────┘    └──────────────┘    └──────────────┘
                           │
                           ▼
                  outputs/paper/
                  (tablas CSV/TeX + figuras PDF/PNG)
```

---

*Última actualización: 02/03/2026*
*Guía creada como parte de la documentación pedagógica del proyecto de tesis.*
