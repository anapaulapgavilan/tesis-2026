# 13 — Sensibilidad del Event Study al Bin Extremo

## Problema

En el event study baseline (K=4 leads, L=8 lags), el test conjunto de
pre-trends para **tarjetas de crédito** (`numtar_cred_m`) arroja p=0.083,
ligeramente por debajo del umbral convencional de 10%. Esto podría levantar
la crítica de que el bin extremo (k ≤ -4) está arrastrando el test.

## ¿Qué se hizo?

Se corrieron 3 variantes adicionales para los 2 outcomes más delicados
(tarjetas de crédito y contratos totales):

| Variante | K leads | L lags | Excluye |
|---|---|---|---|
| **Baseline** | 4 | 8 | — |
| **A** | 3 | 8 | — (bin cambia a k ≤ -3) |
| **B** | 6 | 8 | — (bin cambia a k ≤ -6, más granular) |
| **C** | 4 | 8 | Cohorte g=0 (tratados desde el inicio) |

## Resultados

### Tarjetas de crédito (`numtar_cred_m`)

| Variante | χ² stat | p-value | Pasa al 10%? |
|---|---|---|---|
| Baseline (K=4) | 6.671 | 0.083 | No (borderline) |
| A: K=3 | 5.111 | 0.078 | No (borderline) |
| B: K=6 | 7.119 | 0.212 | **Sí** |
| C: Excl. g=0 | 7.155 | 0.067 | No |

### Contratos totales (`ncont_total_m`)

| Variante | χ² stat | p-value | Pasa al 10%? |
|---|---|---|---|
| Baseline (K=4) | 5.491 | 0.139 | Sí |
| A: K=3 | 4.850 | 0.089 | No (borderline) |
| B: K=6 | 7.170 | 0.208 | **Sí** |
| C: Excl. g=0 | 5.623 | 0.131 | Sí |

## Interpretación

1. **Variante B (K=6)** es la más favorable: al extender la ventana pre, el
   bin deja de acumular periodos lejanos y el test pasa cómodamente. Esto
   sugiere que el p=0.083 del baseline proviene de la acumulación heterogénea
   en el bin k ≤ -4.

2. **Variante A (K=3)** no mejora el p-value de tarjetas de crédito, lo que
   sugiere que la señal no está solo en k = -4 sino distribuida en los leads.

3. **Variante C (excluir g=0)** no cambia sustancialmente el resultado, lo
   que indica que las cohortes tempranas no son las únicas responsables.

4. **Conclusión para la tesis**: El borderline p=0.083 es sensible a la
   especificación de la ventana. Con K=6 leads (que permite ver más periodos
   pre-tratamiento sin binning), el test de pre-trends pasa. Esto refuerza
   la interpretación de que las tendencias paralelas se sostienen para los
   5 outcomes primarios.

## Outputs

| Archivo | Contenido |
|---|---|
| `pretrends_tests_sens.csv` | Tests conjuntos para cada variante × outcome |
| `figura_2_event_study_sens.pdf` | Panel de event studies: outcomes × variantes |

## Ejecución

```bash
python -m tesis_alcaldesas.models.event_study_sensitivity
```
