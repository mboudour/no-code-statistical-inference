from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "app"))

from inference_core import (  # noqa: E402
    categorical_association,
    independent_group_power,
    logistic_regression,
    method_compatibility,
    one_sample_mean,
    paired_comparison,
)
from validation import InputValidationError, validate_inputs  # noqa: E402


def test_design_first_engine_derives_compatible_pathways() -> None:
    recommendations = method_compatibility(
        "Continuous / numeric", "Two groups", "Independent observational units", "Comparison"
    )
    statuses = {item["key"]: item["status"] for item in recommendations}
    assert statuses["two_independent"] == "Compatible"
    assert statuses["paired"] == "Not compatible"
    assert statuses["logistic_regression"] == "Not compatible"


def test_mean_and_paired_workflows_reject_insufficient_or_degenerate_data() -> None:
    with pytest.raises(InputValidationError, match="at least 2"):
        one_sample_mean(pd.DataFrame({"y": [1.0]}), "y")
    with pytest.raises(InputValidationError, match="zero observed variation"):
        one_sample_mean(pd.DataFrame({"y": [1.0, 1.0]}), "y")
    with pytest.raises(InputValidationError, match="complete pairs"):
        paired_comparison(pd.DataFrame({"before": [1.0], "after": [2.0]}), "before", "after")
    with pytest.raises(InputValidationError, match="identical"):
        paired_comparison(pd.DataFrame({"before": [1.0, 2.0, 3.0], "after": [2.0, 3.0, 4.0]}), "before", "after")


def test_group_and_anova_validators_reject_invalid_level_structure() -> None:
    two_group_data = pd.DataFrame({"outcome": [1.0, 2.0, 3.0, 4.0], "group": ["a", "a", "b", "b"]})
    with pytest.raises(InputValidationError, match="exactly two"):
        validate_inputs("two_independent", two_group_data, outcome="outcome", group="group", levels=["a"])
    anova_data = pd.DataFrame({"outcome": [1.0, 2.0, 3.0, 4.0, 5.0], "group": ["a", "b", "b", "c", "c"]})
    with pytest.raises(InputValidationError, match="at least two"):
        validate_inputs("anova", anova_data, outcome="outcome", group="group")


def test_regression_validators_reject_underdetermined_constant_and_rank_deficient_inputs() -> None:
    data = pd.DataFrame({"y": [1.0, 2.0, 3.0], "x1": [1.0, 2.0, 3.0], "x2": [1.0, 2.0, 3.0]})
    with pytest.raises(InputValidationError, match="more complete cases"):
        validate_inputs("linear_regression", data, outcome="y", predictors=["x1", "x2"])
    constant = pd.DataFrame({"y": [1.0, 2.0, 3.0, 4.0], "x": [1.0, 1.0, 1.0, 1.0]})
    with pytest.raises(InputValidationError, match="Constant predictor"):
        validate_inputs("linear_regression", constant, outcome="y", predictors=["x"])
    rank_deficient = pd.DataFrame({"y": [1.0, 2.0, 3.0, 4.0, 5.0], "x1": [1, 2, 3, 4, 5], "x2": [1, 2, 3, 4, 5]})
    with pytest.raises(InputValidationError, match="rank deficient"):
        validate_inputs("linear_regression", rank_deficient, outcome="y", predictors=["x1", "x2"])


def test_categorical_missing_values_default_to_complete_case_with_explicit_opt_in() -> None:
    missing_data = pd.DataFrame({"first": ["a", "b", None, None], "second": ["yes", "no", "yes", "no"]})
    default_result = categorical_association(missing_data, "first", "second")
    assert "Missing" not in default_result["details"]["table"].index
    assert default_result["details"]["missing_data"]["rule"] == "complete_case"
    assert default_result["details"]["missing_data"]["rows_excluded"] == 2
    substantive_result = categorical_association(missing_data, "first", "second", missing_rule="substantive_missing_category")
    assert "Missing" in substantive_result["details"]["table"].index
    assert substantive_result["details"]["missing_data"]["rule"] == "substantive_missing_category"
    assert substantive_result["details"]["missing_data"]["rows_excluded"] == 0
    sparse = pd.DataFrame({"first": ["a", "a", "b", "b"], "second": ["yes", "no", "yes", "no"]})
    sparse_result = categorical_association(sparse, "first", "second")
    assert "Fisher exact" in sparse_result["test"]
    assert sparse_result["diagnostics"]["fisher_exact"] is not None


def test_prospective_power_rejects_zero_effect_and_returns_targeted_plan() -> None:
    with pytest.raises(InputValidationError, match="positive"):
        independent_group_power(0.0, 20)
    plan = independent_group_power(0.5, 20, target_power=0.90)
    assert plan["planning_effect_size"] == 0.5
    assert plan["target_power"] == 0.90
    assert plan["n_per_group_for_target_power"] > 20


def test_logistic_validator_catches_sparse_events_and_separation() -> None:
    sparse_events = pd.DataFrame({"outcome": [0] * 9 + [1], "x": list(range(10))})
    with pytest.raises(InputValidationError, match="smaller outcome class"):
        validate_inputs("logistic_regression", sparse_events, outcome="outcome", predictors=["x"])
    separated = pd.DataFrame({"outcome": [0] * 10 + [1] * 10, "x": [0.0] * 10 + [1.0] * 10})
    with pytest.raises(InputValidationError, match="Perfect separation|did not converge|singular"):
        logistic_regression(separated, "outcome", ["x"])
