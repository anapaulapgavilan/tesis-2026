# EDA — Explicación 2: Resolución de Recomendaciones Críticas (🔴)

**Continuación de:** `docs/02_EDA_EXPLICACION.md` (Secciones 1–10)  
**Fecha:** Febrero 2026  

---

## 11. Resolución de recomendaciones críticas (🔴)

Las 4 recomendaciones marcadas como **🔴 CRÍTICAS** en la Sección F del EDA fueron implementadas
y aplicadas sobre una **copia** de la tabla original. La tabla original `inclusion_financiera`
**NO fue modificada**.

### Tabla resultante

| Propiedad | Valor |
|-----------|-------|
| **Tabla original** | `inclusion_financiera` (175 columnas) — **intacta** |
| **Tabla limpia** | `inclusion_financiera_clean` (223 columnas) |
| **Filas** | 41,905 (sin cambios) |
| **Columnas nuevas (per cápita)** | +51 |
| **Columnas eliminadas (constantes)** | −3 |
| **Diferencia neta** | +48 columnas |

---

### Rec 1. ✅ Normalización per cápita de conteos (`ncont_*`, `numtar_*`, `numcontcred_*`)

**Qué se hizo:** Se crearon 30 columnas nuevas con sufijo `_pc` que dividen cada conteo
de contratos/tarjetas entre la población adulta correspondiente y multiplican por 10,000.

**Fórmula:** `columna_pc = (columna_original × 10,000) / pob_adulta_*`

**Mapeo de sufijos demográficos:**
| Sufijo original | Denominador | Significado |
|-----------------|-------------|-------------|
| `_m` | `pob_adulta_m` | Mujeres |
| `_h` | `pob_adulta_h` | Hombres |
| `_t` | `pob_adulta` | Total |
| `_pm` | — (no se normaliza) | Persona moral (empresas, sin denominador poblacional) |

**Protección contra ÷0:** Los municipios con `pob_adulta = 0` reciben `NaN` en la columna
per cápita (no se generan infinitos ni errores).

**Columnas per cápita creadas (conteos):**
- `ncont_ahorro_m_pc`, `ncont_ahorro_h_pc`, `ncont_ahorro_t_pc`
- `ncont_plazo_m_pc`, `ncont_plazo_h_pc`, `ncont_plazo_t_pc`
- `ncont_n1_m_pc`, `ncont_n1_h_pc`, `ncont_n1_t_pc`
- `ncont_n2_m_pc`, `ncont_n2_h_pc`, `ncont_n2_t_pc`
- `ncont_n3_m_pc`, `ncont_n3_h_pc`, `ncont_n3_t_pc`
- `ncont_tradic_m_pc`, `ncont_tradic_h_pc`, `ncont_tradic_t_pc`
- `ncont_total_m_pc`, `ncont_total_h_pc`, `ncont_total_t_pc`
- `numtar_deb_m_pc`, `numtar_deb_h_pc`, `numtar_deb_t_pc`
- `numtar_cred_m_pc`, `numtar_cred_h_pc`, `numtar_cred_t_pc`
- `numcontcred_hip_m_pc`, `numcontcred_hip_h_pc`, `numcontcred_hip_t_pc`

**Estadísticas de validación (columnas clave):**
| Columna | Media | Min | Max | NaNs |
|---------|-------|-----|-----|------|
| `ncont_total_m_pc` | 3,429.69 | 0.00 | 179,439.41 | 0 |
| `ncont_ahorro_m_pc` | 6.19 | 0.00 | 3,515.38 | 0 |
| `numtar_deb_m_pc` | 3,515.54 | 0.00 | 2,839,565.83 | 0 |

---

### Rec 2. ✅ Normalización per cápita de saldos (`saldocont_*`)

**Qué se hizo:** Se crearon 21 columnas nuevas con sufijo `_pc` para los saldos de
captación, usando la misma fórmula y mapeo de denominadores que los conteos.

**Columnas creadas:** `saldocont_ahorro_m_pc`, `saldocont_ahorro_h_pc`, ...,
`saldocont_total_t_pc` (21 en total; las `_pm` no se normalizan).

---

### Rec 3. ✅ Documentación de `saldoprom_*` (NULLs estructurales — NO imputar)

**Qué se hizo:** Se documentó la distribución de NULLs en las 28 columnas `saldoprom_*`.
NO se imputaron porque los NULLs son el resultado correcto: cuando un municipio no tiene
contratos de un producto, el saldo promedio es indefinido (÷0).

**Distribución de NULLs en `saldoprom_*`:**
| Variable | NULLs | % NULL | Interpretación |
|----------|-------|--------|----------------|
| `saldoprom_ahorro_m` | 39,267 | 93.7% | Mayoría de municipios no tienen ahorro formal |
| `saldoprom_n1_m` | 40,586 | 96.9% | Productos nivel 1 son escasos |
| `saldoprom_n2_m` | 1,118 | 2.7% | Productos nivel 2 son los más comunes |
| `saldoprom_total_m` | 1,102 | 2.6% | Solo 2.6% sin dato total |
| `saldoprom_plazo_m` | 24,231 | 57.8% | ~58% sin depósitos a plazo |

**Acción recomendada (sin cambios):** Usar los flags existentes `flag_undef_saldoprom_*`
para filtrar la muestra analítica:
- `flag = 0` → margen **intensivo** (solo municipios con contratos, saldo promedio definido)
- `flag = 1` → municipio sin contratos de ese producto (saldo promedio = indefinido)

---

### Rec 4. ✅ Exclusión de columnas constantes

**Qué se hizo:** Se eliminaron 3 columnas que tienen varianza = 0 (el mismo valor en
todas las 41,905 observaciones):

| Columna eliminada | Valor constante | Por qué es constante |
|-------------------|-----------------|----------------------|
| `hist_state_available` | 1 | Todos los estados tienen historia disponible |
| `missing_quarters_alcaldesa` | 0 | Ningún municipio tiene trimestres faltantes de alcaldesa |
| `ok_panel_completo_final` | 1 | Todos los municipios pasan el filtro de completitud |

Estas columnas serían automáticamente eliminadas por colinealidad en cualquier regresión,
pero se eliminan explícitamente para mantener la tabla limpia.

---

### Script de transformaciones

El script que ejecuta todas las transformaciones se encuentra en:
`src/transformaciones_criticas.py`

**Uso:**
```bash
cd /Users/anapaulaperezgavilan/Documents/Tesis_DB/Code
source .venv/bin/activate
python src/transformaciones_criticas.py
```

El script es **idempotente**: puede re-ejecutarse sin problemas (elimina y recrea la tabla limpia).

---

### Resumen de estado de recomendaciones

| # | Prioridad | Categoría | Estado |
|---|-----------|-----------|--------|
| 1 | 🔴 CRÍTICA | Normalización conteos | ✅ Resuelto |
| 2 | 🔴 CRÍTICA | Normalización saldos | ✅ Resuelto |
| 3 | 🔴 CRÍTICA | saldoprom NULLs | ✅ Documentado (no requiere cambio) |
| 4 | 🔴 CRÍTICA | Exclusión constantes | ✅ Resuelto |
| 5 | 🟡 Alta | log(pob) | Pendiente (fase de modelado) |
| 6 | 🟡 Alta | Winsorización | Pendiente (fase de modelado) |
| 7 | 🟡 Alta | Ratio M/H | Pendiente |
| 8 | 🟡 Alta | ever_alcaldesa | Pendiente |
| 9 | 🟡 Alta | IDs estándar | Pendiente |
| 10 | 🟢 Media | alcaldesa_acumulado | Pendiente |
| 11 | 🟢 Media | asinh/log outcomes | Pendiente (fase de modelado) |
| 12 | 🟢 Media | tipo_pob NULLs | Pendiente |
