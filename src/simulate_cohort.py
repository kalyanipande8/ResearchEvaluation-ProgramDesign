"""Simulate a 340-patient observational health-study cohort with real
process timestamps (recruitment through analysis-lock), for a research
evaluation methodology and program-design demonstration.

Unlike the causal-inference projects in this portfolio, the focus here is
not effect estimation -- it's the evaluation/documentation layer: a
codebook, a process map with real attrition/timing metrics, and an
evaluation-framework (RE-AIM) maturity score.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

N_PATIENTS = 340
SEED = 29

STUDY_SITES = ["Site-A", "Site-B", "Site-C", "Site-D"]


def simulate(n: int = N_PATIENTS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    py_rng = random.Random(seed)

    age = rng.normal(55, 15, n).clip(18, 90)
    sex = [py_rng.choice(["M", "F"]) for _ in range(n)]
    site = [py_rng.choice(STUDY_SITES) for _ in range(n)]
    race_ethnicity = [py_rng.choice(
        ["White", "Black or African American", "Hispanic or Latino", "Asian", "Other/Unknown"],
        # realistic-ish weighting
    ) for _ in range(n)]
    baseline_condition_score = rng.normal(5, 2, n).clip(0, 10)
    comorbidity_count = rng.poisson(1.6, n).clip(0, 8)
    insurance_type = [py_rng.choice(["Commercial", "Medicare", "Medicaid", "Uninsured"]) for _ in range(n)]

    recruitment_start = date(2025, 1, 6)
    recruitment_date = [recruitment_start + timedelta(days=int(d)) for d in rng.integers(0, 150, n)]
    # consent lag: a real process-mapping metric
    consent_lag_days = rng.integers(0, 10, n)
    consent_date = [rd + timedelta(days=int(cl)) for rd, cl in zip(recruitment_date, consent_lag_days)]
    baseline_lag_days = rng.integers(1, 21, n)
    baseline_date = [cd + timedelta(days=int(bl)) for cd, bl in zip(consent_date, baseline_lag_days)]

    # not every consented patient completes baseline (realistic attrition)
    completed_baseline = rng.random(n) > 0.06
    # not every baseline-complete patient completes follow-up
    completed_followup = completed_baseline & (rng.random(n) > 0.11)
    followup_lag_days = rng.integers(60, 180, n)
    followup_date = [
        bd + timedelta(days=int(fl)) if cf else None
        for bd, fl, cf in zip(baseline_date, followup_lag_days, completed_followup)
    ]

    df = pd.DataFrame({
        "patient_id": [f"RE-{i:04d}" for i in range(n)],
        "site": site,
        "age": np.round(age, 1),
        "sex": sex,
        "race_ethnicity": race_ethnicity,
        "insurance_type": insurance_type,
        "baseline_condition_score": np.round(baseline_condition_score, 2),
        "comorbidity_count": comorbidity_count,
        "recruitment_date": recruitment_date,
        "consent_date": consent_date,
        "baseline_date": [bd if cb else None for bd, cb in zip(baseline_date, completed_baseline)],
        "followup_date": followup_date,
        "completed_baseline": completed_baseline,
        "completed_followup": completed_followup,
    })
    # inject a modest amount of real missingness in a couple of fields,
    # for the codebook's missing-data reporting to have something to report
    missing_mask = rng.random(n) < 0.03
    df.loc[missing_mask, "comorbidity_count"] = None
    missing_mask2 = rng.random(n) < 0.02
    df.loc[missing_mask2, "insurance_type"] = None

    return df


if __name__ == "__main__":
    df = simulate()
    print(df.shape)
    print(df[["completed_baseline", "completed_followup"]].mean())
