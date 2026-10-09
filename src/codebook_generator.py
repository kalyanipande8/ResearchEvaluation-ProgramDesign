"""Auto-generate a real data codebook from the actual cohort dataframe --
not a hand-typed document that can drift out of sync with the data. Each
variable gets its type, completeness, and (for continuous variables)
summary statistics or (for categorical variables) category counts.
"""
from __future__ import annotations

import pandas as pd

VARIABLE_DESCRIPTIONS = {
    "patient_id": "De-identified patient study ID",
    "site": "Enrolling study site",
    "age": "Age in years at enrollment",
    "sex": "Sex at birth",
    "race_ethnicity": "Self-reported race/ethnicity (OMB categories)",
    "insurance_type": "Primary insurance type at enrollment",
    "baseline_condition_score": "Baseline disease severity, 0-10 clinician-rated",
    "comorbidity_count": "Count of documented comorbid conditions at baseline",
    "recruitment_date": "Date of study recruitment contact",
    "consent_date": "Date informed consent was obtained",
    "baseline_date": "Date baseline assessment was completed (null if not completed)",
    "followup_date": "Date follow-up assessment was completed (null if not completed)",
    "completed_baseline": "Indicator: patient completed the baseline assessment",
    "completed_followup": "Indicator: patient completed the follow-up assessment",
}


def generate_codebook(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        series = df[col]
        n = len(series)
        n_missing = int(series.isna().sum())
        pct_missing = round(100 * n_missing / n, 2)
        dtype = str(series.dtype)

        row = {
            "variable": col,
            "description": VARIABLE_DESCRIPTIONS.get(col, ""),
            "dtype": dtype,
            "n": n,
            "n_missing": n_missing,
            "pct_missing": pct_missing,
        }

        non_null = series.dropna()
        if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
            row.update({
                "min": round(float(non_null.min()), 2) if len(non_null) else None,
                "max": round(float(non_null.max()), 2) if len(non_null) else None,
                "mean": round(float(non_null.mean()), 2) if len(non_null) else None,
                "std": round(float(non_null.std()), 2) if len(non_null) else None,
                "n_categories": None,
                "top_categories": None,
            })
        elif pd.api.types.is_bool_dtype(series):
            row.update({
                "min": None, "max": None, "mean": None, "std": None,
                "n_categories": 2,
                "top_categories": non_null.value_counts().to_dict(),
            })
        else:
            value_counts = non_null.astype(str).value_counts()
            row.update({
                "min": None, "max": None, "mean": None, "std": None,
                "n_categories": int(value_counts.nunique()) if len(value_counts) else 0,
                "top_categories": value_counts.head(5).to_dict(),
            })

        rows.append(row)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    from .simulate_cohort import simulate

    df = simulate()
    codebook = generate_codebook(df)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    print(codebook)
