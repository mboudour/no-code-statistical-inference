from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "app"))

from day3_computations import (  # noqa: E402
    adjustment_comparison,
    binary_outcome_columns,
    bootstrap_optimism_logistic,
    categorical_predictor_regression,
    cross_validate_day3_model,
    nested_specification_comparison,
    refit_after_case_exclusion,
)

DATA_DIR = PROJECT_DIR / "data" / "public"


def test_categorical_coding_reports_reference_means_and_contrasts() -> None:
    data = pd.read_csv(DATA_DIR / "carseats.csv")
    result = categorical_predictor_regression(data, "Sales", "ShelveLoc")
    assert result["details"]["reference_group"] == "Bad"
    assert len(result["details"]["group_means"]) == 3
    assert not result["details"]["contrasts"].empty


def test_adjustment_and_nested_specification_return_explicit_comparisons() -> None:
    credit = pd.read_csv(DATA_DIR / "credit.csv")
    adjustment = adjustment_comparison(credit, "Balance", "Income", ["Limit", "Rating"])
    assert adjustment["comparison"]["Model"].tolist() == ["Unadjusted", "Adjusted"]

    cars = pd.read_csv(DATA_DIR / "cars.csv")
    specification = nested_specification_comparison(cars, "dist", ["speed"], quadratic_predictor="speed")
    assert specification["nested_test"]["Numerator df"] == 1
    assert set(specification["comparison"]["Model"]) == {"Baseline", "Extended"}


def test_binary_outcomes_cross_validation_bootstrap_and_sensitivity_refit() -> None:
    default = pd.read_csv(DATA_DIR / "default.csv")
    assert "default" in binary_outcome_columns(default)

    pima = pd.read_csv(DATA_DIR / "pima_train.csv")
    cross_validation = cross_validate_day3_model(pima, "type", ["glu", "bmi", "age"], "logistic", folds=3)
    assert 0 <= cross_validation["summary"]["Out-of-fold AUC"] <= 1
    assert len(cross_validation["fold_metrics"]) == 3

    bootstrap = bootstrap_optimism_logistic(pima, "type", ["glu", "bmi"], repetitions=20)
    assert bootstrap["repetitions_completed"] >= 10
    assert 0 <= bootstrap["corrected"]["AUC"] <= 1

    schools = pd.read_csv(DATA_DIR / "ca_schools.csv")
    refit = refit_after_case_exclusion(schools, "read", ["income", "expenditure"], [], ["0"])
    assert refit["details"]["n"] == len(schools) - 1
