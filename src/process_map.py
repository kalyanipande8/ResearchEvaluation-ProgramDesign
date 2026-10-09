"""Process map for the study workflow (Recruitment -> Consent -> Baseline
-> Follow-up), with real attrition rates and real stage-to-stage timing
computed from the cohort's actual timestamp fields -- a process map backed
by measured numbers, not just a static flowchart.
"""
from __future__ import annotations

import pandas as pd

STAGES = ["Recruited", "Consented", "Baseline complete", "Follow-up complete"]


def build_process_map(df: pd.DataFrame) -> dict:
    n_recruited = len(df)
    n_consented = df["consent_date"].notna().sum()
    n_baseline = int(df["completed_baseline"].sum())
    n_followup = int(df["completed_followup"].sum())

    stage_counts = [n_recruited, n_consented, n_baseline, n_followup]

    funnel = []
    for i, (stage, count) in enumerate(zip(STAGES, stage_counts)):
        pct_of_total = round(100 * count / n_recruited, 2)
        pct_of_prior = round(100 * count / stage_counts[i - 1], 2) if i > 0 else 100.0
        funnel.append({
            "stage": stage, "n": int(count),
            "pct_of_total_recruited": pct_of_total,
            "pct_retained_from_prior_stage": pct_of_prior,
        })

    # real stage-to-stage timing metrics, in days
    consent_lag = (pd.to_datetime(df["consent_date"]) - pd.to_datetime(df["recruitment_date"])).dt.days
    baseline_df = df.dropna(subset=["baseline_date"])
    baseline_lag = (pd.to_datetime(baseline_df["baseline_date"]) - pd.to_datetime(baseline_df["consent_date"])).dt.days
    followup_df = df.dropna(subset=["followup_date"])
    followup_lag = (pd.to_datetime(followup_df["followup_date"]) - pd.to_datetime(followup_df["baseline_date"])).dt.days

    timing = {
        "recruitment_to_consent_days": {"mean": round(float(consent_lag.mean()), 1), "median": float(consent_lag.median())},
        "consent_to_baseline_days": {"mean": round(float(baseline_lag.mean()), 1), "median": float(baseline_lag.median())},
        "baseline_to_followup_days": {"mean": round(float(followup_lag.mean()), 1), "median": float(followup_lag.median())},
    }

    # attrition by site -- flags whether any site has a disproportionate drop-off
    attrition_by_site = (
        df.groupby("site")
        .agg(n_recruited=("patient_id", "size"), n_followup_complete=("completed_followup", "sum"))
        .assign(followup_completion_rate=lambda d: round(100 * d["n_followup_complete"] / d["n_recruited"], 2))
        .reset_index()
        .to_dict(orient="records")
    )

    return {
        "funnel": funnel,
        "timing_days": timing,
        "attrition_by_site": attrition_by_site,
        "overall_followup_completion_rate_pct": round(100 * n_followup / n_recruited, 2),
    }


if __name__ == "__main__":
    from .simulate_cohort import simulate

    df = simulate()
    import json
    print(json.dumps(build_process_map(df), indent=2))
