from __future__ import annotations

from io import BytesIO
import sys
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "app"))

from seminar_ui import read_upload  # noqa: E402
from inference_core import (  # noqa: E402
    audit_dataset,
    build_report,
    categorical_association,
    linear_regression,
    logistic_regression,
    one_sample_mean,
    one_way_anova,
    paired_comparison,
    two_group_welch,
)

DATA_DIR = PROJECT_DIR / "data" / "public"


def test_dataset_audit_identifies_schema_and_missingness() -> None:
    data = pd.read_csv(DATA_DIR / "airquality.csv")
    audit = audit_dataset(data, "Air quality")
    assert audit["rows"] == len(data)
    assert "Ozone" in audit["numeric_columns"]
    assert audit["missing_cells"] > 0
    assert set(audit["variable_table"].columns) >= {"Variable", "Inferred type", "Missing %"}


def test_supported_analysis_families_return_standard_result_fields() -> None:
    results = [
        one_sample_mean(pd.read_csv(DATA_DIR / "women.csv"), "height"),
        two_group_welch(pd.read_csv(DATA_DIR / "plant_growth.csv"), "weight", "group", ["ctrl", "trt1"]),
        paired_comparison(pd.read_csv(DATA_DIR / "trees.csv"), "Girth", "Height"),
        one_way_anova(pd.read_csv(DATA_DIR / "insect_sprays.csv"), "count", "spray"),
        categorical_association(pd.read_csv(DATA_DIR / "ucb_admissions.csv"), "Gender", "Admit"),
        linear_regression(pd.read_csv(DATA_DIR / "cars.csv"), "dist", ["speed"]),
        logistic_regression(pd.read_csv(DATA_DIR / "default.csv"), "default", ["balance"]),
    ]
    required = {"question", "data_design", "method", "assumptions", "diagnostics", "estimate", "uncertainty", "effect_size", "test", "interpretation", "limitations", "next_step", "details"}
    for result in results:
        assert required.issubset(result)
        assert result["assumptions"]
        assert result["limitations"]


class NamedBuffer(BytesIO):
    def __init__(self, name: str, value: bytes) -> None:
        super().__init__(value)
        self.name = name


def test_csv_and_excel_upload_reader() -> None:
    source = pd.read_csv(DATA_DIR / "women.csv").drop(columns="rownames")
    csv_upload = NamedBuffer("women.csv", source.to_csv(index=False).encode("utf-8"))
    assert read_upload(csv_upload).equals(source)
    excel_buffer = BytesIO()
    source.to_excel(excel_buffer, index=False)
    excel_upload = NamedBuffer("women.xlsx", excel_buffer.getvalue())
    assert read_upload(excel_upload).equals(source)


def test_reproducibility_record_contains_required_sections() -> None:
    data = pd.read_csv(DATA_DIR / "women.csv")
    audit = audit_dataset(data, "Women")
    result = one_sample_mean(data, "height")
    report = build_report(result, audit, {"outcome": "height"})
    for section in ["Dataset audit", "Selections", "Question", "Assumptions", "Diagnostics", "Interpretation", "Limitations", "Software"]:
        assert section in report
