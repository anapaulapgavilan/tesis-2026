# Apéndice — Tablas y Figuras Complementarias

Este apéndice lista los outputs complementarios que acompañan el capítulo de
resultados empíricos.  Todos son reproducibles con el pipeline del repositorio.

---

## A. Tablas

### Tabla A1. Robustez de ventana — Stacked DiD

| Campo | Detalle |
|---|---|
| Archivo | `outputs/paper/tabla_A1_window_robustness.csv` |
| Script | `src/did_moderno/window_robustness.py` |
| Muestra | 2,471 municipios × 15 cohortes, never-treated como control |
| Estimador | Stacked DiD (PanelOLS con FE municipio×stack + periodo×stack) |
| Clustering | Municipio original (`cve_mun`, ~2,471 clusters) |
| Ventanas | $[-4, +8]$ (baseline), $[-3, +8]$, $[-4, +6]$ |
| Outcomes | `ncont_total_m` (contratos totales), `saldocont_total_m` (saldo total) |

Resultados: las seis estimaciones (3 ventanas × 2 outcomes) son significativas
al 1% y los coeficientes varían menos de 5% respecto al baseline,
confirmando que los hallazgos no dependen de la elección de ventana.

---

### Tabla A2. MDES — Minimum Detectable Effect Size

| Campo | Detalle |
|---|---|
| Archivo | `outputs/paper/tabla_6_mdes.csv`, `outputs/paper/tabla_6_mdes.tex` |
| Script | `src/tesis_alcaldesas/models/mdes_power.py` |
| Texto resumen | `outputs/paper/mdes_summary.txt` |
| Muestra | 41,905 obs (panel principal), 894 switchers |
| Estimador | TWFE (cálculo analítico de MDE basado en varianza residual y $N_{eff}$) |
| Poder | 80%, $\alpha = 0.05$ (bilateral) |

Reporta el efecto mínimo detectable para cada outcome, permitiendo interpretar
los nulos del TWFE como "descartamos efectos mayores a X%".

---

### Tabla A3. Sensibilidad del event study — pre-trends bajo especificaciones alternativas

| Campo | Detalle |
|---|---|
| Archivo (tests) | `outputs/paper/pretrends_tests_sens.csv` |
| Archivo (figura) | `outputs/paper/figura_2_event_study_sens.pdf` |
| Script | `src/tesis_alcaldesas/models/event_study_sensitivity.py` |
| Muestra | 41,905 obs (panel principal) |
| Variantes | 4 especificaciones × 2 outcomes (`ncont_total_m`, `numtar_cred_m`) |
| Objetivo | Blindar el borderline $p = 0.083$ en tarjetas de crédito |

Las variantes incluyen: (i) baseline K=4/L=8, (ii) K=6/L=8 sin binning agresivo,
(iii) K=4/L=6, (iv) K=4/L=8 con log(1+y).  Con K=6, tarjetas de crédito pasa
holgadamente ($p > 0.20$).

---

## B. Figuras

### Figura A1. Sensibilidad del event study

| Campo | Detalle |
|---|---|
| Archivo | `outputs/paper/figura_2_event_study_sens.pdf` (`.png` también disponible) |
| Script | `src/tesis_alcaldesas/models/event_study_sensitivity.py` |
| Contenido | Coeficientes de event-time bajo 4 variantes × 2 outcomes |

---

### Figura A2. Event study dinámico — Stacked DiD

| Campo | Detalle |
|---|---|
| Archivo | `outputs/paper/figura_3_did_moderno_eventstudy.pdf` (`.png` también disponible) |
| Script | `src/did_moderno/run_stacked_did.py` |
| Contenido | ATT dinámico por event-time (5 outcomes), FE anidados, cluster `cve_mun` |
| Ventana | $[-4, +8]$ trimestres |

---

## C. Otros outputs complementarios

| Archivo | Contenido |
|---|---|
| `outputs/paper/twfe_vs_did_moderno.txt` | Comparación textual TWFE vs Stacked DiD (signos, magnitudes) |
| `outputs/paper/sample_sensitivity.txt` | Comparación main sample vs full sample |
| `outputs/paper/tabla_2_twfe_main.csv` / `_full.csv` | TWFE por muestra |
| `outputs/paper/tabla_7_extensive.csv` | Margen extensivo (LPM binary + share) |

---

## Reproducción

```bash
cd Code/
source .venv/bin/activate
PYTHONPATH=src python -m tesis_alcaldesas.run_all          # pipeline principal (Tablas 1-7, Figuras 1-3)
PYTHONPATH=src python -m did_moderno.window_robustness     # Tabla A1: robustez de ventana
```
