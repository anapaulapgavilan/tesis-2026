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
2. Restringir a ventana $[-4, +8]$ trimestres alrededor de $g$
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

### Nota sobre inferencia: clustering a nivel municipio original

En un dataset apilado, cada municipio $i$ aparece en múltiples stacks $g$.
Los efectos fijos anidados ($\alpha_{i \times g}$, $\gamma_{t \times g}$) absorben
heterogeneidad dentro de cada stack, pero el _clustering_ debe reflejar la
correlación residual a nivel de la unidad fundamental: el municipio original
(`cve_mun`), **no** la entidad compuesta municipio×stack (`mun_stack`).

Clusterizar por `mun_stack` equivaldría a tratar las $G$ apariciones del mismo
municipio como si fueran unidades independientes, lo que infla artificialmente
el número efectivo de clusters ($\sim$37,000 en lugar de $\sim$2,471) y subestima
los errores estándar. La implementación utiliza el argumento `clusters` de
`PanelOLS.fit()` de `linearmodels` para pasar directamente la variable `cve_mun`
como cluster ID, conservando los FE anidados por stack.

Esto es consistente con la recomendación de Cameron & Miller (2015) de
clusterizar al nivel más alto de la jerarquía en la que se sospecha correlación,
y con la práctica estándar en la literatura de stacked DiD (e.g., Deshpande &
Li 2019; Fadlon & Nielsen 2019).

## Resultados

### ATT agregado (Tabla 5)

| Outcome | Stacked ATT | SE | p | IC 95% |
|---|---|---|---|---|
| Contratos totales | 0.082 | 0.028 | 0.003 | [0.028, 0.137] |
| Tarjetas débito | −0.014 | 0.045 | 0.760 | [−0.102, 0.075] |
| Tarjetas crédito | 0.001 | 0.021 | 0.971 | [−0.041, 0.042] |
| Créditos hipotecarios | 0.019 | 0.023 | 0.407 | [−0.026, 0.065] |
| Saldo total | 0.274 | 0.059 | 0.000 | [0.158, 0.390] |

$N = 228{,}440$ observaciones (2,471 municipios × 15 stacks). SE clustered a nivel
municipio original (`cve_mun`, ~2,471 clusters).

### Interpretación comparada con TWFE

Los resultados revelan una **discrepancia importante** entre el TWFE convencional y
el Stacked DiD para dos outcomes:

1. **Contratos totales:** TWFE estima un efecto nulo ($\hat{\beta} = 0.007$, $p = 0.747$),
   mientras que el Stacked DiD detecta un efecto positivo significativo
   ($\hat{\beta} = 0.082$, $p = 0.003$). Esto sugiere que el TWFE convencional sufre
   de sesgo de atenuación por comparaciones contaminadas (Goodman-Bacon 2021), donde
   municipios tratados tempranamente absorben parte del efecto en las comparaciones "malas".

2. **Saldo total:** TWFE reporta un efecto nulo ($\hat{\beta} = 0.004$, $p = 0.931$),
   pero el Stacked DiD encuentra un efecto positivo grande y significativo
   ($\hat{\beta} = 0.274$, $p < 0.001$). La magnitud implica un incremento de ~27% en
   el saldo total per cápita de las mujeres.

3. **Tarjetas de débito, crédito e hipotecarios:** Ambos estimadores coinciden en
   la ausencia de efectos significativos, con signos y magnitudes similares.

### ATT dinámico (Figura 3)

Los coeficientes de event-time confirman:

- **Pre-trends:** Todos los outcomes pasan el test conjunto de tendencias paralelas
  ($p > 0.10$ en los cinco casos), lo que refuerza la credibilidad del diseño.
- **Post-tratamiento:** Para contratos totales y saldo total, los coeficientes post
  muestran una trayectoria ascendente que se materializa gradualmente después del
  evento, consistente con un efecto acumulativo del tratamiento.

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
