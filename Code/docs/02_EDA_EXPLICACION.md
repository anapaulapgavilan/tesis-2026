# Explicación Detallada del Análisis Exploratorio de Datos (EDA)

**Proyecto:** Efecto causal de las alcaldesas en la inclusión financiera de las mujeres en México  
**Base de datos:** `tesis_db` (PostgreSQL 17.8) · Tabla: `inclusion_financiera`  
**Panel:** 2,471 municipios × 17 trimestres (2018Q3 – 2022Q3) = 41,905 observaciones  
**Fecha de generación:** Junio 2025  

---

## Índice

1. [Objetivo del EDA](#1-objetivo-del-eda)  
2. [Estructura del análisis](#2-estructura-del-análisis)  
3. [Sección A — Diccionario observado](#3-sección-a--diccionario-observado)  
4. [Sección B — Calidad e integridad](#4-sección-b--calidad-e-integridad)  
5. [Sección C — Distribuciones univariadas](#5-sección-c--distribuciones-univariadas)  
6. [Sección D — Relaciones bivariadas](#6-sección-d--relaciones-bivariadas)  
7. [Sección E — Sesgo y leakage](#7-sección-e--sesgo-y-leakage)  
8. [Sección F — Recomendaciones](#8-sección-f--recomendaciones)  
9. [Archivos generados](#9-archivos-generados)  
10. [Conclusiones y próximos pasos](#10-conclusiones-y-próximos-pasos)  

---

## 1. Objetivo del EDA

El EDA tiene un objetivo doble:

1. **Conocer la base de datos a profundidad** — entender qué variables existen, su distribución, calidad, valores faltantes y posibles problemas antes de cualquier modelado.
2. **Orientar la estrategia de estimación causal** — validar supuestos clave (como tendencias paralelas para Difference-in-Differences), identificar variables con riesgo de leakage o sesgo, y definir las transformaciones necesarias para que los modelos sean válidos.

La pregunta de investigación que guía todo el análisis es:

> **¿Cuál es el efecto de tener una alcaldesa (mujer como autoridad municipal) en la inclusión financiera de las mujeres en los municipios de México?**

El tratamiento es la variable `alcaldesa_final` (1 = mujer como autoridad municipal, 0 = hombre).

---

## 2. Estructura del análisis

El EDA se organizó en **6 secciones** siguiendo una guía práctica para datos tabulares en panel:

| Sección | Nombre | Propósito |
|---------|--------|-----------|
| **A** | Diccionario observado | Catalogar todas las 175 variables con tipo, NAs, distribución |
| **B** | Calidad e integridad | Validar llave primaria, balance del panel, consistencia |
| **C** | Distribuciones univariadas | Visualizar cada variable clave de forma individual |
| **D** | Relaciones bivariadas | Comparar tratamiento vs. control; validar supuestos causales |
| **E** | Sesgo / leakage | Identificar variables peligrosas para el modelo |
| **F** | Recomendaciones | Listar transformaciones necesarias antes del modelado |

Antes de las secciones, hay un bloque de **configuración (Sección 0)** que:
- Carga las librerías necesarias (pandas, numpy, matplotlib, seaborn, sqlalchemy)
- Establece la semilla de reproducibilidad (`SEED = 42`)
- Configura el estilo visual de los gráficos
- Conecta a la base de datos PostgreSQL
- Define constantes del análisis (variable de tratamiento, llave primaria, columnas de outcomes)
- Carga la tabla completa a un DataFrame de pandas (41,905 filas × 175 columnas)
- Crea una función `per_capita()` para normalizar conteos por población adulta (× 10,000)

---

## 3. Sección A — Diccionario observado

### ¿Qué se hizo?

Se generó un **perfil automático de cada una de las 175 variables** de la base de datos. Para cada variable se calculó:

- **dtype**: Tipo de dato (int64, float64, str, etc.)
- **na_n / na_pct**: Número y porcentaje de valores nulos
- **n_unique**: Número de valores únicos
- Para variables **numéricas**: min, p25, p50 (mediana), p75, max, media, desviación estándar, coeficiente de variación (CV)
- Para variables **categóricas**: valor más frecuente (moda) y su conteo
- **Comentarios automáticos**: alertas si la variable tiene >60% NAs, es constante (1 solo valor), o tiene alta dispersión (CV > 5)

### Resultados clave

| Métrica | Valor |
|---------|-------|
| Variables totales | 175 |
| Con valores nulos | 47 |
| Constantes (std = 0) | 3 (`hist_state_available`, `missing_quarters_alcaldesa`, `ok_panel_completo_final`) |
| Con >60% NAs | Variables `saldoprom_*` — son NULLs **estructurales** (resultado de ÷0 cuando no hay contratos) |
| Alta dispersión (CV > 5) | Mayoría de outcomes financieros — esperado dado la enorme variación en tamaño de municipios |

**Interpretación:** La base tiene buena cobertura general. Los NULLs no son aleatorios sino estructurales (municipios sin contratos no pueden tener saldo promedio). Las 3 constantes deben excluirse de cualquier modelo. La alta dispersión en outcomes confirma que la normalización per cápita es imprescindible.

### Archivo generado
- `outputs/eda/A_diccionario_observado.csv` — Catálogo completo de 175 variables con todas las estadísticas

---

## 4. Sección B — Calidad e integridad

### ¿Qué se hizo?

Se ejecutaron **6 pruebas de calidad** sobre la base de datos:

#### B1. Validación de llave primaria
- Se verificó que no existen **duplicados** en la combinación `(cve_mun, periodo_trimestre)`.
- **Resultado: ✓ 0 duplicados.** Cada municipio-trimestre aparece exactamente una vez.

#### B2. Balance del panel
- Se contó cuántos trimestres tiene cada municipio para verificar si el panel está **100% balanceado**.
- **Resultado: Panel casi balanceado.** 2,463 municipios tienen los 17 trimestres completos. 8 municipios se incorporan gradualmente (2 en 2020Q1, 4 en 2021Q1, 2 en 2021Q4). Esto es normal — son municipios creados durante el periodo.

#### B3. Completitud por periodo
- Se generó una tabla con el número de municipios, filas y porcentaje de alcaldesas por cada trimestre.
- **Resultado:** El % de alcaldesas se estabiliza alrededor de 22-23% a partir de 2019Q1, con un inicio más bajo (16%) en 2018Q3.

| Trimestre | Municipios | % Alcaldesa |
|-----------|------------|-------------|
| 2018Q3 | 2,463 | 16.0% |
| 2019Q1 | 2,463 | 22.9% |
| 2020Q1 | 2,465 | 22.8% |
| 2021Q1 | 2,469 | 22.7% |
| 2022Q3 | 2,463 | 22.4% |

#### B4. Consistencia geográfica
- Se verificó que ningún municipio **cambia de estado** entre trimestres.
- **Resultado: ✓ 0 municipios inconsistentes.**

#### B5. NULLs en tipo_pob
- Se identificaron **2 observaciones** con `tipo_pob` nulo.
- **Resultado: ⚠ Impacto mínimo.** Solo 2 de 41,905 filas.

#### B6. Valores negativos
- Se buscaron valores negativos en todas las columnas numéricas (no debería haber en conteos financieros).
- **Resultado: ✓ 0 columnas con negativos.**

### Resumen de calidad

| Check | Resultado | Status |
|-------|-----------|--------|
| Duplicados PK | 0 | ✓ |
| Panel 100% balanceado | Casi (8 municipios incorporados tarde) | ✗ (tolerable) |
| Municipios cambian estado | 0 | ✓ |
| NULLs en tipo_pob | 2 | ⚠ |
| Columnas con negativos | 0 | ✓ |
| Periodos cubiertos | 2018Q3–2022Q3 (17) | ✓ |

### Archivos generados
- `outputs/eda/B_calidad_integridad.csv` — Tabla resumen de las 6 pruebas
- `outputs/eda/B_completitud_panel.csv` — Municipios y % tratamiento por trimestre

---

## 5. Sección C — Distribuciones univariadas

### ¿Qué se hizo?

Se visualizaron las **distribuciones individuales** de las variables más importantes. Se generaron 5 gráficos:

#### C1. Proporción de alcaldesas por trimestre
- **Gráfico de línea** mostrando el % de municipios con alcaldesa en cada trimestre.
- **Resultado:** El tratamiento empieza en 16% (2018Q3) y sube a ~23% para 2019, manteniéndose estable hasta 2022Q3 (~22.4%). La media global es ~22%.
- **Interpretación:** El salto de 16% a 22.9% entre 2018Q3 y 2019Q1 refleja los cambios de gobierno municipal tras las elecciones. La estabilidad posterior sugiere que los cambios de tratamiento son de elección a elección, con poca variación dentro del mandato.

#### C2. Clasificación de municipios por exposición al tratamiento
- **Gráfico de barras** con tres categorías: switchers, nunca tratados, siempre tratados.
- **Resultado:**
  - **Nunca tratado:** 1,476 municipios (59.7%) — nunca tuvieron alcaldesa
  - **Switcher:** 894 municipios (36.2%) — cambiaron de tratamiento al menos una vez
  - **Siempre tratado:** 101 municipios (4.1%) — siempre tuvieron alcaldesa
- **Interpretación:** Los 894 **switchers son clave** para la identificación causal. Son los municipios que proporcionan variación within (dentro del mismo municipio) que los modelos de efectos fijos aprovechan.

#### C3. Distribución de población (escala log)
- **Histogramas** en escala logarítmica para: población total, población adulta mujeres, población adulta hombres.
- **Resultado:** Las tres distribuciones son **log-normales** con cola derecha fuerte. La mediana de población total es ~13,700 pero el rango va de 81 a 1,922,523.
- **Interpretación:** El uso de `log(pob)` como control en regresiones es indispensable. La enorme variación en tamaño (CV = 2.87) hace que las comparaciones en niveles sean inválidas.

#### C4. Boxplot de outcomes per cápita (mujeres)
- **Boxplots** (sin outliers) para los 10 outcomes de inclusión financiera de mujeres, normalizados por 10,000 mujeres adultas.
- **Resultado:** Los outcomes con mayor magnitud per cápita son depósitos a plazo (`plazo_m_pc`) y contratos nivel 2 (`n2_m_pc`). Variables como ahorro, nivel 1 y nivel 3 tienen medianas cercanas a cero.
- **Interpretación:** Hay gran heterogeneidad en los productos financieros. Los productos más "básicos" (nivel 2, débito) tienen mayor penetración; los más sofisticados (hipotecas, crédito) son mucho más escasos.

#### C5. Distribución de categóricas clave
- **Tres subgráficos:**
  - (a) Municipios por región: la región Sur concentra más municipios (Oaxaca tiene 570 municipios)
  - (b) Municipios por tipo de población: predominan Semi-urbano y Rural
  - (c) % trimestres con alcaldesa por región: variación regional significativa
- **Interpretación:** La distribución desigual de municipios por región es importante para los efectos fijos. Oaxaca, con sus usos y costumbres, tiene dinámicas especiales que los FE de municipio absorberán.

### Archivos generados
- `outputs/eda/C1_tratamiento_por_trimestre.png`
- `outputs/eda/C2_distribucion_poblacion.png` (o `C2_tipo_exposicion.png` en notebook)
- `outputs/eda/C3_boxplot_outcomes_mujeres_pc.png` (o `C3_distribucion_poblacion.png`)
- `outputs/eda/C4_categoricas_clave.png` (o `C4_boxplot_outcomes_mujeres_pc.png`)
- `outputs/eda/C5_tipo_pob_tratamiento.png` (o `C5_categoricas_clave.png`)

> **Nota:** Los nombres de archivos difieren ligeramente entre `run_eda.py` (los nombres en `outputs/eda/`) y `eda.ipynb` (que usa la misma convención pero el contenido visual es idéntico).

---

## 6. Sección D — Relaciones bivariadas

### ¿Qué se hizo?

Se analizaron las **relaciones entre variables**, orientadas directamente a la pregunta de investigación. Se generaron 7 gráficos y tablas:

#### D1. Outcomes per cápita por tratamiento (boxplot)
- **6 boxplots** comparando municipios con y sin alcaldesa para: ahorro, total contratos, tarjetas débito, tarjetas crédito, créditos hipotecarios, depósitos a plazo.
- **Resultado:** Descriptivamente, los municipios **sin alcaldesa** tienden a tener outcomes per cápita **ligeramente mayores o similares** a los municipios con alcaldesa.
- **Interpretación CRUCIAL:** Esto NO significa que las alcaldesas "reduzcan" la inclusión financiera. Los municipios con alcaldesa tienden a ser **más pequeños y rurales** (sesgo de selección). La diferencia cruda está confundida por características observables e inobservables del municipio. Por eso se necesitan efectos fijos y controles.

#### D2. Brecha de género: tendencia temporal mujeres vs. hombres
- **6 gráficos de línea** mostrando la evolución temporal de outcomes per cápita de mujeres vs. hombres para cada producto financiero.
- **Resultado:** En casi todos los productos, los hombres tienen **más contratos per cápita** que las mujeres. La brecha es más pronunciada en créditos hipotecarios y tarjetas de crédito.
- **Interpretación:** Existe una brecha de género persistente en inclusión financiera. Ambos sexos muestran tendencias crecientes similares, pero la brecha se mantiene o se reduce lentamente.

#### D3. Tendencias paralelas (clave para DiD)
- **3 gráficos de línea** comparando la evolución de outcomes per cápita entre municipios tratados y controles para: contratos totales, tarjetas débito, ahorro.
- **Resultado:** Las tendencias de municipios tratados y controles se mueven de forma **aproximadamente paralela** antes del tratamiento para la mayoría de productos.
- **Interpretación:** Este es el **supuesto más importante** para la estimación por Difference-in-Differences. Si las tendencias fueran paralelas antes del tratamiento, cualquier divergencia posterior podría atribuirse al efecto de tener alcaldesa. La validación visual es un primer paso; el event study confirmará formalmente.

#### D4. Ratio Mujer/Hombre por tratamiento
- **3 gráficos de línea** mostrando la evolución del ratio M/H (mediana) para municipios tratados vs. controles.
- **Resultado:** Los ratios oscilan entre 0.8 y 1.1 dependiendo del producto. No se observa una divergencia clara entre tratados y controles.
- **Interpretación:** Si las alcaldesas mejoran la inclusión financiera de mujeres **relativamente** a hombres, el ratio M/H debería subir más en municipios tratados. La evidencia descriptiva es ambigua — el modelo causal formal lo resolverá.

#### D5. Correlaciones de Spearman
- **Heatmap** de correlaciones de Spearman entre tratamiento, población, y los 7 principales outcomes de mujeres.
- **Resultado:**
  - Correlación outcomes-población: **0.60–0.70** (muy alta)
  - Correlación tratamiento-outcomes: baja en niveles (precisamente porque la relación cruda está confundida)
  - Correlaciones cruzadas entre outcomes: altas (0.40–0.85), lo que sugiere un factor latente de "tamaño del sistema financiero"
- **Interpretación:** La alta correlación outcomes-población **confirma que normalizar per cápita es CRÍTICA**. Sin normalización, los modelos capturarían el efecto del tamaño poblacional, no del tratamiento.

#### D6. Balance pre-tratamiento
- **3 boxplots** comparando switchers, nunca-tratados y siempre-tratados en el periodo base (2018Q3) para: población total, población adulta mujeres, contratos totales mujeres.
- **Resultado:** Los municipios **siempre tratados** son en promedio más pequeños que los nunca-tratados. Los switchers se ubican en un punto intermedio.
- **Interpretación:** Hay **diferencias sistemáticas entre grupos**, lo que refuerza la necesidad de efectos fijos de municipio (que absorben diferencias de nivel permanentes). El modelo TWFE aprovecha solo la variación **within** (cambios dentro del mismo municipio a lo largo del tiempo).

#### D7. Heatmap de alcaldesas por estado y año
- **Mapa de calor** mostrando el % de trimestres con alcaldesa para cada estado en cada año (2018–2022).
- **Resultado:** Enorme variación geográfica:
  - **Estados con más alcaldesas:** Baja California (~51%), Baja California Sur (~49%), Quintana Roo (~43%)
  - **Estados con menos alcaldesas:** Estado de México (~10%), Tlaxcala (~12%)
- **Interpretación:** La variación geográfica sugiere que factores culturales, institucionales y partidistas influyen en la selección de candidatas mujeres. Los efectos fijos de municipio capturan estos factores time-invariant.

### Archivos generados
- `outputs/eda/D1_outcomes_por_tratamiento.png`
- `outputs/eda/D2_brecha_genero_temporal.png`
- `outputs/eda/D3_tendencia_por_tratamiento.png` / `D3_tendencias_paralelas.png`
- `outputs/eda/D4_ratio_MH_por_tratamiento.png`
- `outputs/eda/D5_correlaciones_spearman.png`
- `outputs/eda/D6_balance_pre_tratamiento.png`

---

## 7. Sección E — Sesgo y leakage

### ¿Qué se hizo?

Se identificaron **54 variables** que podrían causar problemas si se usan como controles en el modelo causal. Se clasificaron en 6 categorías:

#### E1. Leakage temporal (3 variables)
- Variables: `alcaldesa_final_f1`, `alcaldesa_final_f2`, `alcaldesa_final_f3`
- **Problema:** Son "adelantos" (forwards) del tratamiento — contienen información del futuro (t+1, t+2, t+3). Usarlas como controles violaría la temporalidad causal.
- **Acción:** EXCLUIR de regresiones como regresores; usar SOLO en event studies para testear pre-trends.

#### E2. Variables endógenas (2 variables)
- Variables: `alcaldesa_transition`, `alcaldesa_transition_gender`
- **Problema:** Son contemporáneas al tratamiento y potencialmente correlacionadas con outcomes. Si un cambio de gobierno afecta simultáneamente la inclusión financiera, incluirlas como controles absorbería parte del efecto que queremos medir.
- **Acción:** Usar variantes `*_excl_trans` como análisis de robustez, no como control principal.

#### E3. Artefactos de construcción (7 variables)
- Variables: `hist_mun_available`, `hist_state_available`, `ok_panel_completo`, `ok_panel_completo_final`, `missing_quarters_alcaldesa`, `filled_by_manual`, `quarters_in_base`
- **Problema:** Son variables de proceso/calidad usadas durante la construcción de la base de datos. No existían antes del tratamiento y no representan confusores causales.
- **Acción:** NO usar como controles en regresiones.

#### E4. Constantes (3 variables)
- Variables: `hist_state_available`, `missing_quarters_alcaldesa`, `ok_panel_completo_final`
- **Problema:** Tienen varianza = 0 (mismo valor en todas las observaciones). No aportan ninguna información al modelo.
- **Acción:** EXCLUIR de regresiones (serían automáticamente eliminadas por colinealidad).

#### E5. Flags de proceso (~20 variables)
- Variables: Todas las que empiezan con `flag_undef_saldoprom_*`
- **Problema:** Son indicadoras de missingness estructural (marcan si el saldo promedio es indefinido porque no hay contratos). Son útiles para filtrar pero no son confusores causales.
- **Acción:** Usar solo para filtrar muestras analíticas (e.g., filtrar `flag_undef_saldoprom_ahorro_m = 0` para analizar solo municipios con ahorro).

#### E6. Rezagos del tratamiento (~19 variables)
- Variables: `alcaldesa_*_l1`, `alcaldesa_*_l2`, `alcaldesa_*_l3`
- **Problema:** Son rezagos del tratamiento mismo. Usarlos como controles absorberían mecánicamente el efecto del tratamiento.
- **Acción:** Usar SOLO en la especificación de event study, no como controles.

### Archivo generado
- `outputs/eda/E_sesgo_leakage.csv` — 54 variables clasificadas con tipo de riesgo, razón y acción recomendada

---

## 8. Sección F — Recomendaciones

### ¿Qué se hizo?

Se compilaron **12 recomendaciones priorizadas** para las transformaciones necesarias antes del modelado causal, organizadas por urgencia:

### 🔴 CRÍTICAS (resolver antes de modelar)

| # | Categoría | Variables | Transformación |
|---|-----------|-----------|----------------|
| 1 | Normalización | `ncont_*`, `numtar_*`, `numcontcred_*` | Dividir entre `pob_adulta_m` (mujeres) o `pob_adulta_h` (hombres) × 10,000 |
| 2 | Normalización | `saldocont_*` | Dividir entre `pob_adulta_*` × 10,000 |
| 3 | Imputación | `saldoprom_*` (NULLs estructurales) | NO imputar. Filtrar con `flag_undef_saldoprom_* = 0` |
| 4 | Exclusión | Constantes (3 variables) | EXCLUIR — varianza = 0 |

### 🟡 ALTA prioridad

| # | Categoría | Variables | Transformación |
|---|-----------|-----------|----------------|
| 5 | Escala | `pob`, `pob_adulta_*` | `log(x)` como control en regresiones |
| 6 | Outliers | Outcomes per cápita | Winsorizar al p1–p99 como robustez |
| 7 | Feature eng. | `brecha_genero_*` (nueva) | Crear ratio = `outcome_m / outcome_h` |
| 8 | Feature eng. | `ever_alcaldesa` (nueva) | 1 si el municipio tuvo alcaldesa en cualquier trimestre |
| 9 | IDs | `cve_mun`, `cvegeo_mun` | Usar `cvegeo_mun` (5 dígitos, texto) para merges con INEGI |

### 🟢 Prioridad MEDIA

| # | Categoría | Variables | Transformación |
|---|-----------|-----------|----------------|
| 10 | Feature eng. | `alcaldesa_acumulado` (nueva) | Nº trimestres acumulados con alcaldesa hasta t |
| 11 | Escala | Outcomes per cápita | Evaluar `asinh(x)` o `log(1+x)` para distribuciones muy asimétricas |
| 12 | Imputación | `tipo_pob` (2 NULLs) | Asignar categoría por rango de población |

### Archivo generado
- `outputs/eda/F_recomendaciones.csv` — 12 recomendaciones con prioridad, categoría, variables, transformación y razón

---

## 9. Archivos generados

El EDA produjo **17 archivos** en `outputs/eda/`:

### CSVs (datos tabulares)
| Archivo | Contenido | Filas |
|---------|-----------|-------|
| `A_diccionario_observado.csv` | Perfil de 175 variables (dtype, NAs, stats) | 175 |
| `B_calidad_integridad.csv` | 6 pruebas de calidad con resultados | 6 |
| `B_completitud_panel.csv` | Municipios y % tratamiento por trimestre | 17 |
| `E_sesgo_leakage.csv` | 54 variables con riesgo identificado | 54 |
| `F_recomendaciones.csv` | 12 recomendaciones priorizadas | 12 |

### PNGs (visualizaciones)
| Archivo | Contenido |
|---------|-----------|
| `C1_tratamiento_por_trimestre.png` | Proporción de alcaldesas por trimestre |
| `C2_distribucion_poblacion.png` | Histogramas log de población |
| `C3_boxplot_outcomes_mujeres_pc.png` | Boxplots outcomes per cápita mujeres |
| `C4_categoricas_clave.png` | Distribución de región, tipo_pob, % alcaldesa |
| `C5_tipo_pob_tratamiento.png` | Tipo de población cruzado con tratamiento |
| `D1_outcomes_por_tratamiento.png` | 6 boxplots tratados vs control |
| `D2_brecha_genero_temporal.png` | Tendencia temporal M vs H |
| `D3_tendencia_por_tratamiento.png` | Tendencias paralelas (DiD) |
| `D4_ratio_MH_por_tratamiento.png` | Ratio M/H por tratamiento |
| `D5_correlaciones_spearman.png` | Heatmap de correlaciones |
| `D6_balance_pre_tratamiento.png` | Balance de grupos en baseline |

### Documentación
| Archivo | Contenido |
|---------|-----------|
| `00_README.md` | Resumen ejecutivo de hallazgos |

---

## 10. Conclusiones y próximos pasos

### Hallazgos principales del EDA

1. **La base de datos está limpia y bien estructurada.** Panel casi 100% balanceado, sin duplicados, sin negativos en conteos, consistencia geográfica perfecta.

2. **~22% de municipios-trimestre tienen alcaldesa.** La variación es primordialmente cross-sectional (entre municipios), con switches asociados a los ciclos electorales.

3. **894 switchers (36.2%)** proporcionan la variación necesaria para identificación causal con efectos fijos. Es un número robusto.

4. **La normalización per cápita es indispensable.** La correlación de 0.67–0.70 entre población y outcomes significa que sin normalizar, el modelo captura tamaño del municipio, no inclusión financiera.

5. **Existe una brecha de género persistente** en casi todos los productos financieros (hombres > mujeres per cápita).

6. **La diferencia cruda tratamiento-outcome es confusa.** Los municipios con alcaldesa tienden a ser más pequeños y rurales, generando un sesgo de selección negativo que los efectos fijos deben absorber.

7. **Las tendencias paralelas parecen cumplirse** visualmente para la mayoría de productos financieros, lo cual es prometedor para DiD.

8. **54 variables tienen riesgo de sesgo/leakage** y deben manejarse con cuidado (excluir, usar solo en event study, o solo para filtrar).

### Próximos pasos recomendados

1. **Crear muestra analítica** con variables per cápita, ratio M/H, y nuevas features (`ever_alcaldesa`, `alcaldesa_acumulado`)
2. **Estimar modelo TWFE** (Two-Way Fixed Effects) con efectos fijos de municipio + tiempo usando `pyfixest` o `linearmodels`
3. **Event study** con rezagos y adelantos para validación formal de tendencias paralelas
4. **Análisis de heterogeneidad** por región, tipo de población y tamaño del municipio
5. **Robustez:** excluir transiciones, winsorizar, diferentes medidas de outcome, estimadores robustos a heterogeneidad

---

## Apéndice: Herramientas técnicas utilizadas

| Componente | Herramienta | Versión |
|------------|-------------|---------|
| Base de datos | PostgreSQL | 17.8 (Homebrew) |
| Lenguaje | Python | 3.12 |
| DataFrames | pandas | 3.0.1 |
| Conexión DB | SQLAlchemy + psycopg2 | 2.0.46 |
| Visualización | matplotlib + seaborn | — |
| Entorno | VS Code + Jupyter Notebook | — |
| Reproducibilidad | Semilla `SEED = 42` | — |
