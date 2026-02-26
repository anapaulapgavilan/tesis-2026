# 11 — DiD Moderno (Stacked Difference-in-Differences)

## Motivación: ¿Por qué TWFE puede ser problemático?

El estimador TWFE (Two-Way Fixed Effects) convencional estima:

$$Y_{it} = \alpha_i + \gamma_t + \beta \cdot D_{it} + X_{it}'\delta + \varepsilon_{it}$$

donde $\beta$ se interpreta como el "efecto promedio". Sin embargo, **Goodman-Bacon
(2021)** demuestra que $\hat{\beta}_{TWFE}$ es un promedio ponderado de todas las
comparaciones 2×2 posibles entre grupos tratados en diferentes momentos, incluyendo
**comparaciones "malas"** donde unidades tratadas tempranamente sirven como control
para unidades tratadas más tarde.

Estos pesos pueden ser **negativos** cuando:
- El efecto del tratamiento varía en el tiempo (heterogeneidad dinámica)
- Hay tratamiento escalonado (*staggered adoption*)

En nuestro contexto, los municipios obtienen su primera alcaldesa en diferentes
trimestres entre 2018Q3 y 2022Q3, generando exactamente la estructura de adopción
escalonada que preocupa a la literatura.

### Soluciones propuestas en la literatura

| Estimador | Referencia | Idea central |
|---|---|---|
| Callaway & Sant'Anna | C&S (2021) | ATT por grupo-tiempo, agregable |
| Sun & Abraham | S&A (2021) | IW estimator: corrige pesos TWFE |
| Stacked DiD | CDLZ (2019) | Evita comparaciones contaminadas apilando |
| de Chaisemartin & D'Haultfoeuille | dCDH (2020) | Descomposición + estimador robusto |

## Estimador implementado: Stacked DiD

Se implementó el **Stacked DiD** (Cengiz, Dube, Lindner & Zipperer 2019)
por las siguientes razones:

1. **No requiere R** — se puede implementar completamente en Python con `linearmodels`
2. **Transparente** — la lógica es explícita y auditable
3. **Comparable** — produce un ATT directamente comparable con $\hat{\beta}_{TWFE}$

### Algoritmo

Para cada cohorte $g$ (municipios cuyo `first_treat_period` = $g$):

1. Construir sub-dataset: cohorte $g$ (tratados) + never-treated (controles)
2. Restringir a ventana $[g - 4, g + 8]$ trimestres
3. Añadir identificadores de stack (municipio×stack, periodo×stack)

Apilar todos los sub-datasets y estimar:

$$Y_{i,t,g} = \alpha_{i \times g} + \gamma_{t \times g} + \beta \cdot D_{i,t,g} + \varepsilon_{i,t,g}$$

con SE clustered a nivel municipio.

El coeficiente $\hat{\beta}$ es el ATT promedio ponderado por tamaño de cohorte,
**libre del sesgo de comparaciones contaminadas** porque cada cohorte tratada solo
se compara con never-treated.

### ATT Dinámico

Para el event study dinámico, se reemplazan las dummies de tratamiento por dummies
de event-time $k$ (relativas al onset del tratamiento), con referencia $k = -1$:

$$Y_{i,t,g} = \alpha_{i \times g} + \gamma_{t \times g} + \sum_{k \neq -1} \delta_k \cdot \mathbf{1}\{event\_time = k\} + \varepsilon_{i,t,g}$$

Los coeficientes $\hat{\delta}_k$ se interpretan como el ATT dinámico en cada
$k$ periodos antes/después del tratamiento.

## Comparación con TWFE

Los resultados se comparan en `outputs/paper/twfe_vs_did_moderno.txt`:

- **Si signos y magnitudes son similares:** El sesgo TWFE es menor en estos datos
  (consistente con que la mayoría de las cohortes entran en un rango estrecho).
- **Si difieren:** TWFE incorpora sesgos de timing negativo; el estimador stacked
  es más creíble.
- **En ambos casos:** Si ambos son nulos, la conclusión de "no efecto detectable"
  se refuerza con un estimador apropiado para staggered adoption.

## Outputs

| Archivo | Contenido |
|---|---|
| `tabla_5_did_moderno.csv` | ATT agregado: outcome, coef, SE, p-value, IC 95%, método |
| `figura_3_did_moderno_eventstudy.pdf` | ATT dinámico por event time (5 outcomes) |
| `twfe_vs_did_moderno.txt` | Comparación textual signos/magnitudes TWFE vs Stacked |

## Referencias

- Callaway, B. & Sant'Anna, P. H. C. (2021). *Difference-in-Differences with Multiple Time Periods*. Journal of Econometrics, 225(2), 200–230.
- Cengiz, D., Dube, A., Lindner, A. & Zipperer, B. (2019). *The Effect of Minimum Wages on Low-Wage Jobs*. Quarterly Journal of Economics, 134(3), 1405–1454.
- Goodman-Bacon, A. (2021). *Difference-in-Differences with Variation in Treatment Timing*. Journal of Econometrics, 225(2), 254–277.
- Sun, L. & Abraham, S. (2021). *Estimating Dynamic Treatment Effects in Event Studies with Heterogeneous Treatment Effects*. Journal of Econometrics, 225(2), 175–199.
