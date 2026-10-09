import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_cohort import simulate, STUDY_SITES
from src.codebook_generator import generate_codebook, VARIABLE_DESCRIPTIONS
from src.process_map import build_process_map, STAGES
from src.evaluation_framework import score_re_aim, RE_AIM_DIMENSIONS


@pytest.fixture(scope="module")
def cohort():
    return simulate()


@pytest.fixture(scope="module")
def process_map(cohort):
    return build_process_map(cohort)


def test_cohort_has_340_patients(cohort):
    assert len(cohort) == 340


def test_four_sites_represented(cohort):
    assert set(cohort["site"].unique()) == set(STUDY_SITES)


def test_codebook_documents_every_column(cohort):
    codebook = generate_codebook(cohort)
    assert set(codebook["variable"]) == set(cohort.columns)
    assert len(codebook) == len(cohort.columns)


def test_codebook_reports_real_missingness(cohort):
    """Comorbidity count and insurance type have injected missingness --
    the codebook must actually report it, not show 0% across the board."""
    codebook = generate_codebook(cohort)
    comorbidity_row = codebook[codebook["variable"] == "comorbidity_count"].iloc[0]
    assert comorbidity_row["n_missing"] > 0


def test_process_map_funnel_is_monotonically_non_increasing(process_map):
    counts = [stage["n"] for stage in process_map["funnel"]]
    assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))


def test_process_map_covers_all_stages(process_map):
    stage_names = [s["stage"] for s in process_map["funnel"]]
    assert stage_names == STAGES


def test_process_map_timing_values_are_positive(process_map):
    for stage_timing in process_map["timing_days"].values():
        assert stage_timing["mean"] >= 0


def test_re_aim_covers_all_five_dimensions(cohort, process_map):
    result = score_re_aim(cohort, process_map)
    assert set(result["dimension_scores"].keys()) == set(RE_AIM_DIMENSIONS.keys())


def test_re_aim_scores_in_valid_range(cohort, process_map):
    result = score_re_aim(cohort, process_map)
    for score in result["dimension_scores"].values():
        assert 0.0 <= score <= 100.0
    assert 0.0 <= result["overall_re_aim_score"] <= 100.0
