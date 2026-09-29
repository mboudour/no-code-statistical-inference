from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "app"))

from day2_dataset_options import (  # noqa: E402
    DAY2_DATASET_OPTIONS,
    DAY2_MODULE_IDS,
    day2_dataset_options,
    day2_preparation_guidance,
)
from seminar_ui import public_dataset_options_for_module  # noqa: E402


PUBLIC_DATA_DIR = PROJECT_DIR / "data" / "public"


def test_every_day2_module_has_an_explicit_public_data_policy() -> None:
    assert set(DAY2_DATASET_OPTIONS) == set(DAY2_MODULE_IDS)
    for module_id in DAY2_MODULE_IDS:
        assert day2_dataset_options(module_id) is not None


def test_curated_options_reference_existing_public_files_and_explain_fit() -> None:
    for module_id, options in DAY2_DATASET_OPTIONS.items():
        for option in options:
            assert (PUBLIC_DATA_DIR / option["file"]).is_file(), (module_id, option["file"])
            assert option["method"]
            assert option["rationale"]
            assert option["caution"]


def test_only_paired_module_has_no_ready_to_run_public_file() -> None:
    assert DAY2_DATASET_OPTIONS["d2m04"] == ()
    guidance = day2_preparation_guidance("d2m04")
    assert guidance is not None
    assert "wide CSV" in guidance


def test_weighted_frequency_files_are_not_offered_to_unweighted_categorical_workflows() -> None:
    categorical_modules = ("d2m07", "d2m08", "d2m09", "d2m10")
    for module_id in categorical_modules:
        files = {option["file"] for option in DAY2_DATASET_OPTIONS[module_id]}
        assert "titanic.csv" not in files
        assert "ucb_admissions.csv" not in files


def test_non_day2_module_has_no_day2_registry_entry() -> None:
    assert day2_dataset_options("d1m01") is None
    assert day2_dataset_options("d3m01") is None


def test_day2_picker_uses_the_curated_registry_for_all_ten_modules() -> None:
    manifest = json.loads((PROJECT_DIR / "data" / "module_manifest.json").read_text())
    day2 = next(day for day in manifest["days"] if day["id"] == "day_2")
    for module in day2["modules"]:
        options = public_dataset_options_for_module(module, manifest)
        assert options is not None
        assert [option["file"] for option in options] == [
            option["file"] for option in DAY2_DATASET_OPTIONS[module["id"]]
        ]
        for option in options:
            assert option["name"]
            assert option["method"]
            assert option["rationale"]
            assert option["caution"]
