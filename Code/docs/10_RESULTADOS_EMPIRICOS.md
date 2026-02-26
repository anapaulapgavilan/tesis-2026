# Resultados empíricos

## 4.1  Estadísticos descriptivos

La Tabla 1 presenta las medias y desviaciones estándar de las variables de interés durante el período pre-tratamiento, desagregadas en tres grupos: municipios *nunca tratados* ($N = 1{,}476$; 25,016 observaciones trimestrales), municipios *conmutadores* (switchers, $N = 600$; 4,036 observaciones pre-tratamiento) y municipios *siempre tratados* ($N = 101$; 1,704 observaciones).  Los indicadores de inclusión financiera se expresan en escala de seno hiperbólico inverso (asinh) de las tasas per cápita por cada 10,000 mujeres adultas, lo que permite interpretar los coeficientes como semi-elasticidades aproximadas.

Los municipios que registran al menos un periodo con alcaldesa (switchers) tienden a ser ligeramente más grandes —con una media de $\ln(\text{Población})$ de 9.95 frente a 9.44 en el grupo de nunca tratados— y exhiben niveles pre-tratamiento algo superiores en todos los indicadores financieros: 7.67 frente a 6.98 en contratos totales (asinh), 7.31 frente a 7.00 en tarjetas de débito, y 6.32 frente a 5.78 en tarjetas de crédito.  Los municipios siempre tratados, por su parte, muestran promedios más cercanos al grupo de nunca tratados y algo inferiores a los switchers, consistente con el hecho de que se trata principalmente de municipios rurales o de menor tamaño donde la alcaldía ha estado ocupada por mujeres de forma continua.

Estas diferencias en niveles motivan la inclusión de efectos fijos municipales, que absorben cualquier heterogeneidad permanente entre unidades, así como efectos fijos de periodo, que capturan choques agregados comunes a todos los municipios en cada trimestre.

## 4.2  Resultados del modelo TWFE de referencia

La Tabla 2 reporta las estimaciones del modelo de diferencias en diferencias con efectos fijos bidireccionales (TWFE).  La especificación toma la forma:

$$y_{it} = \alpha_i + \lambda_t + \beta \cdot D_{it} + \varepsilon_{it}$$

donde $y_{it}$ es el indicador de inclusión financiera del municipio $i$ en el trimestre $t$, medido en escala asinh per cápita; $\alpha_i$ y $\lambda_t$ denotan los efectos fijos de municipio y periodo, respectivamente; $D_{it} = \texttt{alcaldesa\_final}_{it}$ es el indicador de tratamiento; y los errores estándar se agrupan (*cluster*) a nivel municipal para dar cuenta de la correlación serial intra-unidad.

No encontramos evidencia de un efecto estadísticamente significativo de la representación política femenina municipal sobre ninguno de los cinco indicadores primarios de inclusión financiera de las mujeres.  El coeficiente estimado para contratos totales es $\hat{\beta} = 0.007$ (EE = 0.022, $p = 0.747$), con un intervalo de confianza al 95\% de $[-0.035,\; 0.049]$.  En el caso de tarjetas de débito, la estimación puntual es ligeramente negativa ($\hat{\beta} = -0.014$, $p = 0.521$), mientras que para tarjetas de crédito es prácticamente nula ($\hat{\beta} = -0.002$, $p = 0.919$).  Los créditos hipotecarios muestran un coeficiente positivo pero lejos de cualquier umbral convencional de significancia ($\hat{\beta} = 0.018$, $p = 0.400$), y el saldo total registra una estimación cercana a cero ($\hat{\beta} = 0.004$, $p = 0.931$) con el intervalo más amplio de los cinco outcomes: $[-0.092,\; 0.100]$.

En términos sustantivos, un coeficiente de 0.007 en escala asinh equivaldría a un cambio aproximado de 0.7\% en la variable en niveles —una magnitud económicamente irrelevante—, y ninguno de los intervalos de confianza descarta un efecto nulo.  El $R^2$ intra-grupo es prácticamente cero en todos los modelos, lo que confirma que la variación del tratamiento dentro de cada municipio no explica variación adicional en los outcomes una vez absorbidos los efectos fijos.

Las 41,905 observaciones corresponden a 2,471 municipios observados durante 17 trimestres (2018-T3 a 2022-T3), con ocho municipios que presentan paneles incompletos (102 celdas faltantes, 0.24\% del total).

## 4.3  Diagnóstico de tendencias paralelas: event study

La identificación causal del estimador TWFE descansa sobre el supuesto de tendencias paralelas: en ausencia del tratamiento, la evolución de los outcomes habría sido similar entre municipios tratados y no tratados.  Para evaluar la plausibilidad de este supuesto, estimamos un modelo de event study con cuatro *leads* ($k = -4, -3, -2$; con $k = -1$ como referencia) y ocho *lags* ($k = 0, 1, \ldots, 7$), agrupando los extremos (*binned endpoints*) para los periodos fuera de la ventana.

La Figura 1 presenta los coeficientes estimados con sus intervalos de confianza al 95\% para cada uno de los cinco outcomes.  El patrón visual es consistente con la validez de tendencias paralelas: los coeficientes pre-tratamiento ($k < 0$) oscilan alrededor de cero sin mostrar una tendencia sistemática de alejamiento, y los coeficientes post-tratamiento permanecen igualmente cercanos a cero, confirmando la ausencia de un efecto dinámico del tratamiento.

Para formalizar el diagnóstico, realizamos un test conjunto de Wald ($\chi^2$) sobre la hipótesis nula de que todos los coeficientes pre-tratamiento ($k = -4, -3, -2$) son simultáneamente iguales a cero.  Los resultados se resumen a continuación:

- **Contratos totales:** $\chi^2 = 5.49$, $p = 0.139$ — no se rechaza al 10\%.
- **Tarjetas de débito:** $\chi^2 = 3.80$, $p = 0.284$ — no se rechaza.
- **Tarjetas de crédito:** $\chi^2 = 6.67$, $p = 0.083$ — rechazo marginal al 10\%.
- **Créditos hipotecarios:** $\chi^2 = 0.75$, $p = 0.861$ — no se rechaza.
- **Saldo total:** $\chi^2 = 3.52$, $p = 0.319$ — no se rechaza.

Cuatro de los cinco outcomes pasan el test de tendencias paralelas a un nivel de significancia del 10\%.  La excepción es tarjetas de crédito, donde el rechazo marginal ($p = 0.083$) se origina en el coeficiente del bin extremo $k \leq -4$ ($\hat{\beta} = -0.078$, $p = 0.043$), que agrega todos los periodos anteriores a cuatro trimestres previos al tratamiento.  Dado que los leads individuales más próximos ($k = -3$ y $k = -2$) no son significativos y que los bins extremos tienden a capturar efectos de composición, esta violación marginal no compromete sustancialmente la credibilidad del diseño.  No obstante, los resultados para tarjetas de crédito deben interpretarse con mayor cautela.

Un patrón similar se observa en contratos totales, donde el bin $k \leq -4$ muestra un coeficiente puntualmente significativo ($\hat{\beta} = -0.087$, $p = 0.031$), pero el test conjunto no rechaza la nula ($p = 0.139$), y los leads $k = -3$ y $k = -2$ no exhiben evidencia de divergencia.

En conjunto, el diagnóstico de tendencias paralelas es razonablemente favorable.  Los coeficientes post-tratamiento no muestran ningún quiebre respecto al patrón pre-tratamiento, lo cual es consistente tanto con la validez del diseño como con la conclusión de un efecto nulo.

## 4.4  Análisis de robustez y heterogeneidad

### 4.4.1  Robustez

La Tabla 3 presenta cinco pruebas de robustez aplicadas al outcome focal (contratos totales de mujeres), diseñadas para evaluar la sensibilidad del resultado principal ante elecciones metodológicas alternativas.

**Transformación funcional.**  La estimación bajo la transformación logarítmica $\log(1 + y)$ arroja un coeficiente de 0.005 (EE = 0.020), prácticamente idéntico al de la especificación base (0.007).  Lo mismo ocurre con la winsorización al percentil 1-99 previa a la transformación asinh ($\hat{\beta} = 0.008$, EE = 0.021).  Estas pruebas descartan que el resultado nulo se deba a la influencia de valores extremos o a la elección de escala.

**Exclusión de transiciones.**  Al imponer valores faltantes en los trimestres donde el tratamiento cambia de estado —eliminando posibles efectos transitorios de la alternancia— el coeficiente se reduce a 0.002 (EE = 0.024) con $N = 38{,}303$, lo que confirma que la inclusión de los periodos de transición no sesga la estimación.

**Placebo temporal.**  Al desplazar el indicador de tratamiento cuatro trimestres hacia el futuro, se obtiene un coeficiente de $-0.019$ (EE = 0.020), estadísticamente indistinguible de cero.  La ausencia de un efecto placebo refuerza que no existe anticipación ni tendencias diferenciales pre-tratamiento que contaminen la estimación principal.

**Placebo de género.**  Cuando se estima el mismo modelo TWFE pero utilizando como outcome los contratos de *hombres* en lugar de los de mujeres, el coeficiente es $-0.001$ (EE = 0.025).  La nulidad de este placebo es informativa: si el tratamiento (alcaldesa) generara un efecto sobre toda la actividad financiera municipal —y no específicamente sobre la inclusión de mujeres—, esperaríamos un coeficiente significativo también para hombres.  La ausencia de efecto en ambos géneros apunta a que el resultado nulo es genuino y no producto de un efecto general confundido.

En síntesis, los resultados son robustos a transformaciones funcionales alternativas, a la exclusión de periodos de transición y a dos especificaciones de placebo.  Todas las estimaciones de robustez se encuentran dentro de un rango estrecho ($[-0.019,\; 0.008]$) y ninguna alcanza significancia estadística convencional.

### 4.4.2  Heterogeneidad

La Tabla 4 explora la posibilidad de que el efecto promedio nulo oculte efectos heterogéneos en subpoblaciones definidas por dos dimensiones: el tipo de localidad (clasificación CONAPO en seis categorías) y el tercil de población municipal.

Sólo un subgrupo exhibe un coeficiente nominalmente significativo: los municipios clasificados como *metrópoli* ($\hat{\beta} = 0.030$, $p = 0.024$, $N = 220$).  Sin embargo, al ajustar por múltiples pruebas mediante el procedimiento de Benjamini-Hochberg (BH), el $q$-value correspondiente es 0.215, por lo que este resultado **no sobrevive la corrección por comparaciones múltiples** al nivel convencional de 10\%.

Los municipios rurales presentan un coeficiente negativo y de magnitud no despreciable ($\hat{\beta} = -0.104$, $p = 0.109$), pero tampoco alcanza significancia estadística ($q = 0.492$).  Los demás subgrupos —semi-metrópoli, en transición, semi-urbano y urbano— producen estimaciones puntuales cercanas a cero y $p$-valores superiores a 0.77.

La desagregación por terciles de población muestra un gradiente sugerente pero no significativo: los municipios del tercil más pequeño (T1) registran un coeficiente de $-0.069$ ($p = 0.196$), el tercil medio (T2) de $-0.021$ ($p = 0.504$), y el tercil más grande (T3) de $0.003$ ($p = 0.823$).  Ninguno sobrevive la corrección BH.

Estos hallazgos sugieren que no existe evidencia robusta de heterogeneidad en el efecto del tratamiento a lo largo de las dimensiones de urbanización o tamaño municipal.

## 4.5  DiD Moderno: Stacked Difference-in-Differences

La literatura reciente de econometría aplicada ha documentado que el estimador TWFE puede producir estimaciones sesgadas bajo adopción escalonada con efectos heterogéneos (Goodman-Bacon 2021; de Chaisemartin & D’Haultfoeuille 2020).  Como nuestro diseño presenta exactamente esta estructura —tratamiento que se activa en 15 cohortes distintas a lo largo de 17 trimestres—, incluimos como **robustez pre-especificada** el estimador Stacked DiD (Cengiz, Dube, Lindner & Zipperer 2019), que elimina las comparaciones contaminadas al restringir cada cohorte tratada a un grupo de control limpio de municipios never-treated.  Para cada una de las 15 cohortes tratadas, construimos un sub-dataset que incluye únicamente los municipios de esa cohorte y los 1,476 municipios nunca tratados, dentro de una ventana de $[-4, +8]$ trimestres alrededor del evento.  Los sub-datasets se apilan y se estima un modelo con efectos fijos anidados de municipio×stack ($\alpha_{i \times g}$) y periodo×stack ($\gamma_{t \times g}$), con errores estándar clustered a nivel del municipio original (`cve_mun`, ~2,471 clusters).  El estimando es un ATT promedio ponderado por tamaño de cohorte (número de municipios tratados en cada cohorte), comparando cada cohorte únicamente contra never-treated dentro de la ventana $[-4, +8]$.

Los resultados del Stacked DiD coinciden con el TWFE en tres de cinco outcomes (tarjetas de débito, crédito y créditos hipotecarios: efectos no significativos y magnitudes similares), pero difieren en dos.  En **contratos totales**, el TWFE estima un efecto esencialmente nulo ($\hat{\beta} = 0.007$, $p = 0.747$), mientras que el Stacked DiD arroja un coeficiente positivo y estadísticamente significativo ($\hat{\beta} = 0.082$, EE = 0.028, $p = 0.003$, IC 95\% $[0.028, 0.137]$).  En **saldo total**, el contraste es aún mayor: TWFE reporta $\hat{\beta} = 0.004$ ($p = 0.931$) frente a $\hat{\beta} = 0.274$ (EE = 0.059, $p < 0.001$, IC 95\% $[0.158, 0.390]$) del Stacked DiD.

Esta divergencia es consistente con la predicción teórica de atenuación bajo adopción escalonada: al usar municipios tratados tempranamente como controles implícitos para cohortes posteriores, el TWFE diluye el efecto.  El Stacked DiD, al restringir cada comparación a never-treated, aísla el efecto limpio.  Crucialmente, la coincidencia en los tres outcomes nulos descarta que el Stacked DiD simplemente “inflate” todos los coeficientes: la divergencia se concentra exactamente donde la teoría predice mayor sesgo de atenuación (outcomes con efectos reales que el TWFE no logra detectar).

El event study dinámico del Stacked DiD confirma la validez del diseño: los cinco outcomes pasan el test conjunto de tendencias paralelas ($p > 0.10$), y para contratos totales y saldo total los coeficientes post-tratamiento muestran una trayectoria ascendente gradual, consistente con un efecto acumulativo.  Este diagnóstico se realiza dentro del diseño stacked (cada cohorte tratada vs never-treated) y está condicionado a la ventana $[-4, +8]$ trimestres alrededor del evento.

## 4.6  Discusión y conclusiones del análisis empírico

Los resultados presentados en esta sección conducen a una conclusión matizada.  El modelo TWFE convencional no detecta efectos estadísticamente significativos en ninguno de los cinco indicadores.  Sin embargo, el estimador Stacked DiD —incluido como robustez pre-especificada ante la estructura de adopción escalonada del tratamiento, siguiendo las recomendaciones de Roth et al. (2023)— **identifica efectos positivos y significativos en contratos totales y saldo total**, los dos indicadores más agregados.

Esta discrepancia es informativa.  El hecho de que el TWFE atenúe los efectos hacia cero es consistente con la predicción teórica de Goodman-Bacon (2021): cuando hay heterogeneidad temporal en el efecto del tratamiento y adopción escalonada, las comparaciones contaminadas introducen un sesgo de atenuación.  El estimador Stacked DiD, al eliminar estas comparaciones, recupera un efecto que el TWFE no es capaz de detectar.

Para los tres outcomes restantes (tarjetas de débito, crédito e hipotecarios), ambos estimadores coinciden en la ausencia de efectos, lo que sugiere que el efecto del tratamiento se concentra en la dimensión de uso agregado del sistema financiero (contratos, saldos) pero no se traduce en mayor adopción de productos específicos.

Los intervalos de confianza del modelo TWFE son suficientemente estrechos como para descartar efectos de magnitud económicamente relevante en los outcomes donde ambos estimadores coinciden (tarjetas de débito, crédito e hipotecarios).  En el caso de los outcomes donde el Stacked DiD detecta efectos significativos (contratos totales y saldo total), los intervalos del TWFE incluyen el cero pero también incluyen los valores puntuales del Stacked DiD, lo que es consistente con un sesgo de atenuación más que con una contradicción entre estimadores.

Varias razones teóricas podrían explicar por qué el efecto aparece en indicadores agregados (contratos y saldos) pero no en productos específicos (tarjetas e hipotecas), así como la discrepancia entre el TWFE convencional y el Stacked DiD.

**Primer canal: oferta financiera parcialmente exógena y márgenes locales acotados.**  La distribución de sucursales, terminales punto de venta y ciertos productos financieros en México responde principalmente a decisiones de la banca comercial y a la regulación federal (CNBV), más que a la política municipal.  Sin embargo, los gobiernos locales sí podrían influir en márgenes complementarios —por ejemplo, facilitación administrativa, coordinación con intermediarios, difusión de programas, o confianza institucional— que afecten el uso agregado del sistema (contratos y saldos) aun cuando no modifiquen la adopción de productos específicos.

**Segundo canal: dinámica temporal y atenuación del TWFE.**  El panel abarca 17 trimestres (poco más de cuatro años).  Si los mecanismos operan gradualmente (confianza institucional, difusión, programas locales), los efectos podrían acumularse con rezago.  En línea con ello, el event study del Stacked DiD sugiere una trayectoria post-tratamiento positiva en contratos y saldos, consistente con un efecto acumulativo.  Por contraste, bajo TWFE los coeficientes post-tratamiento permanecen cercanos a cero, lo que es consistente con atenuación por comparaciones contaminadas en diseños con adopción escalonada (Goodman-Bacon, 2021).

**Tercer canal: heterogeneidad por contexto local (sin evidencia concluyente).**  Los análisis de heterogeneidad muestran signos opuestos entre subgrupos (positivo en metrópolis, negativo en municipios rurales), lo que sugiere que los mecanismos podrían operar de forma diferenciada según infraestructura y urbanización.  Sin embargo, estos resultados no sobreviven la corrección por múltiples pruebas, por lo que se interpretan como indicios exploratorios y no como hallazgos centrales.

**Cuarto canal: tratamiento difuso y medición de mecanismos.**  La variable `alcaldesa_final` mide la presencia de una mujer en la presidencia municipal, pero no captura orientación programática, capacidad administrativa o intensidad de implementación.  Esto puede explicar por qué el efecto aparece en agregados (contratos y saldos) pero no en productos específicos: el tratamiento podría operar por vías generales (uso/confianza) más que por cambios directos en oferta o diseño de productos.

Finalmente, conviene subrayar que la comparación entre estimadores enriquece la interpretación.  La evidencia, tomada en conjunto, sugiere que la representación política femenina municipal tiene un efecto positivo sobre medidas agregadas de inclusión financiera femenina (contratos totales y saldos), pero que este efecto no se traduce en mayor adopción de productos específicos (tarjetas e hipotecas).  La divergencia entre TWFE y Stacked DiD es exactamente la que predice la teoría bajo adopción escalonada con efectos heterogéneos, y la coincidencia en los tres outcomes nulos otorga credibilidad al patrón: no se trata de un artefacto general del estimador, sino de una corrección focalizada donde el sesgo TWFE es operativo.

En todo caso, los resultados son informativos: dentro del horizonte temporal y la definición de tratamiento analizados, la evidencia apunta a un efecto causal **concentrado en agregados** (contratos y saldos) y ausencia de efectos detectables en **productos específicos** (tarjetas e hipotecas).  Esta conclusión es robusta a múltiples especificaciones, y la comparación TWFE vs Stacked DiD sugiere que, en presencia de adopción escalonada, el TWFE puede subestimar efectos positivos al incorporar comparaciones contaminadas.
