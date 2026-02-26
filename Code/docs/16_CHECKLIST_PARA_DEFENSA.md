# 16 — Checklist para Defensa de Tesis

## Estado del análisis empírico

| # | Componente | Estado | Script | Output |
|---|---|---|---|---|
| 1 | Descriptivos pre-tratamiento | ✅ | `table1_descriptives.py` | `tabla_1_descriptiva.*` |
| 2 | TWFE baseline (5 outcomes) | ✅ | `twfe.py` | `tabla_2_twfe.*` |
| 3 | Event study + pre-trends | ✅ | `event_study.py` | `figura_1_event_study.pdf`, `pretrends_tests.csv` |
| 4 | Robustez (log1p, winsor, excl. trans., placebo T, placebo G) | ✅ | `robustness.py` | `tabla_3_robustez.*` |
| 5 | Heterogeneidad (tipo_pob, terciles pob) + BH | ✅ | `heterogeneity.py` | `tabla_4_heterogeneidad.*` |
| 6 | **DiD moderno (Stacked DiD)** | ✅ | `did_moderno/run_stacked_did.py` | `tabla_5_did_moderno.csv`, `figura_3_*.pdf` |
| 7 | **MDES / poder estadístico** | ✅ | `mdes_power.py` | `tabla_6_mdes.*`, `mdes_summary.txt` |
| 8 | **Sensibilidad event study (bin extremo)** | ✅ | `event_study_sensitivity.py` | `figura_2_*.pdf`, `pretrends_tests_sens.csv` |
| 9 | **Sample policy (main vs full)** | ✅ | `sample_policy.py` | `tabla_2_twfe_main.*`, `sample_sensitivity.txt` |
| 10 | **Extensión: extensivo + composición** | ✅ | `extensive_margin.py` | `tabla_7_extensive.*` |

## Tablas y figuras para la tesis

| Tabla/Figura | Contenido | Archivo |
|---|---|---|
| Tabla 1 | Estadísticas descriptivas pre-tratamiento | `tabla_1_descriptiva.tex` |
| Tabla 2 | TWFE baseline (5 outcomes, asinh) | `tabla_2_twfe.tex` |
| Tabla 3 | Pruebas de robustez | `tabla_3_robustez.tex` |
| Tabla 4 | Heterogeneidad + corrección BH | `tabla_4_heterogeneidad.tex` |
| **Tabla 5** | **DiD moderno — ATT agregado (Stacked DiD)** | `tabla_5_did_moderno.csv` |
| **Tabla 6** | **MDES — poder estadístico** | `tabla_6_mdes.tex` |
| **Tabla 7** | **Extensión: extensivo + share** | `tabla_7_extensive.tex` |
| Figura 1 | Event study (5 outcomes, K=4, L=8) | `figura_1_event_study.pdf` |
| **Figura 2** | **Sensibilidad event study** | `figura_2_event_study_sens.pdf` |
| **Figura 3** | **DiD moderno — ATT dinámico** | `figura_3_did_moderno_eventstudy.pdf` |

## Documentación metodológica

| Doc | Tema |
|---|---|
| `09_MODELADO_ECONOMETRICO.md` | Ecuaciones, supuestos, decisiones |
| `10_RESULTADOS_EMPIRICOS.md` | Resultados del TWFE, event study, robustez |
| **`11_DID_MODERNO.md`** | **Por qué TWFE puede sesgar + implementación stacked** |
| **`12_MDES_PODER.md`** | **Qué es MDES + interpretación del nulo** |
| **`13_EVENT_STUDY_SENSIBILIDAD.md`** | **Sensibilidad del borderline p=0.083** |
| **`14_SAMPLE_POLICY.md`** | **Regla de muestra main vs full** |
| **`15_EXTENSION_OUTCOMES.md`** | **Margen extensivo y composición** |

## Preguntas anticipadas de defensa

### "¿Por qué no usas Callaway & Sant'Anna?"
→ Se implementó Stacked DiD (Cengiz et al. 2019) que resuelve el mismo problema.
Ver Tabla 5 y doc `11_DID_MODERNO.md`. Los resultados son cualitativamente
consistentes con TWFE (ver `twfe_vs_did_moderno.txt`).

### "¿Cómo sabes que el nulo no es falta de poder?"
→ Tabla 6 de MDES muestra que descartamos efectos > ~5-6% en contratos/tarjetas
con 80% de poder. Ver doc `12_MDES_PODER.md`.

### "El pre-trend de tarjetas de crédito no pasa al 10%"
→ Con K=6 leads (sin binning agresivo), pasa cómodamente (p=0.212).
El borderline se debe al bin extremo k≤-4. Ver Figura 2 y doc
`13_EVENT_STUDY_SENSIBILIDAD.md`.

### "¿Por qué excluyes 8 municipios?"
→ Panel incompleto (< 17 trimestres). La exclusión no cambia ningún resultado.
Ver doc `14_SAMPLE_POLICY.md` y `sample_sensitivity.txt`.

### "¿Hay efecto en el margen extensivo?"
→ No. Ni en acceso binario (any > 0) ni en composición de género (share mujeres).
Ver Tabla 7 y doc `15_EXTENSION_OUTCOMES.md`.

## Reproducibilidad

```bash
cd Code/
source .venv/bin/activate
pip install -r requirements.txt && pip install -e .

# Pipeline completo:
PYTHONPATH=src python -m tesis_alcaldesas.run_all

# O por partes:
make models
```
