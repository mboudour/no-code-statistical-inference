from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

PROJECT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_DIR / "app"


def app_test() -> AppTest:
    return AppTest.from_file(APP_DIR / "app.py").run(timeout=30)


def test_landing_page_loads() -> None:
    app = app_test()
    assert not app.exception
    assert any("No-Code Statistical Inference" in title.value for title in app.title)


def test_day_pages_load_and_show_ten_modules() -> None:
    pages = [
        "pages/1_Day_1_Data_Variation_and_Uncertainty.py",
        "pages/2_Day_2_Tests_Comparisons_and_Categorical_Inference.py",
        "pages/3_Day_3_Regression_Prediction_and_Reproducibility.py",
    ]
    for page in pages:
        app = app_test().switch_page(page).run(timeout=30)
        assert not app.exception
        # Every day has ten module expanders plus any nested interface expanders.
        assert len(app.expander) >= 10


def test_day3_worked_labs_expose_linear_logistic_and_validation_computations() -> None:
    """Opening worked data must activate the new slide-aligned computations."""
    app = app_test().switch_page("pages/3_Day_3_Regression_Prediction_and_Reproducibility.py").run(timeout=60)
    # Each module contributes a worked-data and a public-data checkbox in module order.
    for checkbox_index, expected_text in [
        (0, "Least-squares line, fitted values, residuals, and slope uncertainty"),
        (10, "Odds ratios compare odds rather than probabilities"),
        (18, "This uses the bundled Pima training file"),
    ]:
        app.checkbox[checkbox_index].set_value(True).run(timeout=90)
        assert not app.exception
        assert any(expected_text in item.value for item in [*app.caption, *app.markdown, *app.info])
    assert any("Final Day 3 model review" in item.value for item in app.header)


def test_guided_inference_starts_with_question_and_design_inputs() -> None:
    app = app_test().switch_page("pages/4_Guided_Inference.py").run(timeout=30)
    assert not app.exception
    assert any("1. State your research question" in widget.label for widget in app.text_area)
    assert any("2. Outcome structure" in widget.label for widget in app.selectbox)
    assert not any("What is the main purpose of your analysis?" in widget.label for widget in app.selectbox)


def test_guided_inference_dataset_lab_and_synthesis_load() -> None:
    for page in ["pages/4_Guided_Inference.py", "pages/5_Dataset_Laboratory.py", "pages/6_Day_Synthesis.py"]:
        app = app_test().switch_page(page).run(timeout=30)
        assert not app.exception
