from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "app"))

from inference_core import (  # noqa: E402
    audit_dataset,
    build_report,
    categorical_association,
    descriptive_numeric_summary,
    linear_regression,
    logistic_regression,
    one_sample_mean,
    one_way_anova,
    paired_comparison,
    two_group_welch,
)
from validation import validate_inputs  # noqa: E402

DATA_DIR = PROJECT_DIR / "data" / "public"


def test_constant_numeric_data_has_descriptive_only_fallback() -> None:
    result = descriptive_numeric_summary(pd.DataFrame({"x": [4.0, 4.0, 4.0]}), "x")
    assert result["method"] == "Descriptive numeric summary only"
    assert "No standard error" in result["uncertainty"]
    assert result["details"]["unique_values"] == 1


def test_high_cardinality_association_is_warned_not_silently_treated_as_simple() -> None:
    data = pd.DataFrame({"item": [f"level_{index}" for index in range(21)], "group": ["a", "b", "c"] * 7})
    validation = validate_inputs("association", data, first="item", second="group")
    assert validation.warnings
    assert "more than 20" in validation.warnings[0]


def test_full_report_includes_contingency_and_expected_count_tables() -> None:
    data = pd.read_csv(DATA_DIR / "ucb_admissions.csv")
    result = categorical_association(data, "Gender", "Admit")
    report = build_report(result, audit_dataset(data, "UCB admissions"), {"first": "Gender", "second": "Admit"}, include_details=True)
    assert "## Detailed appendix" in report
    assert "### Table" in report
    assert "### Expected" in report
    assert "### Visualization record" in report


def test_known_reference_outputs_for_all_supported_inference_families() -> None:
    mean = one_sample_mean(pd.read_csv(DATA_DIR / "women.csv"), "height")
    assert mean["details"]["mean"] == pytest.approx(65.0)
    assert mean["details"]["low"] == pytest.approx(62.5234, abs=1e-4)

    welch = two_group_welch(pd.read_csv(DATA_DIR / "plant_growth.csv"), "weight", "group", ["ctrl", "trt1"])
    assert welch["details"]["difference"] == pytest.approx(-0.371, abs=1e-6)
    assert welch["details"]["p_value"] == pytest.approx(0.250383, abs=1e-6)

    paired = paired_comparison(pd.read_csv(DATA_DIR / "trees.csv"), "Girth", "Height")
    assert paired["details"]["mean"] == pytest.approx(62.751613, abs=1e-6)

    anova = one_way_anova(pd.read_csv(DATA_DIR / "insect_sprays.csv"), "count", "spray")
    assert anova["details"]["eta_squared"] == pytest.approx(0.724439, abs=1e-6)
    assert anova["details"]["p_value"] < 1e-15

    association = categorical_association(pd.read_csv(DATA_DIR / "ucb_admissions.csv"), "Gender", "Admit")
    assert association["details"]["chi2"] == pytest.approx(0.0)
    assert association["details"]["cramer_v"] == pytest.approx(0.0)

    linear = linear_regression(pd.read_csv(DATA_DIR / "cars.csv"), "dist", ["speed"])
    assert linear["details"]["r_squared"] == pytest.approx(0.651079, abs=1e-6)
    assert linear["details"]["coefficients"].loc["speed", "Estimate"] == pytest.approx(3.9324, abs=1e-4)

    logistic = logistic_regression(pd.read_csv(DATA_DIR / "default.csv"), "default", ["balance"])
    assert logistic["details"]["n"] == 10000
    assert logistic["details"]["coefficients"].loc["balance", "Odds ratio"] == pytest.approx(1.0055, abs=1e-4)
