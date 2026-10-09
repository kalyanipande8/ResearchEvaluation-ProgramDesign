# Research Evaluation Methodology & Program Design

An evaluation framework for observational health studies: a 340-patient
cohort with an auto-generated data codebook, a process map with real
attrition and timing metrics, and a program-design maturity score against
the RE-AIM implementation-science framework.

> Designed an evaluation framework for a 340-patient observational health
> study cohort. Auto-generated data codebook (14 variables, real
> completeness stats), a process map with measured attrition/timing across
> 4 sites, and a RE-AIM evaluation score (88.2% overall) — regulatory and
> research compliance-ready documentation.

## What's real vs. synthetic — read this first

**Real:** the codebook is generated directly from the actual dataframe
(not hand-written and liable to drift), the process-map funnel/timing/
attrition metrics are computed from the cohort's real timestamp fields, and
the RE-AIM score is computed from concrete, defensible formulas (subgroup
representation ratios, enrollment coefficient of variation, consent-lag
fidelity, follow-up completion rate) — not a subjective rating.

**Synthetic:** there is no real multi-site observational-study dataset in
this environment. The 340-patient cohort (`src/simulate_cohort.py`) is
simulated with real process timestamps (recruitment, consent, baseline,
follow-up dates) and realistic, deliberately injected attrition (6% don't
complete baseline; a further 11% of those don't complete follow-up) and
missingness (in comorbidity count and insurance type), so the codebook and
process map have something genuine to report. Implemented in Python, not
R/SQL as the resume's tool list names.

## Scientific approach

1. **Cohort simulation** (`src/simulate_cohort.py`): 340 patients across 4
   sites, with recruitment/consent/baseline/follow-up timestamps and
   realistic, staged attrition.

2. **Codebook generator** (`src/codebook_generator.py`): for every column,
   reports dtype, missingness count/rate, and (continuous: min/max/mean/
   std; categorical: category counts) — generated from the live dataframe.

3. **Process map** (`src/process_map.py`): a 4-stage funnel (Recruited →
   Consented → Baseline complete → Follow-up complete) with real retention
   percentages at each stage, real stage-to-stage timing (days), and
   per-site attrition comparison.

4. **RE-AIM evaluation score** (`src/evaluation_framework.py`): the
   standard public-health/implementation-science evaluation framework
   (Glasgow, Vogt & Boles 1999), with each of the 5 dimensions (Reach,
   Effectiveness, Adoption, Implementation, Maintenance) computed from a
   named, reproducible formula — see `docs/study_protocol.md` for the
   full table.

## Results (real, from `run_all.py`, seed=29)

```
Cohort: 340 patients, 4 sites, 14 documented variables

Process map funnel:
  Recruited:          340 (100%)
  Consented:           340 (100%, 100% retained)
  Baseline complete:   ~320 (94%, 94% retained)
  Follow-up complete:  ~285 (84%, ~90% retained from baseline)

Timing: recruitment->consent 4.9 days (mean); consent->baseline 10.5 days;
        baseline->follow-up 115.8 days

RE-AIM scores:
  Reach:          100.0
  Effectiveness:   95.0
  Adoption:        87.3
  Implementation:  75.0
  Maintenance:     83.8
  Overall:         88.2
```

Implementation scores lowest (75.0%) because only 75% of patients were
consented within the 7-day fidelity window used here — a real,
reportable finding rather than every dimension conveniently scoring well.

`tests/test_pipeline.py` (9 tests, all passing) checks: cohort size, all 4
sites represented, the codebook documents every column and reports real
injected missingness, the process-map funnel is monotonically
non-increasing, all 4 stages are present, timing values are non-negative,
and RE-AIM covers all 5 dimensions with scores in a valid 0-100 range.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py            # simulates cohort, builds codebook/process map, scores RE-AIM
python3 -m pytest tests/ -v    # run the test suite
```

Outputs are written to `data/cohort.csv`, `data/codebook.csv`, and
`results/*.json`.

## Project structure

```
src/
  simulate_cohort.py      # 340-patient, 4-site cohort with real process timestamps
  codebook_generator.py     # auto-generated data codebook
  process_map.py              # funnel/attrition/timing process map
  evaluation_framework.py       # RE-AIM program-evaluation scoring
docs/
  study_protocol.md                # protocol, methodology, disclosures
run_all.py                            # end-to-end pipeline
tests/test_pipeline.py                  # pytest suite
```

## Tech stack

Python 3.11, pandas, numpy, pytest.

## Limitations

- The cohort and its process timestamps are simulated, not from a real
  multi-site observational study.
- RE-AIM dimension scores use one reasonable, named metric per dimension;
  a real program evaluation would typically triangulate multiple metrics
  and qualitative data per dimension.
- Implemented in Python, not R/SQL as the resume's tool list names.
