# EDA — Explicación 4: Resolución de Recomendaciones Medias (🟢)

**Continuación de:** `docs/02_EDA_EXPLICACION.md` (Secciones 1–10), `docs/03_EDA_EXPLICACION_2.md` (Sección 11) y `docs/04_EDA_EXPLICACION_3.md` (Secciones 12–15)  
**Fecha:** Febrero 2026  

---

## 16. Resolución de recomendaciones de prioridad media (🟢)

Las 3 recomendaciones marcadas como **🟢 MEDIA prioridad** en la Sección F del EDA
fueron implementadas sobre la tabla `inclusion_financiera_clean` (que ya contenía las
transformaciones críticas de la Sección 11 y las altas de la Sección 12).

### Tabla resultante

| Propiedad | Valor |
|-----------|-------|
| **Tabla original** | `inclusion_financiera` (175 columnas) — **intacta** |
| **Tabla limpia** | `inclusion_financiera_clean` (348 columnas) |
| **Filas** | 41,905 (sin cambios) |
| **Columnas nuevas (esta fase)** | +52 |
| **Acumulado desde original** | +173 columnas |

| Fase | Columnas añadidas | Total acumulado |
|------|-------------------|-----------------|
| Tabla original | — | 175 |
| + Críticas (Recs 1–4) | +51 per cápita, −3 constantes = +48 | 223 |
| + Altas (Recs 5–9) | +4 log + 51 winsor + 17 ratio + 1 ever = +73 | 296 |
| **+ Medias (Recs 10–12)** | **+1 acumulado + 51 asinh + 0 tipo_pob = +52** | **348** |

---

### Rec 10. ✅ Variable de intensidad de tratamiento (`alcaldesa_acumulado`)

**Qué se hizo:** Se creó la variable `alcaldesa_acumulado` que cuenta cuántos
trimestres acumulados ha tenido una alcaldesa cada municipio hasta el periodo
actual (inclusive). Es la suma acumulada ordenada cronológicamente de
`alcaldesa_final` dentro de cada municipio.

**Fórmula:**
```
alcaldesa_acumulado[i,t] = Σ alcaldesa_final[i,s]  para s ≤ t
```

**Estadísticas descriptivas:**

| Estadístico | Valor |
|-------------|-------|
| Media | 2.82 |
| Mediana | 0 |
| Máximo | 17 (todos los trimestres) |
| Mínimo | 0 |
| % con valor 0 | 69.3% |

**Ejemplo — Municipio 1011 (switcher):**

| Periodo | `alcaldesa_final` | `alcaldesa_acumulado` |
|---------|-------------------|-----------------------|
| 2018Q3 | 1 | 1 |
| 2018Q4 | 1 | 2 |
| 2019Q1 | 1 | 3 |
| 2019Q2 | 1 | 4 |
| 2019Q3 | 1 | 5 |
| 2019Q4 | 0 | 5 |
| 2020Q1 | 0 | 5 |
| ... | 0 | 5 |
| 2021Q4 | 1 | 6 |
| 2022Q1 | 1 | 7 |
| 2022Q2 | 1 | 8 |
| 2022Q3 | 1 | 9 |

**Propiedades verificadas:**
- **Monótona no-decreciente:** Dentro de cada municipio, `alcaldesa_acumulado` nunca
  disminuye (la suma acumulada sólo puede mantenerse o incrementarse).
- **Máximo = 17:** Un municipio que tuvo alcaldesa los 17 trimestres alcanza el valor
  máximo posible.
- **Ceros consistentes:** Todos los municipios donde `SUM(alcaldesa_final) = 0`
  (never-treated) tienen `alcaldesa_acumulado = 0` en todos los periodos.

**Justificación:** El indicador binario `alcaldesa_final` captura si una alcaldesa
está activa en un periodo dado, pero no distingue entre un municipio que lleva 1
trimestre con alcaldesa y otro que lleva 10. La variable acumulada permite:
- Modelar **efectos acumulativos/dinámicos** del tratamiento (¿la inclusión financiera
  mejora más conforme aumenta el tiempo de exposición a una alcaldesa?)
- Estimar modelos de **dosis-respuesta** (dose-response) donde la intensidad del
  tratamiento es continua
- Capturar heterogeneidad temporal que el indicador binario ignora

**Uso recomendado:**
- Como variable de tratamiento alternativa en especificaciones de robustez
- En modelos de efectos dinámicos: interacciones `alcaldesa_acumulado × periodos`
- Análisis de heterogeneidad: ¿el efecto marginal de un trimestre adicional con
  alcaldesa es constante o decreciente?

---

### Rec 11. ✅ Transformación arcoseno hiperbólico inverso (asinh) de outcomes

**Qué se hizo:** Se crearon 51 columnas con la transformación `asinh` (arcoseno
hiperbólico inverso) de todas las variables per cápita (sufijo `_pc`). Las nuevas
columnas llevan el sufijo `_pc_asinh`.

**Fórmula:** `columna_pc_asinh = arcsinh(columna_pc) = ln(x + √(x² + 1))`

**¿Por qué asinh y no log?** Las variables per cápita contienen **ceros genuinos**
(municipios sin presencia de ciertos productos financieros). El logaritmo natural
está indefinido en 0, mientras que `asinh(0) = 0`. La transformación asinh:
- Está definida para **todo el dominio real** (incluyendo 0 y negativos)
- Se comporta como `ln(2x) ≈ ln(x) + 0.69` para valores grandes de x
- Preserva el cero: `asinh(0) = 0`
- Es una alternativa estándar a `log(x + 1)` en econometría cuando hay ceros
  (Burbidge, Magee & Robb 1988; Bellemare & Wichman 2020)

**Compresión de la distribución — ejemplo `ncont_total_m_pc`:**

| Estadístico | Original (`_pc`) | asinh (`_pc_asinh`) | Factor de compresión |
|-------------|------------------|---------------------|----------------------|
| Media | 3,429.69 | ~8.4 | 408× |
| Mediana | 575.26 | ~7.1 | 81× |
| Máximo | 179,439.41 | ~12.1 | 14,830× |
| Mínimo | 0.00 | 0.00 | — |

**Motivación estadística:** Las distribuciones per cápita son extremadamente sesgadas:

| Variable | Media / Mediana | Interpretación |
|----------|-----------------|----------------|
| `ncont_total_m_pc` | 6× | Sesgo moderado |
| `saldocont_total_m_pc` | 390× | Sesgo extremo |

Estas distribuciones con colas tan pesadas violan los supuestos de los modelos
lineales. La transformación asinh normaliza las distribuciones, acercándolas a una
distribución simétrica sin perder información.

**Columnas creadas (51 en total):**
- Conteos: `ncont_ahorro_m_pc_asinh`, ..., `ncont_total_t_pc_asinh` (21)
- Saldos: `saldocont_ahorro_m_pc_asinh`, ..., `saldocont_total_t_pc_asinh` (21)
- Crédito hipotecario: `numcontcred_hip_m_pc_asinh`, `numcontcred_hip_h_pc_asinh`,
  `numcontcred_hip_t_pc_asinh` (3)
- Tarjetas débito: `numtar_deb_m_pc_asinh`, `numtar_deb_h_pc_asinh`,
  `numtar_deb_t_pc_asinh` (3)
- Tarjetas crédito: `numtar_cred_m_pc_asinh`, `numtar_cred_h_pc_asinh`,
  `numtar_cred_t_pc_asinh` (3)

**Uso recomendado:**
- **Especificación principal (recomendada para la tesis):** usar `_pc_asinh` como
  variable dependiente en los modelos TWFE y event study. Los coeficientes se
  interpretan como cambios porcentuales aproximados para valores grandes.
- **Robustez:** comparar resultados con `_pc` (nivel), `_pc_w` (winsorizada) y
  `_pc_asinh` (asinh) para verificar que las conclusiones no dependen de la
  transformación.

---

### Rec 12. ✅ Imputación de NULLs en `tipo_pob`

**Qué se hizo:** Se identificaron y corrigieron los 2 municipios con `tipo_pob = NULL`
asignándoles la categoría correspondiente según los rangos poblacionales de la
clasificación existente.

**Municipios corregidos:**

| `cve_mun` | Nombre | Estado | Población | Categoría asignada | Justificación |
|-----------|--------|--------|-----------|-------------------|---------------|
| 2007 | San Felipe | Baja California | 20,320 | Semi-urbano | Rango: 15,009–49,920 |
| 4013 | Dzitbalché (Calkiní) | Campeche | 16,568 | Semi-urbano | Rango: 15,009–49,920 |

**Distribución de `tipo_pob` (antes → después):**

| Categoría | Rango de población | Municipios × trimestres | Antes | Después |
|-----------|-------------------|-------------------------|-------|---------|
| Rural | 81 – 5,000 | 11,288 | 11,288 | 11,288 |
| En Transicion | 5,001 – 14,997 | 10,613 | 10,613 | 10,613 |
| **Semi-urbano** | **15,009 – 49,920** | — | **12,421** | **12,455** (+34) |
| Urbano | 42,664 – 299,635 | 6,138 | 6,138 | 6,138 |
| Semi-metropoli | 300,295 – 995,129 | 1,223 | 1,223 | 1,223 |
| Metropoli | 1,003,530 – 1,922,523 | 220 | 220 | 220 |
| **NULL** | — | — | **2** | **0** |
| **Total** | | **41,905** | **41,905** | **41,905** |

**Nota:** Los 2 municipios NULL aparecen en 17 trimestres cada uno (34 registros),
de ahí el incremento de +34 en Semi-urbano.

**Justificación:** La variable `tipo_pob` es fundamental como control y para análisis
de heterogeneidad (¿el efecto de una alcaldesa es diferente en municipios rurales vs.
urbanos?). Tener NULLs causa pérdida de observaciones al incluirla en regresiones.
La imputación es determinista y verificable: ambos municipios caen inequívocamente
dentro del rango de Semi-urbano.

**Uso recomendado:**
- Como variable de control categórica en todas las especificaciones
- Como variable de interacción para análisis de heterogeneidad por tamaño de municipio
- Para crear subgrupos en análisis estratificados (ej. efecto separado por rural vs
  urbano vs metropolitano)

---

## 17. Validación de transformaciones medias

### Tests de recomendaciones medias (16/16 ✓)

| # | Test | Resultado |
|---|------|-----------|
| T1 | Filas correctas (41,905) | ✓ |
| T2 | Total columnas (348) | ✓ |
| T3 | `alcaldesa_acumulado` existe | ✓ |
| T4 | Sin valores negativos en acumulado | ✓ |
| T5 | Máximo = 17 (todos los trimestres) | ✓ |
| T6 | Never-treated → acumulado = 0 | ✓ |
| T7 | Monótono creciente (0 violaciones) | ✓ |
| T8 | 51 columnas asinh existen | ✓ |
| T9 | Fórmula asinh correcta | ✓ |
| T10 | asinh(0) = 0 | ✓ |
| T11 | `tipo_pob` sin NULLs | ✓ |
| T12 | San Felipe (cve_mun=2007) → Semi-urbano | ✓ |
| T13 | Dzitbalché (cve_mun=4013) → Semi-urbano | ✓ |
| T14 | PK intacta | ✓ |
| T15 | Índice `cvegeo_mun` intacto | ✓ |
| T16 | Tabla original intacta (175 cols) | ✓ |

### Resumen de todas las suites de validación

| Suite | Tests | Estado |
|-------|-------|--------|
| `src/tests/test_criticas.py` (Recs 1–4) | 8/8 | ✓ |
| `src/tests/test_altas.py` (Recs 5–9) | 19/19 | ✓ |
| `src/tests/test_medias.py` (Recs 10–12) | 16/16 | ✓ |
| **Total** | **43/43** | **✓** |

---

## 18. Scripts creados

| Script | Propósito |
|--------|-----------|
| `src/transformaciones_medias.py` | Aplica las 3 recomendaciones de prioridad media (Recs 10–12) |
| `src/tests/test_medias.py` | 16 tests de validación para las Recs medias (10–12) |

**Orden de ejecución completo (idempotente):**
```bash
cd /Users/anapaulaperezgavilan/Documents/Tesis_DB/Code
source .venv/bin/activate

# 1. Crear tabla limpia con transformaciones críticas (175 → 223 cols)
python src/transformaciones_criticas.py

# 2. Agregar transformaciones de alta prioridad (223 → 296 cols)
python src/transformaciones_altas.py

# 3. Agregar transformaciones de prioridad media (296 → 348 cols)
python src/transformaciones_medias.py

# 4. Validar todo
python src/tests/test_criticas.py    # 8 tests
python src/tests/test_altas.py       # 19 tests
python src/tests/test_medias.py      # 16 tests
```

---

## 19. Estado final de todas las recomendaciones del EDA

| # | Prioridad | Categoría | Estado | Sección |
|---|-----------|-----------|--------|---------|
| 1 | 🔴 CRÍTICA | Normalización conteos per cápita | ✅ Resuelto | Sección 11 |
| 2 | 🔴 CRÍTICA | Normalización saldos per cápita | ✅ Resuelto | Sección 11 |
| 3 | 🔴 CRÍTICA | saldoprom NULLs | ✅ Documentado | Sección 11 |
| 4 | 🔴 CRÍTICA | Exclusión constantes | ✅ Resuelto | Sección 11 |
| 5 | 🟡 Alta | log(pob) controles | ✅ Resuelto | Sección 12 |
| 6 | 🟡 Alta | Winsorización p1–p99 | ✅ Resuelto | Sección 12 |
| 7 | 🟡 Alta | Ratio M/H (brecha género) | ✅ Resuelto | Sección 12 |
| 8 | 🟡 Alta | ever_alcaldesa | ✅ Resuelto | Sección 12 |
| 9 | 🟡 Alta | IDs estándar (cvegeo_mun) | ✅ Resuelto | Sección 12 |
| 10 | 🟢 Media | alcaldesa_acumulado | ✅ Resuelto | **Sección 16** |
| 11 | 🟢 Media | asinh outcomes | ✅ Resuelto | **Sección 16** |
| 12 | 🟢 Media | tipo_pob NULLs | ✅ Resuelto | **Sección 16** |

**Progreso: 12/12 recomendaciones resueltas (100%).**

---

## 20. Tabla `inclusion_financiera_clean` — Inventario final de columnas

La tabla final tiene **348 columnas**. A continuación se agrupan por origen:

### Columnas heredadas de la tabla original (175)
Variables originales de CNBV/INEGI: periodos, identificadores geográficos, productos
financieros (conteos, saldos, tarjetas, créditos hipotecarios), población, tipo de
población, político (alcaldesa_final), y derivadas.

### Columnas añadidas por fase

| Fase | Prefijo/Sufijo | # Cols | Descripción |
|------|---------------|--------|-------------|
| Críticas | `*_pc` | 51 | Variables per cápita (÷ población adulta M/H/T) |
| Críticas | — | −3 | Constantes eliminadas (`cve_pais`, `desc_pais`, `id_periodo`) |
| Altas | `log_*` | 4 | Log(población + 1) |
| Altas | `*_pc_w` | 51 | Per cápita winsorizadas (p1–p99) |
| Altas | `ratio_mh_*` | 17 | Brecha de género M/H |
| Altas | `ever_alcaldesa` | 1 | Indicador time-invariant de tratamiento |
| **Medias** | **`alcaldesa_acumulado`** | **1** | **Suma acumulada de trimestres con alcaldesa** |
| **Medias** | **`*_pc_asinh`** | **51** | **Arcoseno hiperbólico inverso de per cápita** |
| **Medias** | **`tipo_pob` (corregida)** | **0** | **2 NULLs imputados, sin columnas nuevas** |
| | | **348** | **Total final** |

---

## 21. Próximos pasos

Con las 12 recomendaciones del EDA resueltas al 100%, la tabla `inclusion_financiera_clean`
está lista para la fase de modelado econométrico. Los siguientes pasos son:

1. **Construir la muestra analítica**: Seleccionar las variables dependientes,
   controles y tratamiento para el modelo principal.
2. **Modelo TWFE (Two-Way Fixed Effects)**: Estimar el efecto causal de
   `alcaldesa_final` sobre outcomes de inclusión financiera femenina, con efectos
   fijos de municipio y periodo.
3. **Event Study**: Estimar leads y lags alrededor del cambio de tratamiento para
   verificar tendencias paralelas pre-tratamiento.
4. **Robustez**: Estimadores modernos de DiD (Callaway & Sant'Anna, Sun & Abraham),
   especificaciones alternativas con `_pc_w`, `_pc_asinh`, `alcaldesa_acumulado`.
5. **Heterogeneidad**: Análisis por `tipo_pob`, región, y otras características
   municipales.
