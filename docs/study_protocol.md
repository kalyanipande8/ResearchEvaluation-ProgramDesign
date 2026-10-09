# Study Protocol & Process Map — Observational Health Study (Template)

**Status: authored protocol/process-mapping template applied to a
synthetic 340-patient cohort, actually executed — not an IRB-submitted
protocol.**

## 1. Study workflow (process map)
`Recruited -> Consented -> Baseline complete -> Follow-up complete`, 4
enrolling sites. Real attrition and timing metrics for this workflow are
computed in `src/process_map.py` and reported in `results/process_map.json`
— not a static diagram disconnected from the data.

## 2. Data documentation (codebook)
Every variable in the cohort dataset is auto-documented by
`src/codebook_generator.py`: type, completeness, and (for continuous
variables) summary statistics or (for categorical variables) category
counts — generated directly from the dataframe, so it cannot silently drift
out of sync with the actual data the way a hand-maintained codebook can.

## 3. Evaluation framework
Program design is scored against **RE-AIM** (Glasgow, Vogt & Boles 1999) —
Reach, Effectiveness, Adoption, Implementation, Maintenance — with each
dimension computed from a concrete, defensible metric (not a subjective
1-5 rating):

| Dimension | Metric used |
|---|---|
| Reach | Representation across sex/race-ethnicity subgroups relative to a 10% floor |
| Effectiveness | Final analyzable (follow-up-complete) sample size vs. a 300-patient feasibility target |
| Adoption | Evenness of enrollment across the 4 sites (coefficient of variation) |
| Implementation | % of patients consented within 7 days of recruitment contact (protocol fidelity) |
| Maintenance | Overall follow-up completion rate |

## 4. Regulatory and research compliance elements
- De-identified patient IDs only; no PHI beyond the documented variable set.
- Codebook and process map together constitute the data-documentation
  package a real IRB/sponsor audit would request.
- Site-level attrition reporting (`attrition_by_site` in the process map)
  supports multi-site monitoring and compliance reporting.

## 5. Honest disclosure
This is demonstrated on a simulated cohort, not a real multi-site
observational study, and implemented in Python rather than R/SQL as the
resume's tool list names — the methodology (codebook generation, funnel/
attrition process mapping, RE-AIM scoring) is the same regardless of
language.
