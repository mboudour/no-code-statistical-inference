from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "app"))

from day3_analysis import (  # noqa: E402
    classification_metrics,
    external_logistic_validation,
    fit_day3_linear_model,
    fit_day3_logistic_model,
    holdout_validation,
)
from day3_dataset_options import DAY3_DATASET_OPTIONS, DAY3_MODULE_IDS, day3_dataset_options  # noqa: E402
from seminar_ui import public_dataset_options_for_module  # noqa: E402

DATA_DIR = PROJECT_DIR / "data" / "public"


def test_every_day3_module_has_explicit_curated_public_data_options() -> None:
    assert set(DAY3_DATASET_OPTIONS) == set(DAY3_MODULE_IDS)
    for module_id in DAY3_MODULE_IDS:
        assert day3_dataset_options(module_id)
        for option in day3_dataset_options(module_id) or ():
            assert (DATA_DIR / option["file"]).is_file(), (module_id, option["file"])
            assert option["method"]
            assert option["rationale"]
            assert option["caution"]


def test_day3_picker_uses_only_its_method_compatibility_registry() -> None:
    manifest = json.loads((PROJECT_DIR / "data" / "module_manifest.json").read_text())
    day3 = next(day for day in manifest["days"] if day["id"] == "day_3")
    for module in day3["modules"]:
        options = public_dataset_options_for_module(module, manifest)
        assert options is not None
        assert [item["file"] for item in options] == [item["file"] for item in DAY3_DATASET_OPTIONS[module["id"]]]
        assert all({"name", "method", "rationale", "caution"}.issubset(item) for item in options)


def test_linear_lab_returns_robust_uncertainty_and_case_diagnostics() -> None:
    data = pd.read_csv(DATA_DIR / "carseats.csv")
    result = fit_day3_linear_model(data, "Sales", ["Price", "Income"], ["ShelveLoc"])
    details = result["details"]
    assert {"coefficients", "robust_hc3_coefficients", "diagnostic_cases", "qq_points", "vif"}.issubset(details)
    assert "ShelveLoc=Good" in details["coefficients"].index
    assert {"Fitted", "Residual", "Standardized residual", "Leverage", "Cook's distance"}.issubset(details["diagnostic_cases"].columns)
    assert np.isfinite(result["_model"].rsquared)


def test_logistic_lab_returns_probability_calibration_and_discrimination() -> None:
    data = pd.read_csv(DATA_DIR / "pima_train.csv")
    result = fit_day3_logistic_model(data, "type", ["glu", "bmi", "age"])
    details = result["details"]
    assert 0 <= result["diagnostics"]["area_under_roc_curve"] <= 1
    assert result["diagnostics"]["brier_score"] >= 0
    assert {"Mean_predicted_probability", "Observed_event_rate", "Records"}.issubset(details["calibration"].columns)
    metrics = classification_metrics(result["_outcome"], result["_probabilities"], threshold=0.5)
    assert sum(metrics[key] for key in ["true_positive", "false_negative", "false_positive", "true_negative"]) == details["n"]


def test_internal_and_external_day3_validation_produce_heldout_metrics() -> None:
    pima_train = pd.read_csv(DATA_DIR / "pima_train.csv")
    pima_test = pd.read_csv(DATA_DIR / "pima_test.csv")
    internal = holdout_validation(pima_train, "type", ["glu", "bmi", "age"], "logistic", seed=2026)
    external = external_logistic_validation(pima_train, pima_test, "type", ["glu", "bmi", "age"])
    for result in [internal, external]:
        assert "Test AUC" in result["effect_size"]
        assert 0 <= result["diagnostics"]["test_auc"] <= 1
        assert "test_predictions" in result["details"]
