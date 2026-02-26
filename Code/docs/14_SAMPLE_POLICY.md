# 14 — Sample Policy (Regla de muestra)

## Definición

### Main sample (muestra principal)

- **Panel balanceado**: excluye municipios con `flag_incomplete_panel == 1`
  (aquellos con menos de 17 trimestres en la base).
- Estos municipios se identificaron en `build_features.py` y se marcan
  con el flag correspondiente.

### Full sample (muestra completa)

- Incluye **todos** los municipios, incluso los que no tienen los 17
  trimestres completos.
- Se usa como **robustez**: si los resultados no cambian al incluir
  municipios incompletos, la exclusión no sesga.

## Municipios incompletos

El panel tiene 2,471 municipios × 17 trimestres = 42,007 obs esperadas.
La base tiene 41,905 obs → 102 obs faltantes → 8 municipios con panel
incompleto (6 con 16 trimestres, 1 con 15, 1 con 14).

### ¿Son los incompletos diferentes?

La pregunta clave es si el missingness se correlaciona con el tratamiento.
Si los municipios que "faltan" periodos son sistemáticamente más o menos
propensos a tener alcaldesas, excluirlos sesga el estimador.

## Implementación

El script `sample_policy.py` corre TWFE en ambas muestras y compara:

```bash
python -m tesis_alcaldesas.models.sample_policy
```

### Outputs

| Archivo | Contenido |
|---|---|
| `tabla_2_twfe_main.csv` / `.tex` | TWFE solo con panel balanceado |
| `tabla_2_twfe_full.csv` / `.tex` | TWFE con panel completo |
| `sample_sensitivity.txt` | Comparación textual de ambos |

## Regla para la tesis

> **Main sample**: Panel balanceado (drop `flag_incomplete_panel == 1`)
> para todas las tablas y figuras principales.
>
> **Robustez**: Full sample (incluye todos) en la tabla de sensibilidad.
> Si los coeficientes no cambian sustancialmente, la exclusión es inocua.

## Justificación

- 8 municipios de ~2,471 = 0.3% del panel.
- Excluirlos asegura que la estructura de panel es regular para FE.
- La robustez con full sample confirma que la exclusión no mueve resultados.
