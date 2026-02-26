"""
window_robustness.py — Robustez de ventana para Stacked DiD.

Estima el ATT agregado para ncont_total_m y saldocont_total_m bajo tres
ventanas: [-4,+8] (baseline), [-3,+8] y [-4,+6].
Mismo clustering (cve_mun) y mismo control (never-treated).

Output:
  outputs/paper/tabla_A1_window_robustness.csv

Uso:
  PYTHONPATH=src python -m did_moderno.window_robustness
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from linearmodels.panel import PanelOLS

# ---------------------------------------------------------------------------
CODE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CODE_DIR / "src"))

from tesis_alcaldesas.config import PARQUET_FEATURES, OUTPUT_PAPER, OUTCOME_LABELS

OUT = OUTPUT_PAPER
OUT.mkdir(parents=True, exist_ok=True)

OUTCOMES = ["ncont_total_m", "saldocont_total_m"]
LABEL = {k: v["es"] for k, v in OUTCOME_LABELS.items()}

WINDOWS = [
    (4, 8, "[-4, +8] (baseline)"),
    (3, 8, "[-3, +8]"),
    (4, 6, "[-4, +6]"),
]


# ---------------------------------------------------------------------------
def _build_stacked(df: pd.DataFrame, k_pre: int, l_post: int) -> pd.DataFrame:
    """Build stacked dataset with given window, reusing core logic."""
    from did_moderno.run_stacked_did import build_cohort_stack

    never_treated = set(
        df.loc[df["cohort_type"] == "never-treated", "cve_mun"].unique()
    )
    switchers = df.loc[df["cohort_type"] == "switcher"]
    cohorts = sorted(switchers["first_treat_t"].dropna().unique())

    stacks = []
    for g in cohorts:
        sub = build_cohort_stack(df, int(g), never_treated,
                                 k_pre=k_pre, l_post=l_post)
        if sub is not None and len(sub) > 0:
            stacks.append(sub)

    return pd.concat(stacks, ignore_index=True)


def _estimate_att(stacked: pd.DataFrame, depvar: str) -> dict | None:
    """Pooled stacked ATT, clustered by cve_mun."""
    col = depvar + "_pc_asinh"
    cols = [col, "D_stack", "mun_stack", "t_stack", "cve_mun"]
    mask = stacked[cols[:2]].notna().all(axis=1)
    sub = stacked.loc[mask].copy()
    if len(sub) < 50:
        return None

    sub["_ent"] = pd.Categorical(sub["mun_stack"]).codes
    sub["_tim"] = pd.Categorical(sub["t_stack"]).codes
    _cluster = pd.Categorical(sub["cve_mun"]).codes
    _cluster = pd.Series(_cluster, index=sub.index)

    sub = sub.set_index(["_ent", "_tim"])
    _cluster.index = sub.index

    mod = PanelOLS(sub[col], sub[["D_stack"]],
                   entity_effects=True, time_effects=True, check_rank=False)
    res = mod.fit(cov_type="clustered", clusters=_cluster)

    b = res.params["D_stack"]
    se = res.std_errors["D_stack"]
    p = res.pvalues["D_stack"]
    ci = res.conf_int().loc["D_stack"]
    return dict(coef=b, se=se, pval=p, ci_lo=ci.iloc[0], ci_hi=ci.iloc[1],
                nobs=res.nobs)


# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("ROBUSTEZ DE VENTANA — Stacked DiD")
    print("=" * 60)

    df = pd.read_parquet(PARQUET_FEATURES)
    print(f"Panel: {df.shape}")

    rows = []
    for k_pre, l_post, wlabel in WINDOWS:
        print(f"\n  Ventana {wlabel} …")
        stacked = _build_stacked(df, k_pre, l_post)
        print(f"    {len(stacked):,} obs, {stacked['stack_id'].nunique()} stacks")

        for out in OUTCOMES:
            r = _estimate_att(stacked, out)
            if r is None:
                continue
            stars = "***" if r["pval"] < 0.01 else ("**" if r["pval"] < 0.05
                    else ("*" if r["pval"] < 0.10 else ""))
            print(f"    {LABEL.get(out, out):30s}  "
                  f"β={r['coef']:.4f}{stars}  SE={r['se']:.4f}  p={r['pval']:.4f}")
            rows.append({
                "window": wlabel,
                "outcome": out,
                "label": LABEL.get(out, out),
                **r,
            })

    result = pd.DataFrame(rows)
    path = OUT / "tabla_A1_window_robustness.csv"
    result.to_csv(path, index=False)
    print(f"\n→ {path}")
    print("✓ Robustez de ventana completada.")


if __name__ == "__main__":
    main()
