# 15 — Extensión: Outcomes del Margen Extensivo y Composición

## Motivación

Los outcomes principales de la tesis miden **intensidad** (contratos per cápita,
saldos per cápita) en escala asinh. Pero una alcaldesa también podría afectar
el **margen extensivo** (¿hay *algún* acceso?) o la **composición de género**
(¿cambia la proporción de mujeres?).

Esta extensión es **exploratoria**: se declara antes de
ver los resultados como una pregunta complementaria, no como un ejercicio de
búsqueda de significancia.

## Outcomes

### Panel A: Margen extensivo (LPM)

Variable binaria:
$$\text{any\_X\_m} = \mathbf{1}\{X_m > 0\}$$

Se estima con un **Linear Probability Model** (LPM = OLS con Y binaria):
misma estructura TWFE con FE municipio + periodo, cluster SE municipio.

| Variable | Definición |
|---|---|
| `any_ncont_total_m` | ¿Tiene al menos un contrato? |
| `any_numtar_deb_m` | ¿Tiene al menos una tarjeta de débito? |
| `any_numtar_cred_m` | ¿Tiene al menos una tarjeta de crédito? |
| `any_numcontcred_hip_m` | ¿Tiene al menos un crédito hipotecario? |
| `any_saldocont_total_m` | ¿Tiene saldo > 0? |

### Panel B: Composición de género

$$\text{share\_m} = \frac{y_{m,\text{pc}}}{y_{m,\text{pc}} + y_{h,\text{pc}}}$$

con guarda: solo se calcula cuando el denominador > 1 por cada 10,000 adultos.

Un coeficiente positivo significaría que las alcaldesas *redistribuyen* el
acceso financiero hacia las mujeres, incluso si el total no cambia.

## Notas metodológicas

- **LPM vs Logit**: Se usa LPM por consistencia con el diseño de FE de panel.
  Logit con muchos FE puede tener problemas de incidental parameters.
- **Pre-especificación**: Se reporta como extensión exploratoria para evitar
  acusaciones de p-hacking. No forma parte de las hipótesis principales.

## Ejecución

```bash
python -m tesis_alcaldesas.models.extensive_margin
```

## Outputs

| Archivo | Contenido |
|---|---|
| `tabla_7_extensive.csv` | Resultados crudos (ambos paneles) |
| `tabla_7_extensive.tex` | Tabla LaTeX para la tesis |
