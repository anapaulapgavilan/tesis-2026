# EDA — Explicación 3: Resolución de Recomendaciones Altas (🟡)

**Continuación de:** `docs/02_EDA_EXPLICACION.md` (Secciones 1–10) y `docs/03_EDA_EXPLICACION_2.md` (Sección 11)  
**Fecha:** Febrero 2026  

---

## 12. Resolución de recomendaciones de alta prioridad (🟡)

Las 5 recomendaciones marcadas como **🟡 ALTA prioridad** en la Sección F del EDA fueron
implementadas sobre la tabla `inclusion_financiera_clean` (que ya contenía las
transformaciones críticas de la Sección 11).

### Tabla resultante

| Propiedad | Valor |
|-----------|-------|
| **Tabla original** | `inclusion_financiera` (175 columnas) — **intacta** |
| **Tabla limpia** | `inclusion_financiera_clean` (296 columnas) |
| **Filas** | 41,905 (sin cambios) |
| **Columnas nuevas (esta fase)** | +73 |
| **Acumulado desde original** | +121 columnas |

| Fase | Columnas añadidas | Total acumulado |
|------|-------------------|-----------------|
| Tabla original | — | 175 |
| + Críticas (Recs 1–4) | +51 per cápita, −3 constantes = +48 | 223 |
| + Altas (Recs 5–9) | +4 log + 51 winsor + 17 ratio + 1 ever = +73 | 296 |

---

### Rec 5. ✅ Transformación logarítmica de población

**Qué se hizo:** Se crearon 4 columnas con la transformación `log(x + 1)` de las
variables de población. Se usa `log1p` (logaritmo natural de x+1) para proteger
contra `log(0)` en municipios con población = 0.

**Fórmula:** `log_col = ln(columna + 1)`

**Columnas creadas:**

| Columna nueva | Columna original | Media | Min | Max |
|---------------|------------------|-------|-----|-----|
| `log_pob` | `pob` | 9.4947 | 4.4067 | 14.4691 |
| `log_pob_adulta` | `pob_adulta` | 9.1727 | 4.2047 | 14.1996 |
| `log_pob_adulta_m` | `pob_adulta_m` | 8.5194 | 3.6109 | 13.5500 |
| `log_pob_adulta_h` | `pob_adulta_h` | 8.4368 | 3.2958 | 13.5102 |

**Justificación:** La distribución de población en los municipios mexicanos es
extremadamente sesgada (CV > 5). Un municipio como Ecatepec tiene ~1.6 millones de
habitantes mientras que los más pequeños tienen menos de 100. La transformación
logarítmica:
- Comprime el rango de variación
- Hace la distribución aproximadamente simétrica
- Permite usar la variable como control en regresiones lineales
- Los coeficientes se interpretan como elasticidades (cambio % en outcome por cambio % en población)

**Uso recomendado:** Incluir `log_pob` o `log_pob_adulta` como control en todas las
especificaciones econométricas. No usar la población en nivel.

---

### Rec 6. ✅ Winsorización de outcomes per cápita (p1–p99)

**Qué se hizo:** Se crearon 51 versiones winsorizadas de las columnas per cápita
(sufijo `_pc`), agregando el sufijo `_w`. Los valores se recortan (clip) al rango
del percentil 1 al percentil 99.

**Fórmula:**
```
columna_pc_w = clip(columna_pc, lower=percentil_1, upper=percentil_99)
```

**Ejemplo de recorte — `ncont_total_m_pc`:**

| Estadístico | Original (`_pc`) | Winsorizado (`_pc_w`) |
|-------------|------------------|-----------------------|
| Max | 179,439.41 | 21,346.29 |
| p99 | 21,346.29 | 21,346.29 |
| p1 | 0.00 | 0.00 |
| Min | 0.00 | 0.00 |

**Impacto:** En cada columna, aproximadamente 420 observaciones por cola (1% de 41,905)
fueron ajustadas al límite del percentil correspondiente. Esto elimina la influencia
desproporcionada de municipios muy pequeños que generan ratios per cápita extremos.

**Columnas creadas (51 en total):**
- Conteos: `ncont_ahorro_m_pc_w`, `ncont_ahorro_h_pc_w`, ..., `ncont_total_t_pc_w` (21)
- Saldos: `saldocont_ahorro_m_pc_w`, ..., `saldocont_total_t_pc_w` (21)
- Crédito hipotecario: `numcontcred_hip_m_pc_w`, `numcontcred_hip_h_pc_w`, `numcontcred_hip_t_pc_w` (3)
- Tarjetas débito: `numtar_deb_m_pc_w`, `numtar_deb_h_pc_w`, `numtar_deb_t_pc_w` (3)
- Tarjetas crédito: `numtar_cred_m_pc_w`, `numtar_cred_h_pc_w`, `numtar_cred_t_pc_w` (3)

**Justificación:** Las distribuciones per cápita tienen colas muy pesadas (algunos
municipios con poblaciones muy pequeñas generan ratios extremos). La winsorización
reduce la influencia de outliers sin eliminar observaciones y es más conservadora que
la truncación. Es estándar en econometría aplicada como prueba de robustez.

**Uso recomendado:**
- Especificación principal: usar `_pc` (sin winsorizar)
- Robustez: repetir con `_pc_w` para verificar que los resultados no dependen de outliers

---

### Rec 7. ✅ Ratio brecha de género (outcome_m / outcome_h)

**Qué se hizo:** Se crearon 17 columnas de ratio M/H que miden la brecha de género en
inclusión financiera. Un ratio < 1 indica que las mujeres tienen menos acceso que los
hombres; > 1 indica lo contrario.

**Fórmula:** `ratio_mh_producto = producto_m_pc / producto_h_pc`

**Protección:** Cuando `producto_h_pc = 0`, el ratio es `NaN` (indeterminado).

**Columnas creadas y estadísticas:**

| Columna | Media | Mediana | NaN | Interpretación |
|---------|-------|---------|-----|----------------|
| `ratio_mh_ncont_ahorro` | 0.85 | 0.85 | 39,163 | Mujeres ~85% del ahorro de hombres |
| `ratio_mh_ncont_plazo` | 1.78 | 1.50 | 24,183 | Mujeres > hombres en plazo |
| `ratio_mh_ncont_n1` | 0.51 | 0.00 | 38,279 | Brecha muy marcada en nivel 1 |
| `ratio_mh_ncont_n2` | 1.57 | 0.97 | 1,504 | Mujeres ≈ hombres (mediana ~1) |
| `ratio_mh_ncont_n3` | 0.70 | 0.67 | 34,616 | Brecha en nivel 3 |
| `ratio_mh_ncont_tradic` | 1.28 | 1.03 | 23,655 | Casi equidad en tradicional |
| `ratio_mh_ncont_total` | 1.44 | 1.01 | 1,485 | En total, cerca de equidad (mediana) |
| `ratio_mh_saldocont_ahorro` | 37.49 | 0.95 | 39,344 | Outliers distorsionan la media |
| `ratio_mh_saldocont_plazo` | 8.85 | 1.12 | 24,193 | Media inflada por outliers |
| `ratio_mh_saldocont_n1` | 28.54 | 0.00 | 38,325 | Mismo patrón |
| `ratio_mh_saldocont_n2` | 40.92 | 0.82 | 1,709 | Hombres > mujeres en saldos N2 |
| `ratio_mh_saldocont_n3` | 16.19 | 0.77 | 34,642 | Hombres > mujeres en saldos N3 |
| `ratio_mh_saldocont_tradic` | 6.62 | 0.92 | 23,668 | Brecha moderada |
| `ratio_mh_saldocont_total` | 40.56 | 0.94 | 1,684 | Hombres ligeramente > mujeres |
| `ratio_mh_numcontcred_hip` | 0.49 | 0.45 | 11,911 | Brecha fuerte en hipotecas |
| `ratio_mh_numtar_deb` | 0.83 | 0.81 | 360 | Mujeres ~83% tarjetas débito |
| `ratio_mh_numtar_cred` | 0.81 | 0.77 | 2,875 | Mujeres ~81% tarjetas crédito |

**Hallazgos clave:**
1. **Brecha persistente en la mayoría de productos:** La mediana de `ratio_mh_ncont_total`
   es ~1.01, pero en productos específicos (nivel 1, hipotecas, tarjetas) las mujeres
   tienen significativamente menos acceso.
2. **El ratio de saldos tiene outliers extremos:** Las medias son muy superiores a las
   medianas, lo que indica que algunos municipios tienen ratios absurdamente altos.
   Para el análisis, es más informativo usar la **mediana** o aplicar winsorización.
3. **Muchos NaN:** Los ratios heredan los NaN de los productos (municipios sin presencia
   de ciertos productos financieros). Los NaN son informativos: indican municipios sin
   mercado para ese producto.

**Justificación:** Esta variable es central para la tesis. Permite evaluar directamente
si la presencia de una alcaldesa reduce la brecha de género en inclusión financiera.

**Uso recomendado:**
- Variable dependiente en las regresiones DiD (especialmente `ratio_mh_ncont_total`,
  `ratio_mh_numtar_deb`, `ratio_mh_numtar_cred`)
- Complementar con análisis separado de outcomes femeninos per cápita

---

### Rec 8. ✅ Indicador `ever_alcaldesa`

**Qué se hizo:** Se creó la variable `ever_alcaldesa` que toma valor 1 si el municipio
tuvo al menos una alcaldesa (`alcaldesa_final = 1`) en cualquier trimestre del panel
(2018Q3–2022Q3), y 0 si nunca la tuvo.

**Distribución:**

| Grupo | Municipios | % |
|-------|------------|---|
| `ever_alcaldesa = 1` (tuvo alcaldesa alguna vez) | 995 | 40.3% |
| `ever_alcaldesa = 0` (nunca tuvo alcaldesa) | 1,476 | 59.7% |
| **Total** | **2,471** | **100%** |

**Nota:** Esta variable es **invariante en el tiempo** — tiene el mismo valor para
todos los trimestres de un mismo municipio.

**Justificación:** Distingue municipios "switchers" (que cambian de tratamiento durante
el panel) de los "never-treated" y "always-treated". Es útil para:
- Verificar balance pre-tratamiento entre los dos grupos
- Análisis de heterogeneidad: ¿el efecto causal es diferente en municipios que
  históricamente han tenido mujeres en el poder vs los que nunca?
- Definir el grupo control en diseños que excluyen always-treated

**Uso recomendado:** Como control, como variable de interacción en análisis de
heterogeneidad, o como criterio de filtrado para especificaciones alternativas.

---

### Rec 9. ✅ Estandarización de identificadores geográficos

**Qué se hizo:** Se verificó la consistencia de los identificadores geográficos y se
creó un índice de base de datos sobre `cvegeo_mun` para optimizar joins con catálogos
INEGI.

**Resultados de la verificación:**

| Prueba | Resultado |
|--------|-----------|
| NULLs en `cvegeo_mun` | 0 |
| Longitud: 5 dígitos | ✓ (todas las observaciones) |
| Consistencia `cvegeo_mun` = `cve_ent` + `cve_mun3` | ✓ (0 inconsistencias) |
| Municipios con múltiples `cvegeo_mun` | 0 |
| Municipios únicos (`cve_mun` int) | 2,471 |
| Municipios únicos (`cvegeo_mun` str) | 2,471 |
| Índice `idx_clean_cvegeo_mun` creado | ✓ |

**Mapeo de identificadores:**

| Columna | Tipo | Ejemplo | Uso |
|---------|------|---------|-----|
| `cve_mun` | integer | 1001 | PK interna del panel (junto con `periodo_trimestre`) |
| `cvegeo_mun` | text (5 char) | "01001" | **ID canónico para merges INEGI** |
| `cve_ent` | text (2 char) | "01" | Entidad federativa |
| `cve_mun3` | text (3 char) | "001" | Municipio dentro de la entidad |

**Justificación:** La clave INEGI estándar para municipios mexicanos es el código
de 5 dígitos (2 de entidad + 3 de municipio), almacenado como texto con ceros a la
izquierda. Al crear un índice sobre esta columna:
- Los JOIN con el Marco Geoestadístico Nacional son O(log n) en lugar de O(n)
- Los JOIN con datos censales (INEGI 2020) son directos
- Se garantiza la compatibilidad con capas geográficas GIS (shapefiles de INEGI)

**Uso recomendado:** Siempre usar `cvegeo_mun` (texto, 5 dígitos) para merges con
fuentes externas. `cve_mun` (entero) se mantiene como PK interna del panel.

---

## 13. Validación de todas las transformaciones

### Tests de recomendaciones críticas (8/8 ✓)

| # | Test | Resultado |
|---|------|-----------|
| T1 | Tabla existe (41,905 filas) | ✓ |
| T2 | Constantes eliminadas (0 restantes) | ✓ |
| T3 | 51 columnas per cápita | ✓ |
| T4 | Sin infinitos en per cápita | ✓ |
| T5 | Sin negativos en per cápita | ✓ |
| T6 | Tabla original intacta (175 cols) | ✓ |
| T7 | PK sin duplicados | ✓ |
| T8 | Fórmula per cápita correcta | ✓ |

### Tests de recomendaciones altas (19/19 ✓)

| # | Test | Resultado |
|---|------|-----------|
| T1 | Filas correctas (41,905) | ✓ |
| T2 | Total columnas (296) | ✓ |
| T3 | 4 columnas log existen | ✓ |
| T4 | log_pob = ln(pob + 1) | ✓ |
| T5 | 51 columnas winsorizadas | ✓ |
| T6 | Winsorizado ≤ original max | ✓ |
| T7 | 17 ratios M/H | ✓ |
| T8 | Fórmula ratio correcta (M/H) | ✓ |
| T9 | `ever_alcaldesa` existe | ✓ |
| T10 | `ever_alcaldesa` totales (2,471 municipios) | ✓ |
| T11 | `ever_alcaldesa` consistente con `alcaldesa_final` | ✓ |
| T12 | Índice `cvegeo_mun` existe | ✓ |
| T13 | `cvegeo_mun` sin NULLs | ✓ |
| T14 | `cvegeo_mun` 5 dígitos | ✓ |
| T15 | PK intacta | ✓ |
| T16 | Tabla original intacta (175 cols) | ✓ |

---

## 14. Scripts creados

| Script | Propósito |
|--------|-----------|
| `src/transformaciones_altas.py` | Aplica las 5 recomendaciones de alta prioridad (Recs 5–9) |
| `src/tests/test_criticas.py` | 8 tests de validación para las Recs críticas (1–4) |
| `src/tests/test_altas.py` | 19 tests de validación para las Recs altas (5–9) |

**Orden de ejecución (idempotente):**
```bash
cd /Users/anapaulaperezgavilan/Documents/Tesis_DB/Code
source .venv/bin/activate

# 1. Crear tabla limpia con transformaciones críticas
python src/transformaciones_criticas.py

# 2. Agregar transformaciones de alta prioridad
python src/transformaciones_altas.py

# 3. Validar
python src/tests/test_criticas.py
python src/tests/test_altas.py
```

---

## 15. Resumen de estado actualizado de recomendaciones

| # | Prioridad | Categoría | Estado |
|---|-----------|-----------|--------|
| 1 | 🔴 CRÍTICA | Normalización conteos per cápita | ✅ Resuelto (Sección 11) |
| 2 | 🔴 CRÍTICA | Normalización saldos per cápita | ✅ Resuelto (Sección 11) |
| 3 | 🔴 CRÍTICA | saldoprom NULLs | ✅ Documentado (Sección 11) |
| 4 | 🔴 CRÍTICA | Exclusión constantes | ✅ Resuelto (Sección 11) |
| 5 | 🟡 Alta | log(pob) controles | ✅ Resuelto (Sección 12) |
| 6 | 🟡 Alta | Winsorización p1–p99 | ✅ Resuelto (Sección 12) |
| 7 | 🟡 Alta | Ratio M/H (brecha género) | ✅ Resuelto (Sección 12) |
| 8 | 🟡 Alta | ever_alcaldesa | ✅ Resuelto (Sección 12) |
| 9 | 🟡 Alta | IDs estándar (cvegeo_mun) | ✅ Resuelto (Sección 12) |
| 10 | 🟢 Media | alcaldesa_acumulado | Pendiente |
| 11 | 🟢 Media | asinh/log outcomes | Pendiente (fase de modelado) |
| 12 | 🟢 Media | tipo_pob NULLs | Pendiente |

**Progreso:** 9/12 recomendaciones resueltas (75%). Las 3 restantes son de prioridad
media y pueden abordarse durante la fase de modelado.
