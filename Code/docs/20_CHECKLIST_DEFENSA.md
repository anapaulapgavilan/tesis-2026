# 20 — Checklist Final para Defensa de Tesis

> Versión actualizada de `16_CHECKLIST_PARA_DEFENSA.md` con todos los
> entregables (incluida robustez de ventana y apéndice).

---

## 1. Análisis empírico — Estado

| # | Componente | Estado | Script | Output principal |
|---|---|---|---|---|
| 1 | Descriptivos pre-tratamiento | ✅ | `models/01_table1_descriptives.py` | `tabla_1_descriptiva.*` |
| 2 | TWFE baseline (5 outcomes) | ✅ | `models/02_twfe.py` | `tabla_2_twfe.*` |
| 3 | Event study + pre-trends | ✅ | `models/03_event_study.py` | `figura_1_event_study.pdf` |
| 4 | Robustez (log1p, winsor, excl. trans., placebo) | ✅ | `models/04_robustness.py` | `tabla_3_robustez.*` |
| 5 | Heterogeneidad (tipo_pob, terciles) + BH | ✅ | `models/05_heterogeneity.py` | `tabla_4_heterogeneidad.*` |
| 6 | Stacked DiD (ATT + dinámico) | ✅ | `did_moderno/run_stacked_did.py` | `tabla_5_did_moderno.csv` |
| 7 | MDES / poder estadístico | ✅ | `mdes_power.py` | `tabla_6_mdes.*` |
| 8 | Sensibilidad event study (bin extremo) | ✅ | `event_study_sensitivity.py` | `figura_2_*.pdf` |
| 9 | Sample policy (main vs full) | ✅ | `sample_policy.py` | `sample_sensitivity.txt` |
| 10 | Extensivo + composición | ✅ | `extensive_margin.py` | `tabla_7_extensive.*` |
| **11** | **Robustez de ventana (Stacked DiD)** | ✅ | `did_moderno/window_robustness.py` | `tabla_A1_window_robustness.csv` |

---

## 2. Tablas y figuras — Cuerpo principal

| ID | Contenido | Archivo |
|---|---|---|
| Tabla 1 | Estadísticas descriptivas pre-tratamiento | `tabla_1_descriptiva.tex` |
| Tabla 2 | TWFE baseline (5 outcomes, asinh) | `tabla_2_twfe.tex` |
| Tabla 3 | Pruebas de robustez | `tabla_3_robustez.tex` |
| Tabla 4 | Heterogeneidad + corrección BH | `tabla_4_heterogeneidad.tex` |
| Tabla 5 | Stacked DiD — ATT agregado | `tabla_5_did_moderno.csv` |
| Tabla 6 | MDES — poder estadístico | `tabla_6_mdes.tex` |
| Tabla 7 | Extensivo + share | `tabla_7_extensive.tex` |
| Figura 1 | Event study (5 outcomes, K=4, L=8) | `figura_1_event_study.pdf` |
| Figura 2 | Sensibilidad event study | `figura_2_event_study_sens.pdf` |
| Figura 3 | Stacked DiD — ATT dinámico | `figura_3_did_moderno_eventstudy.pdf` |

## 3. Tablas y figuras — Apéndice

| ID | Contenido | Archivo |
|---|---|---|
| Tabla A1 | Robustez de ventana (3 ventanas × 2 outcomes) | `tabla_A1_window_robustness.csv` |
| Tabla A2 | MDES (5 outcomes) | `tabla_6_mdes.tex` |
| Tabla A3 | Sensibilidad event study | `pretrends_tests_sens.csv` |
| Figura A1 | Sensibilidad con bins alternativos | `figura_2_event_study_sens.pdf` |
| Figura A2 | Event study — Stacked DiD | `figura_3_did_moderno_eventstudy.pdf` |

Ver detalle en `docs/17b_APENDICE.md`.

---

## 4. Documentación metodológica

| Doc | Tema | Clave |
|---|---|---|
| `09_MODELADO_ECONOMETRICO.md` | Ecuaciones, supuestos, decisiones | §8 = Stacked DiD |
| `10_RESULTADOS_EMPIRICOS.md` | Resultados TWFE + Stacked + discusión | §4.5–4.6 = DiD moderno |
| `11_DID_MODERNO.md` | Implementación Stacked DiD | Clustering por `cve_mun` |
| `12_MDES_PODER.md` | MDES + interpretación del nulo | |
| `13_EVENT_STUDY_SENSIBILIDAD.md` | Borderline p=0.083 → sensibilidad | |
| `14_SAMPLE_POLICY.md` | Regla de muestra main vs full | |
| `15_EXTENSION_OUTCOMES.md` | Margen extensivo y composición | |
| `17_BIBLIOGRAFIA.md` | Bibliografía DiD moderno + BibTeX | |
| `17b_APENDICE.md` | Índice del apéndice estadístico | |
| `18_FREEZE_RELEASE.md` | Instrucciones de freeze y verif. | |
| `19_ONE_PAGER_ASESOR.md` | Resumen ejecutivo (~1 pág) | |
| **`20_CHECKLIST_DEFENSA.md`** | **Este documento** | |

---

## 5. Verificaciones de coherencia

| Verificación | Pasa |
|---|---|
| Números en Doc 10 coinciden con CSVs | ✅ |
| Ventana `[-4,+8]` consistente en Docs 9/10/11 | ✅ |
| Clustering `cve_mun` (2,471) en stacked | ✅ |
| Pre-tendencias no significativas (ambos estimadores) | ✅ |
| outputs/paper/ versionados en git | ✅ |
| Tag `v1.0-thesis-results` existente | ✅ |
| README "Resultado principal" matizado | ✅ |

---

## 6. Preguntas anticipadas de defensa

### "¿Por qué no usas Callaway & Sant'Anna?"
Implementé Stacked DiD (Cengiz et al. 2019 / Baker et al. 2022), que resuelve
el mismo problema de contaminación por tratamiento escalonado. Ver Tabla 5 y
Doc 11. Los tres outcomes nulos coinciden entre estimadores.

### "¿Cómo sabes que el nulo TWFE no es falta de poder?"
Tabla 6 (MDES): descartamos efectos > 0.026–0.088 σ con 80% de poder.
El Stacked DiD sí detecta efecto → el nulo TWFE refleja heterogeneidad temporal,
no ausencia de señal.

### "¿El Stacked DiD no es data mining?"
No: fue pre-especificado como robustez (cf. Roth et al. 2023, §4.1), y 3 de 5
outcomes coinciden con TWFE. La divergencia se explica por mayor poder del
stacked en productos crediticios agregados. La robustez de ventana (Tabla A1)
confirma estabilidad.

### "¿Cómo manejas el múltiple testing?"
Corrección Benjamini-Hochberg en heterogeneidad (Tabla 4). En el cuerpo
principal, los 5 outcomes son pre-especificados → no es fishing.

### "El pre-trend de tarjetas de crédito no pasa al 10%"
Con K=6 leads (sin binning agresivo), pasa cómodamente (p=0.212).
El borderline se debe al bin extremo k≤−4. Ver Figura 2.

### "¿Hay efecto en el margen extensivo?"
No: ni en acceso binario ni en composición de género. El efecto es
margen intensivo (más crédito donde ya hay). Ver Tabla 7.

### "¿Son robustos a la ventana temporal?"
Sí: Tabla A1 muestra que en ventanas [-4,+8], [-3,+8], [-4,+6] los 6
coeficientes son significativos al 1% y varían menos de 5%.

---

## 7. Reproducibilidad

```bash
cd Code/
source .venv/bin/activate
pip install -r requirements.txt && pip install -e .

# Pipeline completo (10 pasos + window robustness):
PYTHONPATH=src python -m tesis_alcaldesas.run_all
PYTHONPATH=src python -m did_moderno.window_robustness

# Verificar que outputs no cambiaron:
git diff -- outputs/paper/
```

---

## 8. Antes de entregar — Checklist final

- [ ] `run_all` ejecuta sin errores (10/10 pasos)
- [ ] `window_robustness` ejecuta sin errores
- [ ] Todos los CSVs/TEX/PDFs en `outputs/paper/` están presentes
- [ ] Tag `v1.0-thesis-results` (o v1.1) empujado a remoto
- [ ] One-pager (`19_ONE_PAGER_ASESOR.md`) revisado con asesor
- [ ] Slides de defensa creadas y alineadas con Docs 9/10
- [ ] README.md refleja pipeline actualizado
- [ ] Números en slides coinciden con CSVs
