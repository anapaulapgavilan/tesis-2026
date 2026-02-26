"""
run_stacked_did.py — Stacked Difference-in-Differences (DiD moderno).

Resuelve el sesgo de TWFE convencional bajo adopción escalonada (staggered
treatment timing) documentado en Goodman-Bacon (2021), Callaway & Sant'Anna
(2021), y Sun & Abraham (2021).

Implementación:
  Para cada cohorte g (definida por `first_treat_period`):
    1. Construir un sub-dataset con la cohorte g (treated) y el grupo
       never-treated (control).
    2. Centrar el tiempo en event_time relativo al tratamiento.
    3. Restringir a una ventana [-K, +L] alrededor del evento.
    4. Estimar TWFE dentro del stack con FE municipio + FE periodo + cluster mun.
  Luego agregar los ATT por cohorte usando pesos proporcionales a N_treated.

Nota: Este es el fallback en Python. Si R estuviera disponible, se usaría
      el paquete `did` (Callaway & Sant'Anna) o `fixest` (Sun & Abraham).

Input:
  data/processed/analytical_panel_features.parquet

Outputs:
  outputs/paper/tabla_5_did_moderno.csv
  outputs/paper/figura_3_did_moderno_eventstudy.pdf
  outputs/paper/twfe_vs_did_moderno.txt

Uso:
  python -m did_moderno.run_stacked_did
  # o bien:
  python src/did_moderno/run_stacked_did.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from scipy import stats

# ---------------------------------------------------------------------------
# Paths — resueltos relativos al archivo
# ---------------------------------------------------------------------------
CODE_DIR = Path(__file__).resolve().parents[2]          # …/Code/
sys.path.insert(0, str(CODE_DIR / "src"))

from tesis_alcaldesas.config import (
    PARQUET_FEATURES, OUTPUT_PAPER, PRIMARY_OUTCOMES, OUTCOME_LABELS,
)

OUT = OUTPUT_PAPER
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PRIMARY_5 = PRIMARY_OUTCOMES
TREATMENT = "alcaldesa_final"
K_PRE = 4          # leads (semestres antes)
L_POST = 8         # lags  (semestres después)

LABEL_MAP = {k: v["es"] for k, v in OUTCOME_LABELS.items()}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _stars(p: float) -> str:
    if p < 0.01:
        return "***"
    elif p < 0.05:
        return "**"
    elif p < 0.10:
        return "*"
    return ""


def load_panel() -> pd.DataFrame:
    df = pd.read_parquet(PARQUET_FEATURES)
    return df


# ---------------------------------------------------------------------------
# 1. Build stacked dataset for ONE cohort g vs never-treated
# ---------------------------------------------------------------------------
def build_cohort_stack(
    df: pd.DataFrame,
    cohort_first_t: int,
    never_treated_muns: set,
    k_pre: int = K_PRE,
    l_post: int = L_POST,
) -> pd.DataFrame | None:
    """
    Para la cohorte g (first_treat_t == cohort_first_t):
      - Tomar municipios tratados de esa cohorte + never-treated
      - Restringir a la ventana [cohort_first_t - k_pre, cohort_first_t + l_post]
      - Añadir un ID de stack para FE anidados
    """
    # Municipios tratados de esta cohorte
    treated_muns = set(
        df.loc[df["first_treat_t"] == cohort_first_t, "cve_mun"].unique()
    )
    if len(treated_muns) == 0:
        return None

    # Ventana temporal
    t_min = cohort_first_t - k_pre
    t_max = cohort_first_t + l_post

    # Subconjunto: cohorte tratada + never-treated, dentro de la ventana
    muns = treated_muns | never_treated_muns
    mask = (
        df["cve_mun"].isin(muns)
        & (df["t_index"] >= t_min)
        & (df["t_index"] <= t_max)
    )
    sub = df.loc[mask].copy()

    if len(sub) == 0:
        return None

    # Event time relativo para este stack
    sub["event_time_stack"] = sub["t_index"] - cohort_first_t

    # Tratamiento limpio: 1 si el municipio es de esta cohorte Y
    # el periodo es >= first_treat_t
    sub["D_stack"] = (
        sub["cve_mun"].isin(treated_muns)
        & (sub["t_index"] >= cohort_first_t)
    ).astype(float)

    # IDs para FE anidados
    sub["stack_id"] = cohort_first_t
    sub["mun_stack"] = sub["cve_mun"].astype(str) + "_" + str(cohort_first_t)
    sub["t_stack"] = sub["t_index"].astype(str) + "_" + str(cohort_first_t)

    # Metadata
    sub["is_treated_cohort"] = sub["cve_mun"].isin(treated_muns).astype(int)

    return sub


# ---------------------------------------------------------------------------
# 2. Build FULL stacked dataset
# ---------------------------------------------------------------------------
def build_stacked_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Apila sub-datasets de todas las cohortes tratadas."""
    # Identificar never-treated
    never_treated = set(
        df.loc[df["cohort_type"] == "never-treated", "cve_mun"].unique()
    )
    print(f"  Never-treated municipios: {len(never_treated)}")

    # Cohortes (sin always-treated)
    switchers = df.loc[df["cohort_type"] == "switcher"]
    cohorts = sorted(switchers["first_treat_t"].dropna().unique())
    print(f"  Cohortes tratadas: {len(cohorts)} → {[int(c) for c in cohorts]}")

    stacks = []
    for g in cohorts:
        sub = build_cohort_stack(df, int(g), never_treated)
        if sub is not None and len(sub) > 0:
            n_tr = sub["is_treated_cohort"].sum() // max(
                sub.loc[sub["is_treated_cohort"] == 1, "t_index"].nunique(), 1
            )
            print(f"    Cohorte g={int(g)}: {len(sub):,} obs "
                  f"({int(n_tr)} treated muns, "
                  f"{sub['cve_mun'].nunique() - int(n_tr)} control muns)")
            stacks.append(sub)

    if not stacks:
        raise RuntimeError("No se pudo construir ningún stack (0 cohortes).")

    stacked = pd.concat(stacks, ignore_index=True)
    print(f"\n  Stacked dataset total: {len(stacked):,} obs  "
          f"| {stacked['cve_mun'].nunique()} municipios únicos "
          f"| {stacked['stack_id'].nunique()} stacks")

    return stacked


# ---------------------------------------------------------------------------
# 3. Estimate ATT from stacked regression (aggregate)
# ---------------------------------------------------------------------------
def estimate_stacked_att(
    stacked: pd.DataFrame,
    depvar: str,
) -> dict:
    """
    Regresión pooled sobre el dataset apilado:
      Y = α_{i×g} + γ_{t×g} + β · D_stack + ε
    con FE de municipio-stack y periodo-stack.
    Clustering a nivel del municipio original (cve_mun) a través de stacks,
    no por mun_stack, para reflejar la correlación intra-municipio correcta.

    Returns dict with coef, se, pval, ci, nobs.
    """
    cols = [depvar, "D_stack", "mun_stack", "t_stack", "cve_mun"]
    mask = stacked[cols[:2]].notna().all(axis=1)
    sub = stacked.loc[mask].copy()

    if len(sub) < 50:
        return None

    # PanelOLS needs numeric time index
    # Encode mun_stack and t_stack as integers
    sub["_ent"] = pd.Categorical(sub["mun_stack"]).codes
    sub["_tim"] = pd.Categorical(sub["t_stack"]).codes

    # Preserve original municipality for clustering across stacks
    _cluster_mun = pd.Categorical(sub["cve_mun"]).codes
    _cluster_mun = pd.Series(_cluster_mun, index=sub.index)

    sub = sub.set_index(["_ent", "_tim"])
    _cluster_mun.index = sub.index  # align after re-index

    y = sub[depvar]
    X = sub[["D_stack"]]

    mod = PanelOLS(y, X, entity_effects=True, time_effects=True, check_rank=False)
    res = mod.fit(cov_type="clustered", clusters=_cluster_mun)

    beta = res.params["D_stack"]
    se = res.std_errors["D_stack"]
    pval = res.pvalues["D_stack"]
    ci_lo, ci_hi = res.conf_int().loc["D_stack"]

    return {
        "coef": beta,
        "se": se,
        "pval": pval,
        "ci_lo": ci_lo,
        "ci_hi": ci_hi,
        "nobs": res.nobs,
        "r2w": res.rsquared_within,
    }


# ---------------------------------------------------------------------------
# 4. Dynamic ATT by event-time from stacked regression
# ---------------------------------------------------------------------------
def estimate_stacked_dynamic(
    stacked: pd.DataFrame,
    depvar: str,
    k_pre: int = K_PRE,
    l_post: int = L_POST,
    ref_k: int = -1,
) -> pd.DataFrame | None:
    """
    Regresión con dummies de event-time en el dataset apilado.

    Returns DataFrame of (k, coef, se, pval, ci_lo, ci_hi).
    """
    sub = stacked.copy()

    # Bin extremes
    sub["evt_bin"] = sub["event_time_stack"].clip(lower=-k_pre, upper=l_post)

    # Generate dummies (k != ref_k, only for treated cohort observations that
    # shift the identification; never-treated have event_time = NA/treated=0)
    dummy_cols = []
    for k in range(-k_pre, l_post + 1):
        if k == ref_k:
            continue
        col = f"evt_k{k:+d}"
        sub[col] = (sub["evt_bin"] == k).astype(float)
        # Never-treated should have all dummies = 0 (they have no event_time
        # per se, but event_time_stack is defined; the identification comes
        # from D_stack which is 0 for them)
        # Actually for stacked DiD, we use the dummy approach:
        # Only treated-cohort observations should have event-time dummies = 1
        sub.loc[sub["is_treated_cohort"] == 0, col] = 0.0
        dummy_cols.append((k, col))

    cols_needed = [depvar] + [c for _, c in dummy_cols] + ["mun_stack", "t_stack", "cve_mun"]
    mask = sub[[depvar]].notna().all(axis=1)
    sub = sub.loc[mask].copy()

    if len(sub) < 50:
        return None

    # PanelOLS needs numeric time index
    sub["_ent"] = pd.Categorical(sub["mun_stack"]).codes
    sub["_tim"] = pd.Categorical(sub["t_stack"]).codes

    # Preserve original municipality for clustering across stacks
    _cluster_mun = pd.Categorical(sub["cve_mun"]).codes
    _cluster_mun = pd.Series(_cluster_mun, index=sub.index)

    sub = sub.set_index(["_ent", "_tim"])
    _cluster_mun.index = sub.index  # align after re-index

    y = sub[depvar]
    X = sub[[c for _, c in dummy_cols]]

    mod = PanelOLS(y, X, entity_effects=True, time_effects=True, check_rank=False)
    res = mod.fit(cov_type="clustered", clusters=_cluster_mun)

    ci_df = res.conf_int()
    rows = []
    for k, col in dummy_cols:
        ci_row = ci_df.loc[col]
        rows.append({
            "k": k,
            "coef": res.params[col],
            "se": res.std_errors[col],
            "pval": res.pvalues[col],
            "ci_lo": ci_row.iloc[0],
            "ci_hi": ci_row.iloc[1],
        })

    # Add reference
    rows.append({
        "k": ref_k, "coef": 0.0, "se": 0.0,
        "pval": 1.0, "ci_lo": 0.0, "ci_hi": 0.0,
    })

    cdf = pd.DataFrame(rows).sort_values("k").reset_index(drop=True)

    # Pre-trends joint test
    pre_cols = [c for k, c in dummy_cols if k < 0 and k != ref_k]
    if pre_cols:
        pre_coefs = np.array([res.params[c] for c in pre_cols])
        vcov = res.cov.loc[pre_cols, pre_cols].values
        try:
            chi2_stat = pre_coefs @ np.linalg.solve(vcov, pre_coefs)
            chi2_pval = 1 - stats.chi2.cdf(chi2_stat, df=len(pre_cols))
        except np.linalg.LinAlgError:
            chi2_stat, chi2_pval = np.nan, np.nan
    else:
        chi2_stat, chi2_pval = np.nan, np.nan

    cdf.attrs["pretrend_chi2"] = chi2_stat
    cdf.attrs["pretrend_pval"] = chi2_pval

    return cdf


# ---------------------------------------------------------------------------
# 5. Plot dynamic ATT
# ---------------------------------------------------------------------------
def plot_dynamic(
    all_coefs: dict[str, pd.DataFrame],
    out_path: Path,
):
    """Event-study style plot from stacked DiD dynamic ATT."""
    n = len(all_coefs)
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    for i, (out_name, cdf) in enumerate(all_coefs.items()):
        ax = axes[i]

        ax.fill_between(cdf["k"], cdf["ci_lo"], cdf["ci_hi"],
                        alpha=0.15, color="darkgreen")
        ax.plot(cdf["k"], cdf["coef"], "o-", color="darkgreen",
                markersize=4, linewidth=1.2)
        ax.axhline(0, color="black", linewidth=0.5)
        ax.axvline(-0.5, color="red", linewidth=0.8, linestyle="--", alpha=0.7)

        pt_pval = cdf.attrs.get("pretrend_pval", np.nan)
        if not np.isnan(pt_pval):
            ax.text(0.02, 0.98, f"Pre-trend χ²: p={pt_pval:.3f}",
                    transform=ax.transAxes, fontsize=7, va="top",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="honeydew", alpha=0.5))

        label = LABEL_MAP.get(out_name, out_name)
        ax.set_title(label, fontsize=10)
        ax.set_xlabel("Event time (k)")
        ax.set_ylabel("ATT (asinh)")

    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Stacked DiD — ATT Dinámico por Event Time", fontsize=13, y=1.01)
    fig.tight_layout()

    fig.savefig(out_path, bbox_inches="tight", dpi=300)
    png = out_path.with_suffix(".png")
    fig.savefig(png, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  → Figura: {out_path} + {png}")


# ---------------------------------------------------------------------------
# 6. Compare with TWFE
# ---------------------------------------------------------------------------
def compare_twfe_vs_stacked(
    stacked_results: pd.DataFrame,
    twfe_path: Path,
    out_path: Path,
):
    """Produce a short text comparison of TWFE vs stacked DiD ATT."""
    try:
        twfe = pd.read_csv(twfe_path)
    except FileNotFoundError:
        print(f"  ⚠ No se encontró {twfe_path} — comparación omitida.")
        return

    lines = [
        "=" * 60,
        "COMPARACIÓN: TWFE convencional vs Stacked DiD",
        "=" * 60,
        "",
        f"{'Outcome':<25s} {'TWFE β':>10s} {'Stacked β':>10s} "
        f"{'TWFE p':>8s} {'Stacked p':>10s} {'Mismo signo':>12s}",
        "-" * 80,
    ]

    for _, row_s in stacked_results.iterrows():
        out = row_s["outcome"]
        row_t = twfe[twfe["outcome"] == out]
        if row_t.empty:
            continue
        row_t = row_t.iloc[0]

        same_sign = "Sí" if (row_s["coef"] * row_t["coef"]) >= 0 else "No"

        lines.append(
            f"{LABEL_MAP.get(out, out):<25s} "
            f"{row_t['coef']:>10.4f} {row_s['coef']:>10.4f} "
            f"{row_t['pval']:>8.4f} {row_s['pval']:>10.4f} "
            f"{same_sign:>12s}"
        )

    lines += [
        "",
        "-" * 80,
        "Interpretación:",
        "  Si los signos y magnitudes son similares → sesgo TWFE es menor.",
        "  Si difieren → TWFE puede incorporar sesgos de timing negativo.",
        "  En ambos casos, la conclusión cualitativa (nulo) se mantiene/revisa.",
        "",
        "Método Stacked DiD: Cengiz, Dube, Lindner & Zipperer (2019).",
        "  Cada cohorte g se compara solo con never-treated en una ventana",
        f"  [{-K_PRE}, +{L_POST}] alrededor del evento, con FE municipio×stack",
        "  y FE periodo×stack, SE clustered a nivel municipio.",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  → Comparación: {out_path}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("DiD MODERNO — Stacked Difference-in-Differences")
    print("=" * 60)

    # --- Load ---
    print("\n[1/5] Cargando panel …")
    df = load_panel()
    print(f"  Shape: {df.shape}")

    # --- Build stacked dataset ---
    print("\n[2/5] Construyendo dataset apilado …")
    stacked = build_stacked_dataset(df)

    # --- Aggregate ATT ---
    print("\n[3/5] Estimando ATT agregado (stacked) …")
    att_rows = []

    for out_name in PRIMARY_5:
        depvar = f"{out_name}_pc_asinh"
        label = LABEL_MAP.get(out_name, out_name)
        print(f"\n  [{out_name}] {depvar} …")

        res = estimate_stacked_att(stacked, depvar)
        if res is None:
            print(f"    ⚠ Insuficientes observaciones — omitido.")
            continue

        print(f"    ATT = {res['coef']:.4f}{_stars(res['pval'])}  "
              f"SE = {res['se']:.4f}  p = {res['pval']:.4f}  "
              f"N = {res['nobs']:,}")

        att_rows.append({
            "outcome": out_name,
            "label": label,
            "coef": res["coef"],
            "se": res["se"],
            "pval": res["pval"],
            "ci_lo": res["ci_lo"],
            "ci_hi": res["ci_hi"],
            "nobs": res["nobs"],
            "r2w": res["r2w"],
            "method": "Stacked DiD",
        })

    att_df = pd.DataFrame(att_rows)

    # Save tabla 5
    csv_path = OUT / "tabla_5_did_moderno.csv"
    att_df.to_csv(csv_path, index=False)
    print(f"\n  → Tabla 5: {csv_path}")

    # --- Dynamic ATT ---
    print("\n[4/5] Estimando ATT dinámico (event-time) …")
    all_dynamic = {}

    for out_name in PRIMARY_5:
        depvar = f"{out_name}_pc_asinh"
        print(f"  [{out_name}] dinámica …")

        cdf = estimate_stacked_dynamic(stacked, depvar)
        if cdf is not None:
            all_dynamic[out_name] = cdf
            pt_p = cdf.attrs.get("pretrend_pval", np.nan)
            print(f"    {len(cdf)} coefs  |  pre-trend p = {pt_p:.4f}")
        else:
            print(f"    ⚠ Insuficientes obs para dinámica.")

    # Plot
    if all_dynamic:
        fig_path = OUT / "figura_3_did_moderno_eventstudy.pdf"
        plot_dynamic(all_dynamic, fig_path)

    # --- Compare with TWFE ---
    print("\n[5/5] Comparando con TWFE convencional …")
    twfe_raw = OUT / "tabla_2_twfe_raw.csv"
    compare_path = OUT / "twfe_vs_did_moderno.txt"
    compare_twfe_vs_stacked(att_df, twfe_raw, compare_path)

    print("\n✓ DiD Moderno completado.")


if __name__ == "__main__":
    main()
