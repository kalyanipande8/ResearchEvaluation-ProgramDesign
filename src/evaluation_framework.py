"""Program/study evaluation scored against RE-AIM (Glasgow, Vogt & Boles
1999, *American Journal of Public Health*) -- Reach, Effectiveness,
Adoption, Implementation, Maintenance -- the standard public-health/
implementation-science evaluation framework, applied here with concrete,
computed metrics rather than a qualitative checklist.
"""
from __future__ import annotations

import pandas as pd

RE_AIM_DIMENSIONS = {
    "Reach": "What proportion of the target population was recruited and represented across key subgroups?",
    "Effectiveness": "Did the study design support a valid effect estimate (sample size, retention)?",
    "Adoption": "Did enrollment occur consistently across all intended sites?",
    "Implementation": "Was the study protocol delivered with acceptable fidelity (timing, consent lag)?",
    "Maintenance": "Did patients remain engaged through the full follow-up period?",
}


def score_re_aim(df: pd.DataFrame, process_map: dict) -> dict:
    n = len(df)

    # Reach: representation across sex and race/ethnicity -- flags if any
    # subgroup is severely underrepresented relative to a 10% floor
    sex_counts = df["sex"].value_counts(normalize=True)
    race_counts = df["race_ethnicity"].value_counts(normalize=True)
    reach_score = round(100 * min(1.0, (sex_counts.min() / 0.10)), 1) if len(sex_counts) else 0.0
    reach_underrepresented_groups = race_counts[race_counts < 0.05].index.tolist()

    # Effectiveness: proxy via final analyzable sample size against a
    # pre-specified target of 300 (a common RWE feasibility threshold)
    n_followup = int(df["completed_followup"].sum())
    effectiveness_score = round(100 * min(1.0, n_followup / 300), 1)

    # Adoption: coefficient of variation in enrollment across sites (lower = more even adoption)
    site_counts = df["site"].value_counts()
    cv = float(site_counts.std() / site_counts.mean())
    adoption_score = round(100 * max(0.0, 1 - cv), 1)

    # Implementation: consent-lag fidelity -- % of patients consented within 7 days
    consent_lag = (pd.to_datetime(df["consent_date"]) - pd.to_datetime(df["recruitment_date"])).dt.days
    implementation_score = round(100 * float((consent_lag <= 7).mean()), 1)

    # Maintenance: overall follow-up completion rate (from the process map)
    maintenance_score = process_map["overall_followup_completion_rate_pct"]

    scores = {
        "Reach": reach_score,
        "Effectiveness": effectiveness_score,
        "Adoption": adoption_score,
        "Implementation": implementation_score,
        "Maintenance": maintenance_score,
    }

    return {
        "dimension_scores": scores,
        "overall_re_aim_score": round(sum(scores.values()) / len(scores), 1),
        "reach_underrepresented_groups": reach_underrepresented_groups,
        "dimension_descriptions": RE_AIM_DIMENSIONS,
    }


if __name__ == "__main__":
    from .simulate_cohort import simulate
    from .process_map import build_process_map

    df = simulate()
    pm = build_process_map(df)
    import json
    print(json.dumps(score_re_aim(df, pm), indent=2))
