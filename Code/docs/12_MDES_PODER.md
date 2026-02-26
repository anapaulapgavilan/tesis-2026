# 12 — MDES y Análisis de Poder Estadístico

## ¿Qué es el MDES?

El **Minimum Detectable Effect Size** (MDES) es el efecto más pequeño que un
diseño de investigación puede detectar con una probabilidad determinada (poder
estadístico). Se calcula como:

$$\text{MDES} = (z_{\alpha/2} + z_{\beta}) \times SE$$

donde:
- $z_{\alpha/2}$ = cuantil normal bilateral para el nivel de significancia
  (1.96 para $\alpha = 0.05$)
- $z_{\beta}$ = cuantil normal para el poder deseado
  (0.84 para poder = 80%)
- $SE$ = error estándar del coeficiente de tratamiento

## ¿Por qué importa para esta tesis?

El resultado principal de la tesis es un **efecto nulo**: no se detecta un
impacto estadísticamente significativo de las alcaldesas sobre la inclusión
financiera femenina. Sin embargo, un nulo puede significar dos cosas:

1. **No hay efecto** (verdadero nulo)
2. **Hay efecto pero el estudio no tiene poder para detectarlo** (falso nulo)

El MDES permite distinguir entre ambos: reporta el efecto más pequeño que
*sí podríamos haber detectado*. Si ese umbral es razonablemente pequeño,
el nulo es informativo ("descartamos efectos mayores a X%").

## Resultados

Los resultados están en:
- `outputs/paper/tabla_6_mdes.csv` — tabla completa
- `outputs/paper/tabla_6_mdes.tex` — formato LaTeX para la tesis
- `outputs/paper/mdes_summary.txt` — interpretación en lenguaje natural

### Interpretación

La SE del tratamiento TWFE viene de la Tabla 2 baseline. Los MDES se reportan
en dos escalas:

1. **Escala asinh** — directamente comparable con los coeficientes reportados
2. **Escala porcentual aproximada** — usando $(\exp(|\text{MDES}|) - 1) \times 100$

Esta aproximación es válida porque para $y$ grande, $\text{asinh}(y) \approx \ln(2y)$,
y cambios en log son cambios porcentuales.

### Cómo citar en la tesis

> "Con el diseño actual (N ≈ 41,905 observaciones municipio-trimestre, errores
> estándar agrupados a nivel municipal), podemos descartar con 80% de poder
> estadístico ($\alpha = 0.05$) efectos del tratamiento mayores a [X]% en
> [outcome]. El resultado nulo es informativo: efectos de la magnitud que la
> política pública podría esperar (mejoras de un dígito porcentual en indicadores
> de inclusión financiera) no están en nuestro intervalo de confianza."

## Ejecución

```bash
python -m tesis_alcaldesas.models.mdes_power
```

## Referencias

- Bloom, H. S. (1995). *Minimum Detectable Effects: A Simple Way to Report the
  Statistical Power of Experimental Designs*. Evaluation Review, 19(5), 547–556.
- Ioannidis, J. P. A., Stanley, T. D. & Doucouliagos, H. (2017). *The Power of
  Bias in Economics Research*. Economic Journal, 127, F236–F265.
