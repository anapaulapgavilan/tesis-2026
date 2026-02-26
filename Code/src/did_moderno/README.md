# DiD Moderno — Estimadores robustos a adopción escalonada

## ¿Qué contiene esta carpeta?

| Archivo | Descripción |
|---|---|
| `run_stacked_did.py` | Stacked DiD en Python (fallback; R no disponible en este entorno) |
| `README.md` | Este archivo |

## ¿Cómo correrlo?

```bash
cd Code/
source .venv/bin/activate
python -m did_moderno.run_stacked_did
```

## ¿Qué produce?

| Output | Descripción |
|---|---|
| `outputs/paper/tabla_5_did_moderno.csv` | ATT agregado por outcome (Stacked DiD) |
| `outputs/paper/figura_3_did_moderno_eventstudy.pdf` | ATT dinámico por event-time (event study desde stacked) |
| `outputs/paper/twfe_vs_did_moderno.txt` | Comparación cualitativa TWFE vs Stacked DiD |

## Lógica del estimador

El **Stacked DiD** (Cengiz, Dube, Lindner & Zipperer 2019) resuelve el sesgo
del TWFE convencional bajo adopción escalonada (*staggered treatment*):

1. Para cada cohorte *g* (definida por `first_treat_period`):
   - Se construye un sub-dataset con los municipios tratados en *g* y los
     municipios **never-treated** como controles.
   - Se restringe a una ventana `[-4, +8]` trimestres alrededor del evento.

2. Todos los sub-datasets se apilan (*stack*), añadiendo FE anidados
   (municipio × stack, periodo × stack).

3. Se estima un único PanelOLS sobre el dataset apilado con:
   - FE municipio-stack (absorbe heterogeneidad municipal dentro de cada comparación)
   - FE periodo-stack (absorbe shocks temporales dentro de cada comparación)
   - SE clustered a nivel municipio

4. El coeficiente de `D_stack` es el **ATT promedio ponderado** por tamaño
   de cohorte, libre del sesgo de comparaciones contaminadas.

## Si R estuviera disponible

Se preferiría usar:
- `did::att_gt()` (Callaway & Sant'Anna 2021) para ATT por grupo-tiempo
- `did::aggte()` para agregaciones (simple, dinámico, calendario)
- `fixest::sunab()` (Sun & Abraham 2021) como alternativa

Para instalar en R:
```r
install.packages(c("did", "fixest", "arrow"))
```

## Dependencias Python

No requiere paquetes adicionales a los ya en `requirements.txt`:
- `linearmodels` (PanelOLS)
- `scipy` (test chi-cuadrado para pre-trends)
- `matplotlib` (figuras)
